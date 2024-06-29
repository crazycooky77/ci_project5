let stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
let client_secret = $('#id_client_secret').text().slice(1, -1);
let stripe = Stripe(stripe_public_key);
let elements = stripe.elements();

let style = {
    base: {
        color: '#000',
        fontFamily: '"Montserrat", sans-serif',
        fontSize: '18px',
        backgroundColor: '#9FFFB8',
        fontSmoothing: 'antialiased',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: 'red',
        iconColor: 'red'
    }
};
let card = elements.create('card', {style: style});
card.mount('#card-element');