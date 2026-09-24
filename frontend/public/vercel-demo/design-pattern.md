# Design Patterns Analysis

## Overview

This Vercel Commerce storefront demonstrates a focused set of recurring design patterns that address the specific requirements of a Shopify-backed e-commerce frontend: optimistic cart updates, server–client data boundaries, external API abstraction, URL-driven state, and cache management. The patterns are shaped by the Next.js App Router architecture and React's concurrent features.

---

## Creational Patterns

### Context Provider with Promise Injection

**Location:** `components/cart/cart-context.tsx`

**Problem Addressed:**
The cart data originates from a server component (via `getCart()`) but must be consumed by deeply nested client components. Passing a resolved value through Context would bypass Suspense boundaries.

**Implementation:**
The `CartProvider` accepts a `Promise<Cart | undefined>` rather than a resolved cart value. Client components access the cart through the `useCart` hook, which uses React's `use()` hook to consume the promise within the Suspense boundary established by the framework.

```tsx
// Provider accepts promise, not resolved value
export function CartProvider({ children, cartPromise }: {
  children: React.ReactNode;
  cartPromise: Promise<Cart | undefined>;
}) {
  return (
    <CartContext.Provider value={{ cartPromise }}>
      {children}
    </CartContext.Provider>
  );
}

// Consumer uses use() to await within Suspense
export function useCart() {
  const initialCart = use(context.cartPromise);
  const [optimisticCart, updateOptimisticCart] = useOptimistic(initialCart, cartReducer);
  // ...
}
```

**Role in System:**
Enables the server-rendered cart data to flow into client components while maintaining React's streaming and Suspense behavior. The pattern is essential for the optimistic cart update system.

### ExtractVariables Type Factory

**Location:** `lib/shopify/index.ts` (lines 67–69)

**Problem Addressed:**
GraphQL operation types each define their own `variables` shape. Creating a single fetch function that accepts any operation requires extracting the correct variable type.

**Implementation:**

```tsx
type ExtractVariables<T> = T extends { variables: object } ? T["variables"] : never;

export async function shopifyFetch<T>({
  query,
  variables,
}: {
  query: string;
  variables?: ExtractVariables<T>;
}): Promise<{ status: number; body: T }>
```

**Role in System:**
Provides compile-time type safety for GraphQL variables across all Shopify operations (cart, products, collections, pages) while allowing a single implementation of the fetch logic.

---

## Structural Patterns

### Data Access Layer / Repository Pattern

**Location:** `lib/shopify/index.ts`

**Problem Addressed:**
The application must interact with Shopify's Storefront API while hiding GraphQL transport details, response shape differences, and caching concerns from the rest of the application.

**Implementation:**
The module provides a unified API surface through functions like `getProduct()`, `getCart()`, `addToCart()`, and `getCollections()`. All Shopify interactions flow through:

1. **`shopifyFetch<T>()`** — Centralized fetch function handling authentication, error normalization, and response parsing.
2. **Reshape functions** — Transform Shopify's response format to domain types.
3. **Cache directives** — Apply Next.js cache tags and lifetimes.

```tsx
export async function getProduct(handle: string): Promise<Product | undefined> {
  "use cache";
  cacheTag(TAGS.products);
  cacheLife("days");

  const res = await shopifyFetch<ShopifyProductOperation>({
    query: getProductQuery,
    variables: { handle },
  });
  return reshapeProduct(res.body.data.product, false);
}
```

**Role in System:**
Abstracts all external API communication behind domain-specific functions. Components never call `fetch` directly or construct GraphQL queries; they call `getProduct()` and receive normalized domain objects.

### Resource Reshaping / Data Mapping

**Location:** `lib/shopify/index.ts` (reshape functions)

**Problem Addressed:**
Shopify's GraphQL API returns paginated connections (edges/nodes) and uses specific field names that differ from the application's domain model.

**Implementation:**

```tsx
// Strip pagination wrapper
const removeEdgesAndNodes = <T>(array: Connection<T>): T[] => {
  return array.edges.map((edge) => edge?.node);
};

// Transform Shopify cart to domain cart
const reshapeCart = (cart: ShopifyCart): Cart => {
  if (!cart.cost?.totalTaxAmount) {
    cart.cost.totalTaxAmount = { amount: "0.0", currencyCode: cart.cost.totalAmount.currencyCode };
  }
  return { ...cart, lines: removeEdgesAndNodes(cart.lines) };
};
```

Additional reshape functions exist for `Collection`, `Product`, and `Image` types. Each handles:
- Null/missing field defaults
- GraphQL connection unwrapping
- Domain-specific field additions (e.g., `path` on `Collection`)

**Role in System:**
Ensures components receive consistent, application-specific types regardless of Shopify's API response format. Enables future backend changes without modifying component code.

### Wrapper Components (UI Decoration)

**Location:** `components/price.tsx`, `components/prose.tsx`

**Problem Addressed:**
Common UI patterns (price formatting, HTML prose rendering) need consistent styling without duplicating class names throughout the codebase.

**Implementation:**

```tsx
export default function Price({
  amount,
  currencyCode,
  className = "",
}: {
  amount: string | number;
  currencyCode: string;
  className?: string;
}) {
  return (
    <span suppressHydrationWarning className={clsx(defaultClasses, className)}>
      {new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: currencyCode,
      }).format(Number(amount) / 100)}
    </span>
  );
}
```

**Role in System:**
Encapsulates styling logic and formatting behavior. Consumers pass data and optional class overrides; the component handles consistent presentation.

---

## Behavioral Patterns

### Optimistic Updates with Dual-Write

**Location:** `components/cart/cart-context.tsx`, `components/cart/add-to-cart.tsx`, `components/cart/edit-item-quantity-button.tsx`, `components/cart/delete-item-button.tsx`

**Problem Addressed:**
Cart operations must feel instant to the user, but Shopify API calls have network latency. The UI should reflect the intended change immediately while the server action persists the change asynchronously.

**Implementation:**
The pattern combines React's `useOptimistic` hook with Next.js Server Actions:

```tsx
// In useCart hook - optimistic state management
export function useCart() {
  const [optimisticCart, updateOptimisticCart] = useOptimistic(initialCart, cartReducer);
  // ...
}

// In AddToCart - dual write: optimistic then server
export function AddToCart({ product }: { product: Product }) {
  return (
    <form action={async () => {
      addCartItem(finalVariant, product);  // Optimistic update
      addItemAction();                      // Server action
    }}>
      <SubmitButton ... />
    </form>
  );
}
```

The `cartReducer` handles optimistic state transitions for `ADD_ITEM`, `UPDATE_ITEM` (plus/minus/delete). Server actions perform the actual Shopify API calls and trigger cache tag invalidation.

**Role in System:**
Provides responsive cart interactions without loading states for individual add/remove/quantity operations. The pattern is central to the user experience of the shopping cart.

### Server Actions (Command Pattern)

**Location:** `components/cart/actions.ts`

**Problem Addressed:**
Client components must invoke server-side logic (Shopify API calls) without exposing credentials or API details to the browser.

**Implementation:**

```tsx
"use server";

export async function addItem(prevState: any, selectedVariantId: string | undefined) {
  if (!selectedVariantId) return "Error adding item to cart";
  try {
    await addToCart([{ merchandiseId: selectedVariantId, quantity: 1 }]);
    updateTag(TAGS.cart);
  } catch (e) {
    return "Error adding item to cart";
  }
}
```

All cart mutations (`addItem`, `removeItem`, `updateItemQuantity`) and cart management (`redirectToCheckout`, `createCartAndSetCookie`) are exposed as Server Actions. They encapsulate:
- Shopify API calls
- Cookie access
- Cache tag invalidation
- Error handling

**Role in System:**
Provides a secure server-side execution environment for operations that require credentials or side effects. The pattern keeps sensitive data on the server while enabling form-based mutations from client components.

### URL-Driven State (Query Parameters as State)

**Location:** `components/product/variant-selector.tsx`, `components/product/gallery.tsx`

**Problem Addressed:**
Product variant selection and gallery image selection must be shareable via URL, survive navigation, and work without JavaScript for initial render.

**Implementation:**

```tsx
export function VariantSelector({ options, variants }: Props) {
  const searchParams = useSearchParams();

  const updateOption = (name: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set(name, value);
    router.replace(`?${params.toString()}`, { scroll: false });
  };

  // Variant selection derived from URL
  const variant = variants.find((variant: ProductVariant) =>
    variant.selectedOptions.every(
      (option) => option.value === searchParams.get(option.name.toLowerCase())
    )
  );
}
```

The variant selector derives the selected variant from `searchParams`, writes selection changes back to the URL via `router.replace()`, and filters available options based on variant availability. The gallery uses the same pattern for image selection.

**Role in System:**
Enables deep linking to specific product configurations. Users can share product URLs that restore their exact variant and gallery selections.

### Webhook-Triggered Cache Invalidation (Event-Driven Regeneration)

**Location:** `lib/shopify/index.ts` (revalidate function), `app/api/revalidate/route.ts`

**Problem Addressed:**
Product and collection pages are cached aggressively (`"days"` lifetime) but must reflect Shopify content changes immediately when the merchant updates inventory or content.

**Implementation:**

```tsx
export async function revalidate(req: NextRequest): Promise<NextResponse> {
  const topic = (await headers()).get("x-shopify-topic") || "unknown";
  const secret = req.nextUrl.searchParams.get("secret");

  if (secret !== process.env.SHOPIFY_REVALIDATION_SECRET) {
    return NextResponse.json({ status: 401 });
  }

  if (isCollectionUpdate) revalidateTag(TAGS.collections, "seconds");
  if (isProductUpdate) revalidateTag(TAGS.products, "seconds");

  return NextResponse.json({ status: 200 });
}
```

Shopify sends webhook POST requests when products or collections change. The endpoint validates the secret, determines the affected cache tags, and triggers Next.js cache revalidation. On-demand regeneration occurs for affected pages while other cached pages remain unchanged.

**Role in System:**
Maintains cache freshness without full-cache invalidation. Enables aggressive caching for performance while ensuring content accuracy after merchant updates.

---

## Data Access Patterns

### Type Guards (Runtime Type Narrowing)

**Location:** `lib/type-guards.ts`

**Problem Addressed:**
GraphQL responses may contain errors alongside data. Error handling must distinguish between different error shapes at runtime.

**Implementation:**

```tsx
export const isObject = (object: unknown): object is Record<string, unknown> => {
  return typeof object === "object" && object !== null && !Array.isArray(object);
};

export const isShopifyError = (error: unknown): error is ShopifyErrorLike => {
  if (!isObject(error)) return false;
  if (error instanceof Error) return true;
  return findError(error);
};
```

Used in `shopifyFetch()` to detect Shopify-specific error responses and transform them into structured error objects with status codes and messages.

**Role in System:**
Enables type-safe error handling downstream. Functions can check `isShopifyError(e)` to determine if an error has structured fields versus being a generic exception.

---

## Presentation Patterns

### Container/Presentational Component Separation

**Locations:** Multiple components throughout `components/`

**Problem Addressed:**
Server components that fetch data should not contain rendering logic, while client components managing interactivity should not duplicate data-fetching concerns.

**Implementation:**

Server components (`ThreeItemGrid`, `Navbar`, `ProductDescription`) handle data fetching:

```tsx
export async function ThreeItemGrid() {
  const homepageItems = await getCollectionProducts({ collection: "hidden-homepage-featured-items" });
  return (
    <section>
      {homepageItems.map(item => (
        <ThreeItemGridItem key={item.handle} item={item} />
      ))}
    </section>
  );
}
```

Client components (`Gallery`, `VariantSelector`, `CartModal`) handle user interaction:

```tsx
"use client"
export function Gallery({ images }) {
  const router = useRouter();
  const updateImage = (index: string) => { /* ... */ };
  return <div>/* interactive gallery */</div>;
}
```

**Role in System:**
Optimizes bundle size by limiting client JavaScript to interactive components. Server components leverage React Server Components for zero-bundle-size data fetching.

### Dynamic Component Tagging

**Location:** `components/layout/search/filter/item.tsx`

**Problem Addressed:**
The same filter component must render as a link when inactive but as plain text when active, without prop-drilling or additional state management.

**Implementation:**

```tsx
function SortFilterItem({ item }: { item: SortFilterItem }) {
  const active = searchParams.get("sort") === item.slug;
  const DynamicTag = active ? "p" : Link;

  return (
    <DynamicTag href={href} className={...}>
      {item.title}
    </DynamicTag>
  );
}
```

The component conditionally assigns either a `<Link>` or `<p>` element to `DynamicTag` based on the active state.

**Role in System:**
Eliminates prop-drilling for styling differences between active/inactive states. Maintains accessibility (links for navigation, text for current selection) without conditional rendering of entire subtrees.

### Suspense Boundary Pattern

**Location:** Throughout `app/` and `components/`

**Problem Addressed:**
Async server components and data fetching must stream content progressively without blocking the entire page.

**Implementation:**

```tsx
export default async function RootLayout({ children }) {
  const cart = getCart(); // Promise, not awaited
  return (
    <CartProvider cartPromise={cart}>
      <Navbar />
      <Suspense fallback={<SearchSkeleton />}>
        <Search />
      </Suspense>
    </CartProvider>
  );
}
```

Data-fetching components are wrapped in Suspense boundaries with appropriate loading fallbacks. The Navbar's `Search` component has a skeleton fallback; the `ProductDescription` has a `null` fallback since product data is already available.

**Role in System:**
Enables progressive loading and streaming. Above-the-fold content renders while below-the-fold async components fetch data in parallel.

---

## Configuration Patterns

### Environment Validation

**Location:** `lib/utils.ts`

**Problem Addressed:**
Missing required environment variables should fail fast at startup rather than causing cryptic runtime errors.

**Implementation:**

```tsx
export const validateEnvironmentVariables = () => {
  const requiredEnvironmentVariables = [
    "SHOPIFY_STORE_DOMAIN",
    "SHOPIFY_STOREFRONT_ACCESS_TOKEN",
  ];
  const missingEnvironmentVariables = requiredEnvironmentVariables
    .filter(envVar => !process.env[envVar]);

  if (missingEnvironmentVariables.length) {
    throw new Error(`Missing environment variables...`);
  }
};
```

Called early in the application lifecycle to fail with a clear message if Shopify credentials are not configured.

**Role in System:**
Provides actionable error messages for misconfiguration. Prevents silent failures when environment setup is incomplete.

---

## Pattern Summary

| Pattern | Location | Classification | Architectural Significance |
|---------|----------|----------------|---------------------------|
| Context Provider + Promise Injection | `cart-context.tsx` | Creational | Central to cart state management |
| Server Actions | `cart/actions.ts` | Behavioral | Secure cart mutations |
| Data Access Layer | `lib/shopify/index.ts` | Structural | All external API communication |
| Resource Reshaping | `lib/shopify/index.ts` | Structural | Domain type transformation |
| Optimistic Updates | `cart-context.tsx`, `add-to-cart.tsx` | Behavioral | Responsive cart UX |
| URL-Driven State | `variant-selector.tsx`, `gallery.tsx` | Behavioral | Deep linking support |
| Cache Tag Invalidation | `lib/shopify/index.ts` | Behavioral | On-demand cache refresh |
| Type Guards | `lib/type-guards.ts` | Behavioral | Runtime type safety |
| Container/Presentational | Throughout `components/` | Structural | Bundle optimization |
| Suspense Boundaries | Throughout `app/` | Behavioral | Progressive loading |
| Dynamic Component Tagging | `search/filter/item.tsx` | Structural | Reduced prop-drilling |

---

## Patterns Not Present

The repository does not evidence the following patterns, even though they might be expected for a typical e-commerce application:

- **Observer/Pub-Sub:** Cart state is managed through React Context and optimistic updates rather than an event bus.
- **CQRS (Command Query Responsibility Segregation):** Read and write operations use the same data access layer.
- **Saga/Process Manager:** Cart checkout flow delegates to Shopify's hosted checkout rather than managing payment state internally.
- **Circuit Breaker:** No retry logic or fallback behavior for Shopify API failures beyond error throwing.
- **Repository Caching:** No local caching layer between the application and Shopify API beyond Next.js cache tags.

---

## Confidence Assessment

All identified patterns are **Verified** based on direct examination of source code implementing the pattern's defining characteristics. No patterns are classified as "Possible" in this analysis.