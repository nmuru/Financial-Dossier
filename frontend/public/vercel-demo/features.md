# Features

## Overview

Next.js Commerce is a headless Shopify storefront built with the Next.js App Router and React Server Components. It delivers a fully functional, server-rendered ecommerce experience by consuming the Shopify Storefront API. This document describes every independently meaningful capability the application exposes to end users, operators, and external systems.

---

## 1. Homepage with Featured Product Display

### Capability

The homepage presents a curated set of featured products in a prominent grid layout, followed by a horizontally scrollable product carousel.

### Actor

Site visitor.

### Workflow

1. A visitor navigates to the root URL (`/`).
2. The server renders a `ThreeItemGrid` component displaying three featured products in a 2/3 + 1/3 grid layout.
3. A `Carousel` component renders below the grid, displaying products from a secondary featured collection in an infinitely looping horizontal scroll.
4. Both sections pull from dedicated Shopify collections named `hidden-homepage-featured-items` and `hidden-homepage-carousel`. Products in collections prefixed with `hidden-` are excluded from search and collection browsing pages.
5. A `Footer` renders at the bottom of the page.

### Outcome

The visitor sees a visually composed homepage with featured products they can immediately interact with.

### Evidence

- `app/page.tsx` renders `ThreeItemGrid` and `Carousel`
- `components/grid/three-items.tsx` fetches `hidden-homepage-featured-items` via `getCollectionProducts`
- `components/carousel.tsx` fetches `hidden-homepage-carousel` via `getCollectionProducts`
- `components/grid/tile.tsx` renders `GridTileImage` with price labels

### Status

Implemented.

---

## 2. Product Catalog and Collection Browsing

### Capability

Site visitors can browse the full product catalog or narrow their view to a specific Shopify collection. Products display in a responsive grid with pagination. Both collection and search views support sorting.

### Actor

Site visitor.

### Workflow

1. A visitor navigates to `/search` to browse all products, or `/search/[collection]` to browse a specific collection.
2. The `SearchLayout` renders a left sidebar with a collection filter list, a center area for the product grid, and a right sidebar with sort options.
3. Products are fetched server-side via `getProducts` (all products) or `getCollectionProducts` (filtered by collection), using sort key and reverse direction derived from URL search parameters.
4. Products are rendered as `GridTileImage` components within a responsive CSS grid.
5. A visitor can select a sort order (Relevance, Trending, Latest Arrivals, Price Low–High, Price High–Low) which updates the URL and re-fetches the product list server-side.
6. A visitor can click a collection name in the left sidebar to navigate to `/search/[collection]` for that collection's products.

### Outcome

The visitor browses and sorts products within the full catalog or a specific collection.

### Evidence

- `app/search/page.tsx` — all-products search view with `getProducts`
- `app/search/[collection]/page.tsx` — collection-specific view with `getCollectionProducts`
- `app/search/layout.tsx` — layout composing collections sidebar, sort sidebar, and product grid
- `lib/constants.ts` — defines `sorting` array with five sort options (Relevance, Trending, Latest, Price asc/desc)
- `components/layout/search/collections.tsx` — fetches collections and renders `FilterList`
- `components/layout/search/filter/index.tsx` — renders sort filter items
- `components/layout/search/filter/item.tsx` — `PathFilterItem` for collections, `SortFilterItem` for sort options
- `components/layout/product-grid-items.tsx` — renders product grid items as clickable tiles

### Status

Implemented.

---

## 3. Product Search

### Capability

A search input in the navbar allows visitors to query the Shopify product catalog by keyword. Results are displayed on the `/search` page filtered by the search query.

### Actor

Site visitor.

### Workflow

1. A visitor types a keyword into the search input in the `Navbar`.
2. The form submits a `GET` request to `/search?q=<keyword>`.
3. The `SearchPage` component extracts the `q` parameter and passes it as the `query` argument to `getProducts`.
4. The product grid renders only matching products. If no matches exist, a "There are no products that match" message is displayed.
5. The search query is preserved in the URL, allowing shareable search result links.

### Outcome

The visitor sees products matching their search keyword.

### Evidence

- `components/layout/navbar/search.tsx` — client component with a `<Form>` posting to `/search`
- `app/search/page.tsx` — reads `searchParams.q` and passes to `getProducts({ query: searchValue })`
- `lib/shopify/index.ts` — `getProducts` sends `query` variable to Shopify GraphQL API
- `lib/shopify/queries/product.ts` — `getProductsQuery` includes a `$query` variable passed to Shopify's `products` connection

### Status

Implemented.

---

## 4. Product Detail Page

### Capability

A dedicated page displays complete information for a single product: images, title, description, price, available variants, and an add-to-cart control. Related product recommendations appear below the main content.

### Actor

Site visitor.

### Workflow

1. A visitor navigates to `/product/[handle]` where `[handle]` is the product's Shopify handle.
2. The page server component fetches the product via `getProduct(handle)`.
3. A `Gallery` component renders the product's images with prev/next navigation and a thumbnail strip.
4. A `ProductDescription` component renders the title, price, description HTML, and a `VariantSelector`.
5. An `AddToCart` button triggers the cart-add action.
6. A `RelatedProducts` section fetches and displays related products via `getProductRecommendations(productId)`.
7. The page injects JSON-LD structured data (`Product` schema) for SEO and renders OpenGraph metadata.
8. Products tagged with `nextjs-frontend-hidden` are excluded from search indexing (controlled by the `HIDDEN_PRODUCT_TAG` constant).

### Outcome

The visitor views detailed product information and can add the product to their cart or navigate to related products.

### Evidence

- `app/product/[handle]/page.tsx` — product detail page with JSON-LD, gallery, description, and related products
- `components/product/gallery.tsx` — image gallery with navigation and thumbnails
- `components/product/product-description.tsx` — title, price, description HTML
- `components/product/variant-selector.tsx` — option selector with availability indicators
- `components/cart/add-to-cart.tsx` — add-to-cart form with optimistic UI
- `lib/constants.ts` — `HIDDEN_PRODUCT_TAG = "nextjs-frontend-hidden"`
- `lib/shopify/index.ts` — `getProduct`, `getProductRecommendations` functions

### Status

Implemented.

---

## 5. Product Variant Selection

### Capability

When a product has multiple variants (e.g., size or color options), visitors can select their preferred variant. The UI visually indicates which combinations are available for purchase and which are out of stock.

### Actor

Site visitor on a product detail page.

### Workflow

1. The `VariantSelector` component renders option buttons for each product option (e.g., Size, Color).
2. The visitor clicks an option value (e.g., "Large").
3. The component updates the URL search params (e.g., `?size=large`) via `router.replace` without a full page reload.
4. The `AddToCart` component reads the selected variant from URL search params and uses it for the cart operation.
5. Variant buttons are styled to indicate: active selection (ring highlight), available (hover ring), or unavailable/out of stock (strikethrough style).
6. When all required options are selected, the `AddToCart` button becomes enabled.

### Outcome

The visitor selects a specific product variant before adding to cart, with clear visual feedback on availability.

### Evidence

- `components/product/variant-selector.tsx` — client component managing option selection via URL params
- `components/product/variant-selector.tsx` lines 62–75 — availability checking against variant combinations
- `components/cart/add-to-cart.tsx` lines 66–73 — reads selected variant from `useSearchParams`

### Status

Implemented.

---

## 6. Add to Cart

### Capability

A visitor can add a product (with selected variant) to their shopping cart. The operation uses optimistic UI to update the cart display immediately, while the server action communicates the change to Shopify in the background.

### Actor

Site visitor on a product detail page.

### Workflow

1. The visitor selects a variant (if applicable) and clicks the "Add To Cart" button.
2. `AddToCart` binds the selected variant ID and calls `addCartItem(finalVariant, product)` to update the optimistic cart state.
3. Simultaneously, `addItem` server action invokes `addToCart` which calls the Shopify Storefront API `cartLinesAdd` mutation.
4. The cart's `totalQuantity` increases and the cart modal slides open automatically.
5. If no variant is selected or the variant is unavailable, the button is disabled.

### Outcome

The item is added to the visitor's cart and the cart modal opens.

### Evidence

- `components/cart/add-to-cart.tsx` — client form with `useActionState` and optimistic cart update
- `components/cart/actions.ts` — `addItem` server action calling `addToCart` from `lib/shopify`
- `components/cart/cart-context.tsx` — `useCart` hook with `addCartItem` for optimistic updates
- `lib/shopify/index.ts` lines 228–239 — `addToCart` function using `cartLinesAdd` mutation
- `lib/shopify/mutations/cart.ts` — `addToCartMutation` GraphQL

### Status

Implemented.

---

## 7. Shopping Cart Modal

### Capability

A slide-in cart drawer displays the current cart's items, quantities, prices, subtotal, taxes placeholder, and a checkout button. The cart auto-opens when items are added and persists across page navigations via a browser cookie.

### Actor

Site visitor.

### Workflow

1. On first load, the `CartModal` checks for a `cartId` cookie. If absent, `createCartAndSetCookie` is called to create a new Shopify cart and persist its ID in a cookie.
2. The `CartProvider` wraps the application and passes the cart promise down to client components via React Context.
3. When a visitor adds an item, the cart modal slides open automatically if it was closed (`app/search/layout.tsx` and similar).
4. The cart modal renders each line item with: product image, title, variant title (if not default), quantity stepper, line total price, and a delete button.
5. Quantity changes and deletions use optimistic updates in the UI while server actions sync with Shopify.
6. The checkout button redirects to Shopify's hosted checkout URL (`cart.checkoutUrl`).

### Outcome

The visitor views, modifies, and proceeds to checkout their shopping cart.

### Evidence

- `components/cart/modal.tsx` — full cart drawer with line items, totals, and checkout
- `components/cart/cart-context.tsx` — `CartProvider`, `useCart`, `cartReducer` for optimistic state
- `components/cart/actions.ts` — `createCartAndSetCookie`, `redirectToCheckout` server actions
- `components/cart/open-cart.tsx` — cart icon with item count badge
- `lib/shopify/index.ts` lines 220–226 — `createCart` function
- `lib/shopify/fragments/cart.ts` — GraphQL fragment fetching `checkoutUrl`

### Status

Implemented.

---

## 8. Cart Quantity Management

### Capability

A visitor can increase, decrease, or remove items from their cart. Changes update the Shopify cart via server actions and reflect in the UI optimistically.

### Actor

Site visitor with items in their cart.

### Workflow

1. In the cart modal, each line item has `+` and `−` buttons managed by `EditItemQuantityButton`.
2. Clicking `+` or `−` triggers `updateItemQuantity` with the new quantity. The `−` button reduces quantity; if quantity reaches zero, the item is removed via `removeFromCart`.
3. A delete button (`DeleteItemButton`) calls `removeItem` to remove the item entirely.
4. Both operations update the optimistic cart state immediately and invoke the corresponding Shopify mutation (`cartLinesUpdate` or `cartLinesRemove`) in the background.
5. The cart's `totalQuantity` and cost totals recalculate automatically via the cart reducer.

### Outcome

The visitor adjusts cart item quantities or removes items, with immediate UI feedback.

### Evidence

- `components/cart/edit-item-quantity-button.tsx` — quantity increment/decrement
- `components/cart/delete-item-button.tsx` — item removal
- `components/cart/actions.ts` — `updateItemQuantity` and `removeItem` server actions
- `components/cart/cart-context.tsx` lines 39–66 — `updateCartItem` reducer logic
- `lib/shopify/index.ts` lines 242–268 — `removeFromCart`, `updateCart` Shopify API calls
- `lib/shopify/mutations/cart.ts` — `editCartItemsMutation`, `removeFromCartMutation`

### Status

Implemented.

---

## 9. Checkout Redirect

### Capability

A visitor can proceed to checkout. The application redirects to Shopify's hosted checkout page, which handles payment processing and order fulfillment.

### Actor

Site visitor with items in their cart.

### Workflow

1. The visitor clicks "Proceed to Checkout" in the cart modal.
2. `redirectToCheckout` server action retrieves the current cart via `getCart()` and calls `redirect(cart.checkoutUrl)`.
3. The visitor is redirected to Shopify's secure checkout page.
4. The cart persists in Shopify; the `cartId` cookie remains until the visitor completes or abandons checkout.

### Outcome

The visitor transitions to Shopify's checkout flow to complete their purchase.

### Evidence

- `components/cart/actions.ts` lines 98–101 — `redirectToCheckout` server action
- `components/cart/modal.tsx` lines 218–220 — checkout form
- `lib/shopify/fragments/cart.ts` — `checkoutUrl` field in GraphQL fragment
- `lib/shopify/types.ts` line 100 — `checkoutUrl` in `ShopifyCart` type

### Status

Implemented.

---

## 10. Static Content Pages

### Capability

The storefront renders Shopify-hosted CMS pages (e.g., "About Us", "Shipping Policy") as regular HTML pages.

### Actor

Site visitor navigating to a CMS page.

### Workflow

1. A visitor navigates to `/[handle]` (e.g., `/about-us`).
2. The page fetches content via `getPage(handle)` from the Shopify Storefront API.
3. The page renders the title and body HTML (rendered via a `Prose` component) along with an "updated at" date.
4. Metadata (title, description, OpenGraph) is generated from the page's SEO fields.

### Outcome

The visitor reads CMS content hosted in Shopify.

### Evidence

- `app/[page]/page.tsx` — dynamic CMS page renderer
- `lib/shopify/index.ts` lines 426–433 — `getPage` function
- `lib/shopify/queries/page.ts` — `getPageQuery` GraphQL
- `components/prose.tsx` — renders HTML content safely

### Status

Implemented.

---

## 11. Dynamic Navigation Menus

### Capability

The header and footer navigation menus are populated from Shopify menus. Menu items in the header link to collection pages (`/search/[collection]`); footer links link to CMS pages.

### Actor

Site visitor using navigation.

### Workflow

1. `Navbar` and `Footer` server components call `getMenu("next-js-frontend-header-menu")` and `getMenu("next-js-frontend-footer-menu")` respectively.
2. `getMenu` fetches menu items from Shopify and rewrites URLs: `/collections/*` becomes `/search/*`, and `/pages/*` paths are stripped to root-relative paths.
3. The header renders the logo, nav links, search bar, and cart icon.
4. The footer renders the logo, nav links, copyright, and Vercel attribution.
5. On mobile, a `MobileMenu` drawer provides the same nav links in a slide-in panel.

### Outcome

The visitor navigates between collections, CMS pages, and other sections using dynamic menus sourced from Shopify.

### Evidence

- `components/layout/navbar/index.tsx` — header with logo, nav, search, cart
- `components/layout/navbar/mobile-menu.tsx` — mobile navigation drawer
- `components/layout/footer.tsx` — footer with menu and copyright
- `components/layout/footer-menu.tsx` — footer menu rendering with active link highlighting
- `lib/shopify/index.ts` lines 398–424 — `getMenu` with URL rewriting logic
- `lib/shopify/queries/menu.ts` — `getMenuQuery` GraphQL

### Status

Implemented.

---

## 12. On-Demand Cache Revalidation

### Capability

When Shopify products or collections are created, updated, or deleted, the application receives webhook notifications and revalidates its Next.js cache tags to reflect the latest data without a full redeploy.

### Actor

Shopify (via webhook) or an operator with the revalidation secret.

### Workflow

1. Shopify sends a `POST` request to `/api/revalidate?secret=<SHOPIFY_REVALIDATION_SECRET>` with an `x-shopify-topic` header indicating the event type.
2. The handler validates the secret. If invalid, it returns a 401 response.
3. It checks the topic against known product and collection webhook events.
4. For collection events (`collections/create`, `collections/delete`, `collections/update`), it calls `revalidateTag(TAGS.collections)`.
5. For product events (`products/create`, `products/delete`, `products/update`), it calls `revalidateTag(TAGS.products)`.
6. For any other topic, it returns 200 without revalidating.

### Outcome

Cached product and collection pages are invalidated and refetched from Shopify on the next request.

### Evidence

- `app/api/revalidate/route.ts` — `POST` handler calling `revalidate(req)`
- `lib/shopify/index.ts` lines 505–543 — `revalidate` function with topic parsing and `revalidateTag` calls
- `lib/constants.ts` — `TAGS` object defining cache tag keys

### Status

Implemented.

---

## 13. Dynamic Sitemap Generation

### Capability

The application generates a `sitemap.xml` that lists all product, collection, and CMS page URLs along with their last-modified timestamps. This supports search engine indexing.

### Actor

Search engine crawlers.

### Workflow

1. A crawler requests `/sitemap.xml`.
2. The `sitemap.ts` file fetches all collections via `getCollections`, all products via `getProducts`, and all pages via `getPages`.
3. It constructs a `MetadataRoute.Sitemap` array mapping each entity to its URL and `updatedAt` timestamp.
4. The sitemap includes the root URL `/`.
5. Collections prefixed with `hidden-` are included in the sitemap because they are filtered at the query level (not excluded at the sitemap level), though they are excluded from search pages.

### Outcome

Search engines can discover all public URLs.

### Evidence

- `app/sitemap.ts` — generates sitemap from collections, products, and pages
- `lib/utils.ts` — `baseUrl` for constructing absolute URLs

### Status

Implemented.

---

## 14. Robots.txt

### Capability

The application serves a `robots.txt` file that allows all crawlers and references the sitemap URL.

### Actor

Search engine crawlers.

### Workflow

1. A crawler requests `/robots.txt`.
2. The `robots.ts` file returns a robots configuration allowing all user agents, with a reference to the sitemap at `<baseUrl>/sitemap.xml`.

### Outcome

Search engines are directed to the sitemap and allowed to crawl the site.

### Evidence

- `app/robots.ts` — generates robots.txt configuration

### Status

Implemented.

---

## 15. SEO Metadata

### Capability

Product, collection, and CMS pages generate structured metadata (title, description, OpenGraph) for search engines and social media sharing.

### Actor

Search engines, social media platforms, visitors sharing links.

### Workflow

1. Each dynamic page exports a `generateMetadata` async function.
2. The function fetches the entity (product, collection, or page) and extracts SEO fields from Shopify.
3. Next.js assembles `<title>`, `<meta name="description">`, and OpenGraph tags into the document `<head>`.
4. Product pages additionally include `robots` meta tags that prevent indexing of products tagged with `HIDDEN_PRODUCT_TAG`.

### Outcome

Pages are indexed with appropriate titles, descriptions, and social sharing metadata.

### Evidence

- `app/product/[handle]/page.tsx` lines 13–47 — product metadata with robots control
- `app/search/[collection]/page.tsx` lines 9–24 — collection metadata
- `app/[page]/page.tsx` lines 7–24 — CMS page metadata
- `app/page.tsx` lines 5–11 — homepage metadata

### Status

Implemented.

---

## 16. Structured Data (JSON-LD)

### Capability

Product detail pages embed JSON-LD structured data in the document `<head>` conforming to the Schema.org `Product` type, enabling rich search results.

### Actor

Search engines that support structured data.

### Workflow

1. On the product detail page, a `productJsonLd` object is constructed containing `name`, `description`, `image`, and `offers` fields.
2. It is serialized and injected into a `<script type="application/ld+json">` tag.
3. The `offers` block includes `availability` (InStock/OutOfStock), `priceCurrency`, `highPrice`, and `lowPrice`.

### Outcome

Search engines can parse structured product data for rich results.

### Evidence

- `app/product/[handle]/page.tsx` lines 58–82 — JSON-LD injection

### Status

Implemented.

---

## 17. Dynamic OpenGraph Images

### Capability

Product, collection, and CMS pages generate dynamic OpenGraph images (1200×630) for social sharing using Next.js's `ImageResponse`.

### Actor

Social media platforms, visitors sharing links.

### Workflow

1. Pages export an `generateImage` function or use the shared `OpengraphImage` component.
2. The component renders a branded image with the site logo and the entity's title.
3. The image is generated at runtime using `@vercel/og`.

### Outcome

Shared links display a branded preview image.

### Evidence

- `components/opengraph-image.tsx` — shared OG image component with Inter Bold font
- `app/opengraph-image.tsx` — root-level OG image export
- `app/product/[handle]/opengraph-image.tsx` — product-specific OG image
- `app/search/[collection]/opengraph-image.tsx` — collection-specific OG image

### Status

Implemented.

---

## 18. Responsive and Adaptive Layout

### Capability

The storefront adapts its layout across desktop, tablet, and mobile viewports. Navigation collapses to a hamburger menu on mobile; product grids reduce column counts; the cart drawer resizes appropriately.

### Actor

Site visitors on any device.

### Workflow

1. Tailwind CSS responsive utility classes (`md:`, `lg:`, `sm:`) control layout breakpoints throughout all components.
2. The navbar shows full nav links on desktop but a hamburger menu on mobile.
3. The product grid displays 1 column on mobile, 2 on tablet, and 3 on desktop.
4. The cart drawer is full-width on mobile and fixed-width (390px) on desktop.
5. Collection and sort filters switch from a sidebar list on desktop to a dropdown on mobile.

### Outcome

The storefront is usable on mobile phones, tablets, and desktop computers.

### Evidence

- `components/layout/navbar/index.tsx` — responsive nav with hamburger on mobile
- `components/layout/navbar/mobile-menu.tsx` — mobile drawer with breakpoint-aware closing
- `components/layout/search/filter/index.tsx` — dual desktop/mobile filter render
- `components/layout/search/filter/dropdown.tsx` — mobile dropdown filter
- `components/grid/tile.tsx` — responsive image sizing with `sizes` prop
- `components/cart/modal.tsx` — responsive cart drawer width

### Status

Implemented.

---

## 19. Dark Mode

### Capability

The storefront renders in either light or dark mode. The color scheme adapts based on the visitor's system preference via CSS `prefers-color-scheme`.

### Actor

Site visitors with dark mode system preference.

### Workflow

1. Tailwind CSS `dark:` variants are applied throughout all components.
2. The `dark:bg-neutral-900`, `dark:text-white` classes switch the palette when the `html` element has the `dark` class.
3. Next.js applies the `dark` class to `<html>` based on system preference automatically when `className` is set on `<html>` in `RootLayout`.

### Outcome

Visitors see the storefront in dark mode if their system prefers it.

### Evidence

- `app/layout.tsx` line 35 — `dark:bg-neutral-900 dark:text-white` on `<body>`
- Numerous components use `dark:` Tailwind variants (e.g., `components/grid/tile.tsx`, `components/cart/modal.tsx`, `components/layout/footer.tsx`)

### Status

Implemented.

---

## 20. Welcome Notification

### Capability

First-time visitors (identified by the absence of a `welcome-toast` cookie) see a dismissible welcome toast notification introducing the storefront.

### Actor

First-time site visitor.

### Workflow

1. `WelcomeToast` is rendered in `RootLayout` as a client component.
2. On mount, it checks for the `welcome-toast` cookie.
3. If absent and the viewport height is sufficient, it displays a toast via `sonner` with a welcome message and a "Deploy your own" link.
4. On dismissal, it sets the cookie with a 1-year max-age.

### Outcome

New visitors receive a brief introduction to the storefront.

### Evidence

- `components/welcome-toast.tsx` — toast with cookie-based display control
- `app/layout.tsx` line 41 — renders `WelcomeToast`
- `package.json` — `sonner` dependency

### Status

Implemented.

---

## 21. Client-Side Error Handling

### Capability

When a client-side error occurs, the application displays a user-friendly error message with a "Try Again" button that re-renders the failed subtree.

### Actor

Site visitor experiencing an unexpected error.

### Workflow

1. The `Error` component (`app/error.tsx`) is a client component that Next.js renders when a client-side error boundary catches an error.
2. It displays a "Oh no!" message and a "Try Again" button.
3. Clicking "Try Again" calls the `reset` function to remount the subtree.

### Outcome

The visitor can recover from client-side errors without a full page reload.

### Evidence

- `app/error.tsx` — client error boundary component

### Status

Implemented.

---

## 22. Loading State Skeletons

### Capability

Portions of the page that depend on asynchronous data show skeleton loading states while the data fetches, preventing layout shift and giving visual feedback.

### Actor

Site visitor waiting for content to load.

### Workflow

1. Server components that fetch data are wrapped in `<Suspense>` boundaries with fallback components.
2. The product gallery on the product detail page shows an empty aspect-ratio placeholder while images load.
3. The `SearchSkeleton` shows a placeholder input field in the navbar during search data fetching.
4. Collection and menu lists show skeleton placeholders during data fetching.

### Outcome

The visitor sees a stable layout with placeholder elements during data loading.

### Evidence

- `app/product/[handle]/page.tsx` lines 86–90 — gallery Suspense fallback
- `components/layout/navbar/search.tsx` lines 31–42 — `SearchSkeleton`
- `components/layout/search/collections.tsx` lines 17–31 — skeleton loading for collections
- `components/layout/footer.tsx` lines 30–40 — footer menu skeleton

### Status

Implemented.

---

## Feature Dependency Map

```text
Shopify Storefront API (external)
    ├── Product/Collection/Cart/Menu Data
    │   ├── Homepage Featured Display
    │   ├── Product Catalog Browsing
    │   ├── Collection Filtering
    │   ├── Product Search
    │   ├── Product Detail Pages
    │   ├── Related Products
    │   ├── Dynamic Navigation Menus
    │   ├── Static Content Pages
    │   └── Sitemap Generation
    └── Checkout URL
        └── Checkout Redirect

Cart State (cookie-backed)
    ├── Create Cart (on first load)
    ├── Add to Cart
    ├── Cart Modal Display
    ├── Cart Quantity Management
    └── Cart Optimistic Updates

Shopify Webhook → Revalidation API
    └── Cache Invalidation

Next.js Metadata APIs
    ├── SEO Metadata
    ├── Structured Data (JSON-LD)
    ├── OpenGraph Images
    └── Sitemap + Robots
```

---

## Documentation vs. Implementation Comparison

| Documented in README | Implementation Status |
|---|---|
| High-performance, server-rendered Next.js App Router storefront | Verified — React Server Components, Server Actions, `Suspense`, `useOptimistic` confirmed |
| Shopify integration | Verified — full Storefront API GraphQL integration |
| Multiple commerce provider support (alternative forks) | Repository is the Shopify-maintained version; other providers are separate forks |
| Orama search upgrade (integration) | Not included in this repository; separate `oramasearch/nextjs-commerce` fork |
| React Bricks CMS (integration) | Not included in this repository; separate `reactbricks/nextjs-commerce-rb` fork |
| Local development with Vercel CLI | Described in README; `.env.example` shows required environment variables |

The README accurately describes the core purpose and technology. Optional integrations (Orama, React Bricks) are maintained as separate repositories rather than being bundled in this one.

---

## Features Not Present

The following capabilities are commonly found in ecommerce storefronts but are not present in this repository:

- **User accounts and authentication** — No login, registration, or account pages.
- **Order history** — No order tracking or past purchase view (orders are handled entirely by Shopify after checkout redirect).