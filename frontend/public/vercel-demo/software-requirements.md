# Software Requirements

## Overview

This document specifies the software requirements for Next.js Commerce, a high-performance server-rendered e-commerce application that integrates with Shopify as a headless commerce platform. The application enables product browsing, cart management, search and filtering, variant selection, and checkout through Shopify's hosted checkout experience.

The requirements in this document are derived from analysis of the repository's implementation, including GraphQL queries, cart operations, product display logic, navigation components, SEO generation, and data models. Each requirement is classified by certainty level based on the strength of supporting evidence.

## Functional Requirements

### Product Browsing and Discovery

**FR-001**: The system must display products in a grid layout on the homepage from a Shopify collection containing exactly three products.

- **Evidence**: `components/grid/three-items.tsx` fetches from collection "hidden-homepage-featured-items" and expects exactly three products (`homepageItems[0]`, `homepageItems[1]`, `homepageItems[2]`).
- **Classification**: Verified

**FR-002**: The system must display a horizontally scrolling carousel of products on the homepage.

- **Evidence**: `components/carousel.tsx` fetches from collection "hidden-homepage-carousel" and renders products in a flex container with `animate-carousel` CSS class. Products are duplicated three times to create a looping effect.
- **Classification**: Verified

**FR-003**: The system must allow users to browse products by collection through dedicated category pages.

- **Evidence**: `app/search/[collection]/page.tsx` renders products from the specified collection with sorting support. Collection metadata is generated for SEO purposes.
- **Classification**: Verified

**FR-004**: The system must allow users to search for products using a text search input.

- **Evidence**: `components/layout/navbar/search.tsx` provides a search form that submits to `/search` with a `q` query parameter. `app/search/page.tsx` retrieves the search query and passes it to `getProducts`.
- **Classification**: Verified

**FR-005**: The system must allow users to sort products by relevance, best-selling, latest arrivals, or price (ascending/descending).

- **Evidence**: `lib/constants.ts` defines the sorting options with sort keys: RELEVANCE, BEST_SELLING, CREATED_AT, and PRICE. Filter components in `components/layout/search/filter/` manage sort parameter persistence.
- **Classification**: Verified

**FR-006**: The system must display product detail pages containing images, descriptions, pricing, variant selection, and an add-to-cart interface.

- **Evidence**: `app/product/[handle]/page.tsx` renders the Gallery, ProductDescription, and RelatedProducts components. Product data is fetched via `getProduct`.
- **Classification**: Verified

**FR-007**: The system must generate JSON-LD structured data for products containing name, description, image, availability status, price currency, and price range.

- **Evidence**: `app/product/[handle]/page.tsx` defines `productJsonLd` with schema.org Product type, including AggregateOffer with availability, priceCurrency, highPrice, and lowPrice fields.
- **Classification**: Verified

**FR-008**: The system must display related product recommendations on product pages.

- **Evidence**: `app/product/[handle]/page.tsx` calls `getProductRecommendations(product.id)` and renders a horizontal scrollable list of recommended products.
- **Classification**: Verified

**FR-009**: The system must allow users to view custom CMS pages at the root path.

- **Evidence**: `app/[page]/page.tsx` fetches pages via `getPage(handle)` and renders their title, body content, and last updated date.
- **Classification**: Verified

### Shopping Cart Management

**FR-010**: The system must create a new cart when the cart modal opens if no cart exists.

- **Evidence**: `components/cart/modal.tsx` calls `createCartAndSetCookie()` in a useEffect when `cart` is undefined.
- **Classification**: Verified

**FR-011**: The system must store the cart identifier in a browser cookie named "cartId".

- **Evidence**: `components/cart/actions.ts` sets the cookie via `(await cookies()).set("cartId", cart.id!)`.
- **Classification**: Verified

**FR-012**: The system must allow users to add products to the cart via an Add to Cart button on product pages.

- **Evidence**: `components/cart/add-to-cart.tsx` binds the form action to `addItem` from `components/cart/actions.ts`, which calls the Shopify `addToCart` mutation.
- **Classification**: Verified

**FR-013**: The system must maintain item quantities in the cart and calculate subtotal, tax, and total amounts.

- **Evidence**: `components/cart/cart-context.tsx` implements `updateCartTotals` that reduces quantities and sums total amounts across cart lines.
- **Classification**: Verified

**FR-014**: The system must allow users to view cart contents in a slide-out modal dialog.

- **Evidence**: `components/cart/modal.tsx` implements a full-screen slide-out cart using Headless UI Dialog and Transition components.
- **Classification**: Verified

**FR-015**: The system must allow users to modify item quantities using plus and minus buttons.

- **Evidence**: `components/cart/edit-item-quantity-button.tsx` submits `updateItemQuantity` actions with incremented or decremented quantities.
- **Classification**: Verified

**FR-016**: The system must allow users to remove items from the cart.

- **Evidence**: `components/cart/delete-item-button.tsx` submits `removeItem` actions with the merchandise ID.
- **Classification**: Verified

**FR-017**: The system must display optimistic cart updates immediately when users add, remove, or update items.

- **Evidence**: `components/cart/cart-context.tsx` uses React's `useOptimistic` hook with a cart reducer to update the UI before server confirmation.
- **Classification**: Verified

**FR-018**: The system must redirect users to the Shopify checkout URL when they proceed to checkout.

- **Evidence**: `components/cart/actions.ts` implements `redirectToCheckout` that fetches the cart and calls `redirect(cart.checkoutUrl)`.
- **Classification**: Verified

**FR-019**: The system must display cart item thumbnails, product titles, variant option labels, quantities, and individual prices.

- **Evidence**: `components/cart/modal.tsx` renders each cart line with an image, product title, variant title (excluding "Default Title"), quantity, and total price via the Price component.
- **Classification**: Verified

### Product Variant Selection

**FR-020**: The system must display product variant options as selectable buttons on product pages.

- **Evidence**: `components/product/variant-selector.tsx` iterates through product options and renders each value as a button element.
- **Classification**: Verified

**FR-021**: The system must update the selected variant based on URL search parameters.

- **Evidence**: `components/product/variant-selector.tsx` reads search params and highlights the button matching the current option value. The variant is resolved by matching all selected options against variant `selectedOptions`.
- **Classification**: Verified

**FR-022**: The system must visually indicate and disable variant options that are not available for sale.

- **Evidence**: `components/product/variant-selector.tsx` computes `isAvailableForSale` by finding a variant matching all selected options and checking its `availableForSale` property. Unavailable options render with strikethrough styling and `disabled` attribute.
- **Classification**: Verified

**FR-023**: The system must display product images in a gallery with previous and next navigation controls.

- **Evidence**: `components/product/gallery.tsx` renders the current image with navigation buttons that update the displayed image index.
- **Classification**: Verified

**FR-024**: The system must persist the selected image index in URL search parameters.

- **Evidence**: `components/product/gallery.tsx` updates the "image" search param via `router.replace` when navigating between images.
- **Classification**: Verified

### Navigation and Layout

**FR-025**: The system must display a navigation bar containing logo, menu links, search input, and cart icon.

- **Evidence**: `components/layout/navbar/index.tsx` renders LogoSquare, navigation menu from Shopify, Search component, and CartModal.
- **Classification**: Verified

**FR-026**: The system must fetch navigation menu items from Shopify using the menu handle "next-js-frontend-header-menu".

- **Evidence**: `components/layout/navbar/index.tsx` calls `getMenu("next-js-frontend-header-menu")`. URLs are transformed from Shopify format (e.g., "/collections/") to the app's format (e.g., "/search/").
- **Classification**: Verified

**FR-027**: The system must fetch footer menu items from Shopify using the menu handle "next-js-frontend-footer-menu".

- **Evidence**: `components/layout/footer.tsx` calls `getMenu("next-js-frontend-footer-menu")` and renders links via FooterMenu component.
- **Classification**: Verified

**FR-028**: The system must display a mobile hamburger menu on small screens with navigation links and search.

- **Evidence**: `components/layout/navbar/mobile-menu.tsx` implements a full-screen mobile navigation overlay using Headless UI Dialog.
- **Classification**: Verified

**FR-029**: The system must close the mobile menu when the user navigates or when the viewport width exceeds the mobile breakpoint.

- **Evidence**: `components/layout/navbar/mobile-menu.tsx` calls `closeMobileMenu()` on link click and in a resize event handler when `window.innerWidth > 768`.
- **Classification**: Verified

### SEO and Metadata

**FR-030**: The system must generate a sitemap.xml containing routes, collections, products, and pages with last modified timestamps.

- **Evidence**: `app/sitemap.ts` fetches collections, products, and pages, then maps them to URLs with `lastModified` set to the entity's `updatedAt` field.
- **Classification**: Verified

**FR-031**: The system must generate a robots.txt file allowing all crawlers and referencing the sitemap URL.

- **Evidence**: `app/robots.ts` returns a robots configuration with wildcard user agent rules, sitemap reference, and host set to the base URL.
- **Classification**: Verified

**FR-032**: The system must generate OpenGraph metadata for social media sharing on product, collection, and page routes.

- **Evidence**: `app/product/[handle]/page.tsx` includes openGraph with images; `app/[page]/page.tsx` includes publishedTime and modifiedTime.
- **Classification**: Verified

**FR-033**: The system must generate page titles using a template format of "Page Title | Site Name".

- **Evidence**: `app/layout.tsx` defines metadata with `title: { default: SITE_NAME, template: \`%s | ${SITE_NAME}\` }`.
- **Classification**: Verified

**FR-034**: The system must exclude products tagged with "nextjs-frontend-hidden" from product listings and search results.

- **Evidence**: `lib/shopify/index.ts` implements `HIDDEN_PRODUCT_TAG = "nextjs-frontend-hidden"` and filters products with `filterHiddenProducts` in `reshapeProduct`.
- **Classification**: Verified

**FR-035**: The system must mark hidden products as noindex/nofollow in robots metadata.

- **Evidence**: `app/product/[handle]/page.tsx` sets `index: indexable` and `follow: indexable` where `indexable = !product.tags.includes(HIDDEN_PRODUCT_TAG)`.
- **Classification**: Verified

### User Notifications and Feedback

**FR-036**: The system must display a toast notification welcoming users on first visit.

- **Evidence**: `components/welcome-toast.tsx` shows a sonner toast with "Welcome to Next.js Commerce!" message on initial page load, gated by a "welcome-toast" cookie.
- **Classification**: Verified

**FR-037**: The system must display error messages when cart operations fail.

- **Evidence**: `components/cart/add-to-cart.tsx`, `delete-item-button.tsx`, and `edit-item-quantity-button.tsx` all render `<p aria-live="polite">` elements displaying server action messages.
- **Classification**: Verified

**FR-038**: The system must display a "Try Again" button in the error boundary UI.

- **Evidence**: `app/error.tsx` renders an error message with a button that invokes the `reset` function provided by Next.js error boundaries.
- **Classification**: Verified

## Business and Domain Rules

**DR-001**: Products tagged with "nextjs-frontend-hidden" must be excluded from all product listing operations.

- **Evidence**: `lib/shopify/index.ts` - `reshapeProduct` function checks `product.tags.includes(HIDDEN_PRODUCT_TAG)` and returns `undefined` when true.
- **Classification**: Verified

**DR-002**: Collections with handles starting with "hidden-" must be excluded from the collections navigation list.

- **Evidence**: `lib/shopify/index.ts` - `getCollections` filters collections with `.filter((collection) => !collection.handle.startsWith("hidden"))`.
- **Classification**: Verified

**DR-003**: The cart must default to USD currency when no items are present.

- **Evidence**: `components/cart/cart-context.tsx` - `createEmptyCart` sets `currencyCode: "USD"` for all money amounts. `updateCartTotals` uses `lines[0]?.cost.totalAmount.currencyCode ?? "USD"`.
- **Classification**: Verified

**DR-004**: The cart must default tax amount to zero until Shopify calculates it at checkout.

- **Evidence**: `lib/shopify/index.ts` - `reshapeCart` sets `totalTaxAmount: { amount: "0.0", ... }` when undefined. `components/cart/cart-context.tsx` initializes tax to "0".
- **Classification**: Verified

**DR-005**: Cart items with variant option value "Default Title" must not display the variant label.

- **Evidence**: `components/cart/modal.tsx` conditionally renders the variant title: `{item.merchandise.title !== DEFAULT_OPTION ? <p>{item.merchandise.title}</p> : null}`.
- **Classification**: Verified

**DR-006**: Cart items must be sorted alphabetically by product title when displayed in the cart modal.

- **Evidence**: `components/cart/modal.tsx` sorts lines: `.sort((a, b) => a.merchandise.product.title.localeCompare(b.merchandise.product.title))`.
- **Classification**: Verified

**DR-007**: The welcome toast must only display once per user session.

- **Evidence**: `components/welcome-toast.tsx` checks `document.cookie.includes("welcome-toast=2")` and sets a cookie with `max-age=31536000` on dismiss.
- **Classification**: Verified

## Interface Requirements

**IR-001**: The system must communicate with the Shopify Storefront GraphQL API using API version 2023-01.

- **Evidence**: `lib/constants.ts` defines `SHOPIFY_GRAPHQL_API_ENDPOINT = "/api/2023-01/graphql.json"`.
- **Classification**: Verified

**IR-002**: The system must authenticate GraphQL requests using the X-Shopify-Storefront-Access-Token header.

- **Evidence**: `lib/shopify/index.ts` - `shopifyFetch` sets header `"X-Shopify-Storefront-Access-Token": key`.
- **Classification**: Verified

**IR-003**: The system must provide a webhook revalidation endpoint at POST `/api/revalidate` accepting a secret query parameter.

- **Evidence**: `app/api/revalidate/route.ts` POST handler calls `revalidate(req)` which reads `secret` from `req.nextUrl.searchParams.get("secret")`.
- **Classification**: Verified

**IR-004**: The revalidation endpoint must reject requests where the secret does not match the SHOPIFY_REVALIDATION_SECRET environment variable.

- **Evidence**: `lib/shopify/index.ts` - `revalidate` returns `NextResponse.json({ status: 401 })` when `!secret || secret !== process.env.SHOPIFY_REVALIDATION_SECRET`.
- **Classification**: Verified

**IR-005**: The revalidation endpoint must revalidate the "collections" cache tag for collections/create, collections/delete, and collections/update webhook topics.

- **Evidence**: `lib/shopify/index.ts` - `revalidateTag(TAGS.collections, "seconds")` is called when `isCollectionUpdate` is true.
- **Classification**: Verified

**IR-006**: The revalidation endpoint must revalidate the "products" cache tag for products/create, products/delete, and products/update webhook topics.

- **Evidence**: `lib/shopify/index.ts` - `revalidateTag(TAGS.products, "seconds")` is called when `isProductUpdate` is true.
- **Classification**: Verified

## Data Requirements

**DataR-001**: The system must maintain Cart data with identifier, checkout URL, cost breakdown (subtotal, total, tax), line items, and total quantity.

- **Evidence**: `lib/shopify/types.ts` - `ShopifyCart` type and `lib/shopify/fragments/cart.ts` GraphQL fragment define all cart fields.
- **Classification**: Verified

**DataR-002**: The system must maintain Product data with identifier, handle, availability status, titles, descriptions, options, price range, variants, images, SEO metadata, tags, and update timestamp.

- **Evidence**: `lib/shopify/fragments/product.ts` GraphQL fragment and `lib/shopify/types.ts` - `ShopifyProduct` type define all product fields.
- **Classification**: Verified

**DataR-003**: The system must maintain Collection data with handle, title, description, SEO metadata, update timestamp, and application path.

- **Evidence**: `lib/shopify/types.ts` - `ShopifyCollection` type and `Collection` type (which adds `path`).
- **Classification**: Verified

**DataR-004**: The system must maintain Image data with URL, alt text, width, and height.

- **Evidence**: `lib/shopify/fragments/image.ts` GraphQL fragment defines all image fields.
- **Classification**: Verified

**DataR-005**: The system must maintain ProductOption data with identifier, name, and array of values.

- **Evidence**: `lib/shopify/types.ts` - `ProductOption` type: `{ id, name, values: string[] }`.
- **Classification**: Verified

**DataR-006**: The system must maintain ProductVariant data with identifier, title, availability status, selected options, and price.

- **Evidence**: `lib/shopify/types.ts` - `ProductVariant` type defines all variant fields.
- **Classification**: Verified

**DataR-007**: The system must maintain SEO data with title and description.

- **Evidence**: `lib/shopify/fragments/seo.ts` GraphQL fragment: `fragment seo on SEO { description, title }`.
- **Classification**: Verified

**DataR-008**: The system must maintain Menu data with title and path for navigation links.

- **Evidence**: `lib/shopify/types.ts` - `Menu` type: `{ title: string; path: string }`.
- **Classification**: Verified

**DataR-009**: The system must maintain Page data with identifier, title, handle, HTML body, summary, SEO metadata, and timestamps.

- **Evidence**: `lib/shopify/types.ts` - `Page` type defines all page fields.
- **Classification**: Verified

## Security Requirements

**SR-001**: The system must require SHOPIFY_STORE_DOMAIN environment variable to be configured before making API calls.

- **Evidence**: `lib/shopify/index.ts` throws `"SHOPIFY_STORE_DOMAIN environment variable is not set"` when `!endpoint`.
- **Classification**: Verified

**SR-002**: The system must require SHOPIFY_STOREFRONT_ACCESS_TOKEN environment variable for Storefront API authentication.

- **Evidence**: `lib/shopify/index.ts` uses `process.env.SHOPIFY_STOREFRONT_ACCESS_TOKEN!` as the authentication key.
- **Classification**: Verified

**SR-003**: The system must validate that SHOPIFY_STORE_DOMAIN does not contain bracket characters.

- **Evidence**: `lib/utils.ts` - `validateEnvironmentVariables` throws an error if the domain includes "[" or "]".
- **Classification**: Verified

**SR-004**: The system must store the cart identifier in an HTTP cookie.

- **Evidence**: `components/cart/actions.ts` uses Next.js `cookies().set()` API which creates an HTTP cookie.
- **Classification**: Verified (inferred from Next.js cookie behavior)

**SR-005**: The system must not expose Shopify credentials to client-side code.

- **Evidence**: `lib/shopify/index.ts` (server-side only) handles all Shopify