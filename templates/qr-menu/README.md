# QR Menu template

One self-contained file: `index.html`. Customers scan the table QR code, browse the menu, order, track their order and call the waiter.

## Pages
- **Menu** (`#menu`): restaurant header, table number, search, sticky categories, "most ordered" row, products with photo, price and tags.
- **Product sheet**: description, prep time, options (size, milk, sugar, extras…), quantity, note for the kitchen.
- **Cart** (`#cart`): quantities, order note, payment method (cash / card), totals, send order.
- **Order tracking** (`#track`): live status Sent → Accepted → In the kitchen → Ready → Served, estimated time, timeline with times, items, quick waiter calls.
- **Waiter** (`#waiter`): call waiter, bill (cash / card), order is late, water, napkins, cutlery, ice, bread, salt & sauces, clean table, takeaway box, other (with note). Each request shows Sent → Seen → On the way → Done.

Languages: French, Arabic (RTL), English, Spanish, German, Dutch. Light and dark mode follow the phone.

Illustrations: 3D icons from Microsoft Fluent Emoji (MIT licence), embedded in the file. A product with an `img` URL shows that photo instead.

## Connecting it to the platform
Everything to change is at the top of the `<script>`:

1. `CONFIG` — restaurant name, logo, tagline, currency, service %, languages, default language.
   The table number comes from the QR link: `index.html?table=12`.
2. `MENU` — `categories`, `optionGroups`, `products`. Each text field is `{ fr, ar, en, es, de, nl }`; a missing language falls back to English. Product fields: `id, cat, price, prep (minutes), img (URL or null), tags ["popular","new","veg","spicy"], soldOut, options [groupIds]`.
   Or set `CONFIG.api.menu` to a URL that returns the same JSON.
3. `CONFIG.api` — endpoints. While they are `null` and `demo: true`, statuses advance by themselves (preview mode).
   - `placeOrder` POST → `{ id, number, eta? }`
   - `orderStatus` GET `…/{id}` → `{ status: "sent|accepted|preparing|ready|served|cancelled", eta? }` (polled every 10 s)
   - `waiterCall` POST → `{ id }`
   - `requestStatus` GET `…/{id}` → `{ status: "sent|seen|coming|done" }`
4. Push updates instead of polling (websocket, etc.):
   `QRMenu.updateOrderStatus(id, "preparing")`, `QRMenu.updateRequestStatus(id, "coming")`, `QRMenu.setMenu(data)`, `QRMenu.setConfig({...})`.
