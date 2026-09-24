# Low-Level Design

## 1. Scope and Method

This document translates the high-level components of the application into their concrete implementation structure: modules, functions, types, GraphQL contracts, state primitives, server actions, client components, and control flow.

The implementation is a single Next.js 15 (App Router, canary) application written in TypeScript with the React 19 RC. It depends on a single external system, Shopify, accessed through a private Storefront GraphQL API. The application contains no backend of its own; all server logic runs as React Server Components, Server Actions, and route handlers inside the Next.js runtime.

The analysis is grounded in the following source layout:

- `app/`: Next.js App Router pages, layouts, route handlers, and metadata generators.
- `components/`: React components, both server and client.
- `lib/shopify/`: The Shopify integration (GraphQL operations, fragments, types, fetch helper, and domain reshape functions).
- `lib/constants.ts`, `lib/type-guards.ts`, `lib/utils.ts`: Cross-cutting constants, runtime error shape detection, and URL helpers.
- `next.config.ts`, `tsconfig.json`, `postcss.config.mjs`, `app/globals.css`: Build and styling configuration.
- `fonts/Inter-Bold.ttf`: Static font asset consumed by the Open Graph image generator.

## 2. Module and Package Organization

| Path | Role | Server / Client |
|---|---|---|
| `app/layout.tsx` | Root layout, cart context bootstrap, metadata. | Server |
| `app/page.tsx` | Home page. Composes `ThreeItemGrid`, `Carousel`, `Footer`. | Server |
| `app/[page]/page.tsx`, `app/[page]/layout.tsx`, `app/[page]/opengraph-image.tsx` | Dynamic CMS-style page rendering. | Server |
| `app/product/[handle]/page.tsx` | Product detail page, JSON-LD, related products. | Server |
| `app/search/page.tsx`, `app/search/layout.tsx`, `app/search/loading.tsx`, `app/search/children-wrapper.tsx` | Search and listing. | Server + Client (`children-wrapper`) |
| `app/search/[collection]/page.tsx`, `app/search/[collection]/opengraph-image.tsx` | Category page. | Server |
| `app/api/revalidate/route.ts` | Webhook entry point. | Server route handler |
| `app/error.tsx` | Error boundary. | Client (`"use client"`) |
| `app/robots.ts`, `app/sitemap.ts` | SEO metadata endpoints. | Server |
| `app/opengraph-image.tsx` | Site default Open Graph image. | Server |
| `components/cart/*` | Cart context, UI, and server actions. | Mixed |
| `components/product/*` | Product detail UI. | Mixed |
| `components/grid/*` | Tile-based grid primitives. | Server |
| `components/layout/*` | Header, footer, search filters, navigation. | Mixed |
| `components/carousel.tsx`, `components/label.tsx`, `components/logo-square.tsx`, `components/loading-dots.tsx`, `components/price.tsx`, `components/prose.tsx`, `components/welcome-toast.tsx`, `components/opengraph-image.tsx` | Shared UI primitives. | Mixed |
| `lib/shopify/index.ts` | Storefront API client, reshapers, and operations. | Server only (uses `next/headers`, `next/cache`) |
| `lib/shopify/queries/*`, `lib/shopify/mutations/*`, `lib/shopify/fragments/*` | GraphQL documents. | N/A (string constants) |
| `lib/shopify/types.ts` | Domain and operation types. | N/A |
| `lib/constants.ts`, `lib/type-guards.ts`, `lib/utils.ts` | Cross-cutting helpers. | Server safe |

## 3. Component Map (Logical to Concrete)

### 3.1 Shopify Storefront Adapter

Logical component: provider integration responsible for talking to Shopify, normalizing responses, and applying Next.js caching.

Concrete realization:

- Module: `lib/shopify/index.ts`
- Module: `lib/shopify/types.ts`
- Submodules: `lib/shopify/queries/{cart,collection,menu,page,product}.ts`
- Submodules: `lib/shopify/mutations/cart.ts`
- Submodules: `lib/shopify/fragments/{cart,image,product,seo}.ts`
- Configuration: `lib/utils.ts` (`validateEnvironmentVariables`)

Key exported functions and their behavior:

- `shopifyFetch<T>({ headers?, query, variables? })` (`lib/shopify/index.ts:71`): Generic POST to the Storefront GraphQL endpoint. Reads `endpoint` and `key` from module-scope constants derived from `SHOPIFY_STORE_DOMAIN` and `SHOPIFY_STOREFRONT_ACCESS_TOKEN`. Throws `Error("SHOPIFY_STORE_DOMAIN environment variable is not set")` when the domain is missing. Throws the first element of `body.errors` if present. Wraps thrown values into a normalized shape: `{ cause, status, message, query }` for `ShopifyErrorLike` values, otherwise `{ error, query }`.
- `removeEdgesAndNodes<T>(array: Connection<T>)` (`lib/shopify/index.ts:125`): Unwraps `{ edges: [{ node }] }` GraphQL connection responses into a flat array of nodes.
- `reshapeCart(cart: ShopifyCart): Cart` (`lib/shopify/index.ts:129`): Defaults `cost.totalTaxAmount` to `{ amount: "0.0", currencyCode }` if absent, replaces the `Connection<CartItem>` `lines` with `CartItem[]`.
- `reshapeCollection(collection)` (`lib/shopify/index.ts:143`): Attaches `path = "/search/${collection.handle}"`.
- `reshapeCollections(collections)` (`lib/shopify/index.ts:156`): Filters falsy entries and reshapes the remainder.
- `reshapeImages(images, productTitle)` (`lib/shopify/index.ts:172`): Sets a derived `altText` of the form `${productTitle} - ${filename}` if missing; the filename is parsed from the URL using a regex match.
- `reshapeProduct(product, filterHiddenProducts = true)` (`lib/shopify/index.ts:184`): Returns `undefined` if the product is missing or tagged with `HIDDEN_PRODUCT_TAG` (`"nextjs-frontend-hidden"`). Flattens `images` and `variants` connections.
- `reshapeProducts(products)` (`lib/shopify/index.ts:204`): Filters and reshapes a list of products.
- Cart operations: `createCart`, `addToCart`, `removeFromCart`, `updateCart`, `getCart`. All call `shopifyFetch` with the corresponding GraphQL document and return `reshapeCart` results. `getCart` is marked with `"use cache: private"`, tags `TAGS.cart`, and uses `cacheLife("seconds")`. The other cart mutations read the cart id from `cookies().get("cartId")`.
- Content operations: `getCollection`, `getCollectionProducts`, `getCollections`, `getMenu`, `getPage`, `getPages`, `getProduct`, `getProductRecommendations`, `getProducts`. All marked `"use cache"` except `getPage`/`getPages`, with `cacheTag` set to the relevant tag (`TAGS.collections`, `TAGS.products`) and `cacheLife("days")`.
  - `getCollectionProducts` and `getCollections` short-circuit to a safe fallback when the Shopify endpoint is not configured (`endpoint === ""`). For `getCollections` the fallback is a single synthetic `All` collection; for `getCollectionProducts` it returns `[]` and logs a message.
  - `getCollections` always prepends a synthetic `All` collection, then filters out any remaining collection whose handle starts with `hidden`.
  - `getMenu` rewrites item URLs by stripping the configured domain, replacing `/collections` with `/search`, and removing `/pages`.
- `revalidate(req: NextRequest): Promise<NextResponse>` (`lib/shopify/index.ts:506`): Webhook handler. Reads `x-shopify-topic` and `secret` from the URL. Topics `collections/{create,delete,update}` and `products/{create,delete,update}` trigger `revalidateTag(TAGS.collections, "seconds")` and `revalidateTag(TAGS.products, "seconds")` respectively. Returns `200` for all requests, including the `401` for an invalid secret, to prevent Shopify webhook retries.

Operation-to-document mapping:

| Function | GraphQL document | Source |
|---|---|---|
| `createCart` | `createCartMutation` | `lib/shopify/mutations/cart.ts:14` |
| `addToCart` | `addToCartMutation` | `lib/shopify/mutations/cart.ts:3` |
| `removeFromCart` | `removeFromCartMutation` | `lib/shopify/mutations/cart.ts:36` |
| `updateCart` | `editCartItemsMutation` | `lib/shopify/mutations/cart.ts:25` |
| `getCart` | `getCartQuery` | `lib/shopify/queries/cart.ts:3` |
| `getCollection` | `getCollectionQuery` | `lib/shopify/queries/collection.ts:17` |
| `getCollections` | `getCollectionsQuery` | `lib/shopify/queries/collection.ts:26` |
| `getCollectionProducts` | `getCollectionProductsQuery` | `lib/shopify/queries/collection.ts:39` |
| `getMenu` | `getMenuQuery` | `lib/shopify/queries/menu.ts:1` |
| `getPage` | `getPageQuery` | `lib/shopify/queries/page.ts:21` |
| `getPages` | `getPagesQuery` | `lib/shopify/queries/page.ts:30` |
| `getProduct` | `getProductQuery` | `lib/shopify/queries/product.ts:3` |
| `getProductRecommendations` | `getProductRecommendationsQuery` | `lib/shopify/queries/product.ts:29` |
| `getProducts` | `getProductsQuery` | `lib/shopify/queries/product.ts:12` |

### 3.2 Cart Subsystem

Logical component: persistent user cart, represented by a Shopify cart id stored in a browser cookie, surfaced to the UI as an optimistic React context.

Concrete realization:

- Cookie: `cartId` (`components/cart/actions.ts:105`).
- Server actions module: `components/cart/actions.ts` ("use server").
  - `addItem(prevState, selectedVariantId)`: If the variant is undefined, returns `"Error adding item to cart"`. Calls `addToCart` from the adapter with `{ merchandiseId, quantity: 1 }` and `updateTag(TAGS.cart)`. Returns the same error string on exception.
  - `removeItem(prevState, merchandiseId)`: Loads the cart, locates the line by `merchandise.id`, calls `removeFromCart([lineItem.id])` and invalidates the cart tag. Returns `"Error fetching cart"` or `"Item not found in cart"` if the prerequisites fail.
  - `updateItemQuantity(prevState, payload)`: Loads the cart, locates the line, and either removes the line (if `quantity === 0`), updates the line via `updateCart`, or adds a new line via `addToCart` if the merchandise is absent. Invalidates `TAGS.cart` on success.
  - `redirectToCheckout()`: Fetches the current cart and calls `redirect(cart!.checkoutUrl)` (Shopify-hosted checkout).
  - `createCartAndSetCookie()`: Calls `createCart()` and sets the `cartId` cookie to the new cart id.
- Client context: `components/cart/cart-context.tsx`.
  - Exports `CartProvider` and `useCart`.
  - The provider stores only a `Promise<Cart | undefined>` and exposes it through `CartContext`.
  - The hook `useCart()` consumes the promise with `use(context.cartPromise)`, then runs `useOptimistic(initialCart, cartReducer)`.
  - `cartReducer` handles two actions:
    - `UPDATE_ITEM { merchandiseId, updateType: "plus" | "minus" | "delete" }`: Maps over `lines`, calling `updateCartItem`. If the line quantity reaches 0, the line is removed. Recomputes `totalQuantity` and `cost` via `updateCartTotals`.
    - `ADD_ITEM { variant, product }`: Finds the existing line for the variant, increments or appends via `createOrUpdateCartItem`. Recomputes totals.
  - `calculateItemCost(quantity, price)` multiplies and returns a string. `updateCartTotals(lines)` computes `totalQuantity`, a single currency code (default `"USD"`), and sets `subtotalAmount`, `totalAmount`, and `totalTaxAmount` to `0`. The `totalTaxAmount` for the optimistic cart is always set to `"0"` and the real tax amount from the server is only seen after the next non-optimistic render.
  - `createEmptyCart()` produces a zero-quantity cart skeleton used when the initial cart is `undefined`.
- Client UI: `components/cart/modal.tsx` (uses `@headlessui/react` `Dialog`/`Transition`).
  - On mount, if `cart` is falsy, calls the server action `createCartAndSetCookie`.
  - Tracks `quantityRef` to detect changes; opens automatically when the optimistic total quantity changes from 0 to positive.
  - Renders a sorted list of cart lines. For each line, it builds a `merchandiseUrl` by mapping `selectedOptions` (other than the `"Default Title"` constant `DEFAULT_OPTION`) into search parameters and using `createUrl` from `lib/utils.ts`.
  - Renders `DeleteItemButton`, `EditItemQuantityButton` (plus/minus), `Price` (tax, total), and a checkout form whose `action={redirectToCheckout}` is a server action. The `CheckoutButton` reads `useFormStatus` to disable the button and show `LoadingDots` while pending.
- Add to cart UI: `components/cart/add-to-cart.tsx` ("use client").
  - Uses `useActionState(addItem, null)` to obtain the latest server action result message and a bound `formAction`.
  - Determines the selected variant by matching each `selectedOptions[i]` value to a search parameter named after the option (lower-cased). If there is exactly one variant, falls back to that variant. Reads the URL via `useSearchParams`.
  - The form's `action` first dispatches an optimistic `addCartItem(finalVariant, product)` to the cart context, then invokes the bound `addItemAction` server action.
  - The submit button (`SubmitButton`) is a local component that disables itself and shows "Out Of Stock" when `!availableForSale`, and is disabled with a "Please select an option" state when no variant is selected.
- Quantity edit button: `components/cart/edit-item-quantity-button.tsx` ("use client"). Uses `useActionState(updateItemQuantity, null)`. Binds the form action with `{ merchandiseId, quantity: type === "plus" ? item.quantity + 1 : item.quantity - 1 }`. The form first dispatches an optimistic update with `optimisticUpdate(payload.merchandiseId, type)` then invokes the bound server action.
- Delete item button: `components/cart/delete-item-button.tsx` ("use client"). Uses `useActionState(removeItem, null)`. Binds the action to the merchandise id; the form dispatches `optimisticUpdate(merchandiseId, "delete")` then the server action.

### 3.3 Product Page Subsystem

Logical component: product detail view.

Concrete realization:

- Route entry: `app/product/[handle]/page.tsx`.
  - `generateMetadata` (server): Calls `getProduct(params.handle)`. If the product is missing, calls `notFound()`. Returns `Metadata` with title, description, `robots.index/follow` derived from `!product.tags.includes(HIDDEN_PRODUCT_TAG)`, and an OpenGraph image when a `featuredImage` exists.
  - Default export (server): Fetches the product with `getProduct`. On `undefined`, returns `notFound()`. Emits a `Product` JSON-LD `<script type="application/ld+json">` element with `@type: AggregateOffer` and an availability mapping based on `product.availableForSale`. Composes a two-column flex layout: `Gallery` (wrapped in `Suspense`) on the left and `ProductDescription` (also wrapped in `Suspense`) on the right, plus a `RelatedProducts` section. Renders `Footer` at the bottom.
  - Internal `RelatedProducts({ id })`: Calls `getProductRecommendations(id)`; returns `null` if empty. Renders a horizontal list of `<Link>` items, each containing a `GridTileImage` with `fill` layout.
- Gallery: `components/product/gallery.tsx` ("use client"). Reads the active image index from the `image` search parameter (parsed with `parseInt`; default 0). Provides previous/next buttons that call `router.replace("?" + params)` with the updated `image` index. Renders the active image with `next/image` (`priority: true`) and an inline thumbnail strip where the active thumbnail uses `active: true` on `GridTileImage`.
- Product description: `components/product/product-description.tsx` (server). Composes title, a rounded blue price pill, `VariantSelector`, optional `Prose` HTML, and `AddToCart`.
- Variant selector: `components/product/variant-selector.tsx` ("use client"). Returns `null` when there are no options or exactly one option with one value. Builds `combinations` from `variants` with a lowercase option-name key map. For each option value, it computes `optionParams` from the current `searchParams` (preserving other params), filters to only known option keys, and checks `isAvailableForSale` by matching the combination. The button is disabled with an "Out of Stock" affordance when no matching combination is available. The button's `formAction` calls `updateOption(name, value)` which performs `router.replace("?" + params)`.
- Add to cart: see Cart Subsystem.

### 3.4 Search / Collection Subsystem

Logical component: browse-by-collection and free-text search.

Concrete realization:

- Route: `app/search/page.tsx` (server). Reads `sort` and `q` from `searchParams` (now a Promise in Next 15). Resolves a `sortKey`/`reverse` pair from `sorting` (using `defaultSort` when missing). Calls `getProducts({ sortKey, reverse, query: searchValue })`. Renders a heading announcing either the result count or a "no results" message, and a `Grid` of `ProductGridItems`.
- Route: `app/search/[collection]/page.tsx` (server). Reads `sort` from `searchParams` and the collection handle from `params`. Resolves sort from `sorting`. Calls `getCollection` (used by `generateMetadata` and `opengraph-image.tsx`) and `getCollectionProducts({ collection, sortKey, reverse })`. Renders a `Grid` of `ProductGridItems` or a "No products found in this collection" message.
- Layout: `app/search/layout.tsx`. Three-column flex container: `Collections` on the left, children in the middle (wrapped in `Suspense` + `ChildrenWrapper`), and `FilterList list={sorting} title="Sort by"` on the right. Includes `Footer`.
- Loading state: `app/search/loading.tsx`. Renders 12 `Grid.Item` skeletons with pulse animation.
- Children wrapper: `app/search/children-wrapper.tsx` ("use client"). Uses `useSearchParams` and returns a `Fragment` keyed by `searchParams.get("q")`, forcing the children subtree to remount when the search query changes.
- Collections sidebar: `components/layout/search/collections.tsx`. `Collections` renders a `Suspense` around `CollectionList`, which awaits `getCollections()` and renders a `FilterList` with `title="Collections"`. The `Suspense` fallback is a list of skeleton bars.
- Filter list: `components/layout/search/filter/index.tsx`. `FilterList({ list, title? })` renders an inline `<ul>` (desktop) and a `FilterItemDropdown` (mobile), both inside `Suspense` with `fallback={null}`.
- Filter item: `components/layout/search/filter/item.tsx` ("use client"). Branches on `"path" in item`:
  - `PathFilterItem({ item })`: For `Collection` items. Renders a `<Link>` (or `<p>` when active) to `createUrl(item.path, newParams)`. Removes the `q` parameter from the destination.
  - `SortFilterItem({ item })`: Builds an href preserving the existing `q` and setting `sort=item.slug`. Renders a `<Link>` (or `<p>` when active) with `prefetch={!active ? false : undefined}`.
- Filter dropdown: `components/layout/search/filter/dropdown.tsx` ("use client"). Detects clicks outside a `useRef`-tracked container. Computes the active label from `pathname` or `searchParams.get("sort")`. Toggles an absolute-positioned list of `FilterItem`s.
- Sort definition: `lib/constants.ts:8-41` exports `defaultSort` and `sorting` (`SortFilterItem[]`).
- Grid: `components/grid/index.tsx` exports `Grid` and `Grid.Item` (compound component). Both forward props to a `<ul>`/`<li>` while merging className through `clsx`.
- Grid tile image: `components/grid/tile.tsx` renders a wrapper with conditional border, an `Image` (when `src` is present), and a `Label` (when `label` is supplied). Supports an `active` flag for highlighted state.
- Product grid items: `components/layout/product-grid-items.tsx` maps a list of `Product` to `Grid.Item` + `Link` + `GridTileImage`.

### 3.5 Layout, Navigation, and Global UI

Logical component: persistent chrome.

Concrete realization:

- Root layout: `app/layout.tsx`. Reads `SITE_NAME` from `process.env`. Declares a `metadata` object with a templated `title` and a `metadataBase` from `lib/utils.ts#baseUrl`. Returns `<html>` with the Geist font class, `<body>` styled with Tailwind utility classes, a `CartProvider` whose `cartPromise` is the unawaited `getCart()` call (so the cart context can stream in), a `Navbar`, the rendered `children`, a `Toaster` (`sonner`), and a `WelcomeToast`.
- Navbar: `components/layout/navbar/index.tsx` (server).
  - Fetches `getMenu("next-js-frontend-header-menu")`.
  - Layout: Mobile menu trigger (visible below `md`), logo + site name + main menu links, the search box (centered, hidden on mobile), and the cart modal.
  - Wraps `MobileMenu` and `Search` in `Suspense` (with `SearchSkeleton` fallback).
- Mobile menu: `components/layout/navbar/mobile-menu.tsx` ("use client"). Toggles a Headless UI `Dialog` slide-in. Closes on viewport resize above 768px, on `pathname` change, or on `searchParams` change.
- Search box: `components/layout/navbar/search.tsx` ("use client"). Renders a `<Form action="/search">` with a single `name="q"` input. Uses `key={searchParams?.get("q")}` and `defaultValue` from the URL. Also exports `SearchSkeleton`.
- Cart modal trigger: `components/cart/open-cart.tsx` (server). Static icon plus a quantity badge.
- Footer: `components/layout/footer.tsx` (server). Renders logo, `FooterMenu` (wrapped in `Suspense` with a multi-skeleton fallback), a "Deploy" link, and copyright text. `copyrightDate` is `2023 + (currentYear > 2023 ? `-${currentYear}` : "")`. Calls `getMenu("next-js-frontend-footer-menu")`.
- Footer menu: `components/layout/footer-menu.tsx` ("use client"). Renders a list of `FooterMenuItem`. Each item is a `<Link>` whose `active` state is determined by `pathname === item.path` and updated in a `useEffect`.
- Error boundary: `app/error.tsx` ("use client"). Renders an error card with a "Try Again" button that calls `reset`.
- Welcome toast: `components/welcome-toast.tsx` ("use client"). On mount, if the viewport is at least 650px tall and the cookie `welcome-toast=2` is not present, dispatches a `sonner` toast with `id: "welcome-toast"`, `duration: Infinity`, and an `onDismiss` that sets a one-year cookie.
- Price: `components/price.tsx`. Formats `parseFloat(amount)` with `Intl.NumberFormat` (`style: "currency"`, `currencyDisplay: "narrowSymbol"`) and renders the currency code in a `<span>` (`suppressHydrationWarning={true}` to avoid mismatches when the formatter resolves the symbol client-side).
- Label: `components/label.tsx` (server). A pill containing a title and a `Price`, positioned at `bottom` or `center`.
- Prose: `components/prose.tsx` (server). Renders HTML through `dangerouslySetInnerHTML` with Tailwind Typography styling.
- Loading dots: `components/loading-dots.tsx` (server). Three animated dots with staggered delays.
- Logo: `components/logo-square.tsx` (server) wraps `components/icons/logo.tsx` in a square container.

### 3.6 SEO and Discovery Endpoints

Logical component: search engine and social metadata.

Concrete realization:

- `app/sitemap.ts` (`dynamic = "force-dynamic"`): Calls `validateEnvironmentVariables()`. Builds `routesMap` for the home page; fetches `getCollections`, `getProducts({})`, and `getPages` in parallel; combines their URL entries. Catches any rejection and rethrows the serialized error.
- `app/robots.ts`: Returns a single `userAgent: "*"` rule with `sitemap` and `host` from `baseUrl`.
- `app/opengraph-image.tsx`: Renders an `ImageResponse` with the site title (via `components/opengraph-image.tsx`).
- `app/[page]/opengraph-image.tsx`: Renders the page title through the same component.
- `app/search/[collection]/opengraph-image.tsx`: Renders the collection title.
- `components/opengraph-image.tsx` (server): Reads `./fonts/Inter-Bold.ttf` from disk using `fs/promises#readFile`, builds an `ImageResponse` 1200x630 with the font and a black background.

## 4. Type and Contract Inventory

### 4.1 Domain types (`lib/shopify/types.ts`)

- `Maybe<T> = T | null`
- `Connection<T> = { edges: Array<Edge<T>> }`, `Edge<T> = { node: T }`
- `Image = { url; altText; width; height }`
- `Money = { amount: string; currencyCode: string }` (amount is a decimal string, never a number)
- `SEO = { title; description }`
- `ProductOption = { id; name; values: string[] }`
- `ProductVariant = { id; title; availableForSale; selectedOptions: { name; value }[]; price: Money }`
- `ShopifyProduct = { id; handle; availableForSale; title; description; descriptionHtml; options; priceRange: { maxVariantPrice; minVariantPrice }; variants: Connection<ProductVariant>; featuredImage; images: Connection<Image>; seo; tags: string[]; updatedAt }`
- `Product = Omit<ShopifyProduct, "variants" | "images"> & { variants: ProductVariant[]; images: Image[] }` — the public product shape after `reshapeProduct`.
- `ShopifyCollection = { handle; title; description; seo; updatedAt }`
- `Collection = ShopifyCollection & { path: string }` — after `reshapeCollection`.
- `CartProduct = { id; handle; title; featuredImage }`
- `CartItem = { id?; quantity; cost: { totalAmount: Money }; merchandise: { id; title; selectedOptions: { name; value }[]; product: CartProduct } }`
- `ShopifyCart = { id?; checkoutUrl; cost: { subtotalAmount; totalAmount; totalTaxAmount: Money }; lines: Connection<CartItem>; totalQuantity }`
- `Cart = Omit<ShopifyCart, "lines"> & { lines: CartItem[] }` — the public cart shape after `reshapeCart`.
- `Page = { id; title; handle; body; bodySummary; seo?; createdAt; updatedAt }`
- `Menu = { title; path: string }`

### 4.2 Operation response types

Each Storefront query/mutation has a corresponding `Shopify*Operation` type pairing `data` with `variables` (where applicable):

- `ShopifyCartOperation` (`cartId`)
- `ShopifyCreateCartOperation` (no variables)
- `ShopifyAddToCartOperation` (`cartId`, `lines: { merchandiseId; quantity }[]`)
- `ShopifyRemoveFromCartOperation` (`cartId`, `lineIds: string[]`)
- `ShopifyUpdateCartOperation` (`cartId`, `lines: { id; merchandiseId; quantity }[]`)
- `ShopifyCollectionOperation` (`handle`)
- `ShopifyCollectionProductsOperation` (`handle`, `reverse?`, `sortKey?`)
- `ShopifyCollectionsOperation` (no variables)
- `ShopifyMenuOperation` (`handle`)
- `ShopifyPageOperation` (`handle`)
- `ShopifyPagesOperation` (no variables)
- `ShopifyProductOperation` (`handle`)
- `ShopifyProductRecommendationsOperation` (`productId`)
- `ShopifyProductsOperation` (`query?`, `reverse?`, `sortKey?`)

### 4.3 GraphQL fragments

- `image` (`url`, `altText`, `width`, `height`)
- `seo` (`title`, `description`)
- `product` (in `lib/shopify/fragments/product.ts`): id, handle, availableForSale, title, description, descriptionHtml, options, priceRange (max/min), `variants(first: 250)` connection, `featuredImage` with `image` fragment, `images(first: 20)` connection, `seo` with `seo` fragment, tags, updatedAt.
- `collection` (inline in `lib/shopify/queries/collection.ts`): handle, title, description, seo, updatedAt.
- `page` (inline in `lib/shopify/queries/page.ts`): id, title, handle, body, bodySummary, seo, createdAt, updatedAt.
- `cart` (in `lib/shopify/fragments/cart.ts`): id, checkoutUrl, cost (subtotal/total/totalTax), `lines(first: 100)` connection with `cost.totalAmount` and merchandise product fragment, `totalQuantity`.

### 4.4 Cross-cutting types

- `lib/constants.ts` defines `SortFilterItem` and the `TAGS` map (`collections`, `products`, `cart`) used as cache tags, plus `HIDDEN_PRODUCT_TAG`, `DEFAULT_OPTION`, and `SHOPIFY_GRAPHQL_API_ENDPOINT` ("/api/2023-01/graphql.json").
- `lib/type-guards.ts` defines `ShopifyErrorLike` and `isShopifyError` (recursive prototype walk to detect `Error` instances and `Error`-like plain objects).
- `components/layout/search/filter/index.tsx` defines `ListItem = SortFilterItem | PathFilterItem` and `PathFilterItem = { title; path }`.
- `components/product/variant-selector.tsx` defines an internal `Combination = { id; availableForSale; [key: string]: string | boolean }` for the per-option lookup table.
- `components/cart/cart-context.tsx` defines `UpdateType`, `CartAction`, and `CartContextType` (carrying `cartPromise`).

## 5. Important Data Flow and Control Flow

### 5.1 Cart read on initial render

1. `app/layout.tsx` (server) calls `getCart()` and passes the unawaited `Promise<Cart | undefined>` to `CartProvider`.
2. `getCart` (`lib/shopify/index.ts:270`) is marked `"use cache: private"`, tags `TAGS.cart`, and uses `cacheLife("seconds")`. It reads the `cartId` cookie, short-circuits to `undefined` when missing, and otherwise calls `shopifyFetch` with `getCartQuery`.
3. `CartProvider` (`components/cart/cart-context.tsx:193`) stores the promise in `CartContext`.
4. `useCart()` (`components/cart/cart-context.tsx:207`) calls `use(context.cartPromise)` to unwrap it, then `useOptimistic(initialCart, cartReducer)` to layer the optimistic state.
5. `CartModal` (`components/cart/modal.tsx`) calls `useCart`; on `useEffect`, if `cart` is falsy, it calls the `createCartAndSetCookie` server action. It opens automatically when the optimistic total quantity changes from zero.

### 5.2 Add to cart

1. `AddToCart` (`components/cart/add-to-cart.tsx:60`) selects the variant from URL search parameters whose name matches each option (lower-cased). If only one variant exists, it is used.
2. The form's `action` is an async function: it first calls `addCartItem(finalVariant, product)` (which dispatches an `ADD_ITEM` action to `useOptimistic`), then `addItemAction()` (the bound server action).
3. The server action `addItem` (`components/cart/actions.ts:15`) calls `addToCart` with `quantity: 1`, then `updateTag(TAGS.cart)`. The cache tag invalidation causes the next `getCart` invocation to re-execute.
4. When the new cart data resolves, the optimistic value is replaced by the freshly fetched cart through `useOptimistic`.

### 5.3 Update quantity

1. `EditItemQuantityButton` (`components/cart/edit-item-quantity-button.tsx:32`) submits