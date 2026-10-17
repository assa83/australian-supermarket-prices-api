# Australian Supermarket Prices API – Woolworths & Coles

Get **Woolworths** and **Coles** grocery prices as clean JSON from Python, JavaScript or n8n: product search, category shelves, **specials** (half price, multibuy), **regular vs special price**, **unit price**, discount %, availability, barcode, images and nutrition. Build a **Woolworths vs Coles price comparison**, a price tracker or a specials alert in minutes.

Powered by two actors on Apify:
- [Woolworths AU Product Scraper](https://apify.com/lagenuina_agency/woolworths-scraper) (`lagenuina_agency/woolworths-scraper`)
- [Coles AU Product Scraper](https://apify.com/lagenuina_agency/coles-scraper) (`lagenuina_agency/coles-scraper`)

No browser, no login, no cookies to manage.

## Example output (real results, shortened)

```json
{
  "id": "6080386",
  "barcode": "9315090215700",
  "name": "MILKLAB Lactose Free Dairy Long Life Milk 1L",
  "brand": "MILKLAB",
  "price": 3.5,
  "discount_price": 3.1,
  "discount_percent": 11,
  "is_on_special": true,
  "unit_price": "$3.10 / 1L",
  "is_available": true,
  "source_url": "https://www.woolworths.com.au/shop/productdetails/6080386/milklab-lactose-free-dairy-long-life-milk"
}
```

```json
{
  "id": "3034279",
  "name": "Banana Flavoured Milk",
  "brand": "Big M",
  "size": "600mL",
  "price": 3.9,
  "discount_price": 3.45,
  "promotion": "save $0.45",
  "unit_price": 5.75,
  "unit": "L",
  "is_available": true,
  "source_url": "https://www.coles.com.au/product/big-m-banana-flavoured-milk-600ml-3034279"
}
```

`price` is always the regular price and `discount_price` the special price (or `null`), in AUD, for both supermarkets.

## Quickstart (3 steps)

1. Create a free Apify account and copy your API token from [Settings → Integrations](https://console.apify.com/settings/integrations).
2. Put it in an environment variable (never in code): `export APIFY_TOKEN=your_token`
3. Run the example:

```bash
pip install -r python/requirements.txt
python python/example.py "milk" "coffee beans" --limit 20
```

JavaScript: `cd js && npm install && node example.mjs`

## Examples

**Python** (`pip install "apify-client<2"`)

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("lagenuina_agency/coles-scraper").call(run_input={"operation": "specials", "special": "halfprice", "limit": 100})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item["name"], item["price"], "->", item["discount_price"])
```

**JavaScript / Node.js** (`npm install apify-client`)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor('lagenuina_agency/woolworths-scraper').call({ query: 'milk', searchTerms: ['bread'], limit: 50 });
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items);
```

**cURL / any language** – one HTTP call, results in the response:

```bash
curl -X POST "https://api.apify.com/v2/acts/lagenuina_agency~woolworths-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"operation": "specials", "categoryId": "dairy-eggs-fridge", "limit": 50}'
```

Both actors accept the same main fields: `operation` (`search`, `category`, `specials`, `item`, `categories`), `query`, `searchTerms`, `categoryId`, `productId`/`url`, `specialsOnly`, `limit`, `maxItems`. Coles adds `special` (`halfprice`, `multibuy`, `onlineonly`), `storeId` and `details` (barcode, nutrition); Woolworths adds `sortType` and `includeDetails`. All fields are documented on the actor pages (Input tab).

## Use case: Woolworths vs Coles price comparison to CSV / Google Sheets

`python/example.py` searches your keywords at both supermarkets and writes one row per product (`prices_<date>.csv`): store, product, brand, size, regular price, special price, discount %, unit price, availability and link. Run it daily (cron, GitHub Actions) to build a price history, or let the n8n workflow do it.

`js/example.mjs` lists this week's deepest discounts: Coles half-price specials and Woolworths pantry and drinks specials, sorted by discount.

## n8n workflow

[`n8n/workflow.json`](n8n/workflow.json): every day 07:00 → run Woolworths and Coles in parallel → merge → one row per product → append to Google Sheets.

1. In n8n: **Workflows → Import from File** and pick `n8n/workflow.json`.
2. Create a **Header Auth** credential named `Apify API token` with name `Authorization` and value `Bearer <your token>`, and select it in both *prices* nodes.
3. Edit the JSON body (your keywords), set your Google Sheet ID and activate.

The `run-sync-get-dataset-items` endpoint waits up to 300 s; for bigger runs use `/runs` plus a webhook.

## Use with AI agents (MCP)

Give Claude, ChatGPT, Cursor or any MCP client both supermarkets as tools:

```json
{
  "mcpServers": {
    "au-supermarkets": {
      "url": "https://mcp.apify.com/?actors=lagenuina_agency/woolworths-scraper,lagenuina_agency/coles-scraper"
    }
  }
}
```

Then ask *"Is milk cheaper per litre at Coles or Woolworths today?"* or *"What coffee is half price this week?"*. Sign in with Apify OAuth when asked, or send `Authorization: Bearer <APIFY_TOKEN>`.

## Pricing

Pay per product, platform usage included, no start fee:

| Apify plan | Woolworths, per 1,000 products | Coles, per 1,000 products |
|---|---|---|
| Free | $0.48 | $0.80 |
| Bronze | $0.40 | $0.72 |
| Silver | $0.32 | $0.64 |
| Gold, Platinum, Diamond | $0.24 | $0.56 |

Coles full product details (barcode, ingredients, nutrition) are optional: +$0.50 per 1,000 products. See the actor pages for details.

## Disclaimer

Independent, not affiliated with or endorsed by Woolworths Group or Coles Group. The actors read only publicly available product data, without login. Use them in line with the applicable terms and laws.

## License

[MIT](LICENSE) © Quelli di Carne Genuina
