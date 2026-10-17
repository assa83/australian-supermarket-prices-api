// This week's half-price specials at Coles and the deepest discounts at Woolworths.
// Usage: node example.mjs
import { ApifyClient } from 'apify-client';

const token = process.env.APIFY_TOKEN;
if (!token) {
    console.error('Set APIFY_TOKEN first: https://console.apify.com/settings/integrations');
    process.exit(1);
}

const client = new ApifyClient({ token });
const [coles, woolies] = await Promise.all([
    client.actor('lagenuina_agency/coles-scraper').call({ operation: 'specials', special: 'halfprice', limit: 50 }),
    client.actor('lagenuina_agency/woolworths-scraper').call({ operation: 'specials', categoryIds: ['pantry', 'drinks'], limit: 50 }),
]);
for (const [store, run] of [['Coles', coles], ['Woolworths', woolies]]) {
    const { items } = await client.dataset(run.defaultDatasetId).listItems();
    items.sort((a, b) => b.discount_percent - a.discount_percent);
    console.log(`\n${store}: ${items.length} specials`);
    for (const it of items.slice(0, 10)) console.log(`  -${it.discount_percent}%  $${it.discount_price ?? it.current_price} (was $${it.price})  ${it.full_name ?? it.name}`);
}
