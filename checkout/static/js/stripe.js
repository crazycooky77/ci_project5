let stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
let clientSecret = $('#id_client_secret').text().slice(1, -1);
let stripe = Stripe(stripePublicKey);
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


card.addEventListener('change', function(event) {
    let errorDiv = document.getElementById('card-errors');
    if (event.error) {
        let html = `
        <span class="icon" role="alert">
            <i class="fas fa-times"></i>
        </span>
        <span>${event.error.message}</span>`
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});


let stripeForm = document.getElementById('payment-form')

stripeForm.addEventListener('submit', function(ev) {
    ev.preventDefault()
    card.update({'disabled': true})
    $('#payment-button').attr('disabled', true)
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card
        }
    }).then(function(result) {
        if (result.error) {
            let errorDiv = document.getElementById('card-errors')
            let html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`
            $(errorDiv).html(html);
            card.update({'disabled': false})
            $('#payment-button').attr('disabled', false)
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                stripeForm.submit()
            }
        }
    })
})