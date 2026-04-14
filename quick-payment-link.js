/**
 * Szybkie tworzenie Payment Link dla "48 Tajemnic Manipulacji"
 * Pieniądze trafiają bezpośrednio na konto Stripe.
 * Uruchom: node quick-payment-link.js
 */

require('dotenv').config();
const Stripe = require('stripe');

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

async function main() {
  console.log('\n--- Tworzenie Payment Link ---\n');

  // 1. Produkt
  const product = await stripe.products.create({
    name: '48 Tajemnic Manipulacji — E-book',
    description:
      '48 praw manipulacji i wpływu społecznego. PDF od razu po zakupie.',
    metadata: { type: 'ebook' },
  });
  console.log('Produkt:', product.id);

  // 2. Cena (47 PLN)
  const price = await stripe.prices.create({
    product: product.id,
    unit_amount: 4700,   // 47.00 PLN w groszach
    currency: 'pln',
  });
  console.log('Cena:', price.id);

  // 3. Payment Link
  const link = await stripe.paymentLinks.create({
    line_items: [{ price: price.id, quantity: 1 }],
    after_completion: {
      type: 'redirect',
      redirect: {
        url: 'https://ericsonart.github.io/48-tajemnic-wladzy/sukces.html',
      },
    },
  });

  console.log('\n========================================');
  console.log('PAYMENT LINK:');
  console.log(link.url);
  console.log('========================================\n');
}

main().catch(err => {
  console.error('Błąd:', err.message);
  if (err.raw) console.error(err.raw);
  process.exit(1);
});
