let stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
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
    let xhr = new XMLHttpRequest();
    let data = new FormData()
    data.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value)
    data.append('check-stock', 'check-stock')
    data.append('shipping-addr', document.querySelector("input[name='shipping-addr']").value)
    data.append('billing-addr', document.querySelector("input[name='billing-addr']").value)

    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let updatedSecret = $($.parseHTML(xhr.responseText)).filter("#id_client_secret").get(0).text
            let oldCart = $("#cart-detail").get(0)
            let updatedCart = $($.parseHTML(xhr.responseText)).find("#cart-detail").get(0)
            let oldCartStock = $("#checkout-stock-change").get(0)
            let updatedCartStock = $($.parseHTML(xhr.responseText)).find("#checkout-stock-change").get(0)
            let stockChange = $($.parseHTML(xhr.responseText)).find("input[name='js-stock']").get(0).value
            oldCart.replaceWith(updatedCart)
            oldCartStock.replaceWith(updatedCartStock)
            $('#id_client_secret').html(updatedSecret)
            document.querySelectorAll("input[name='js-stock']")[0].value = stockChange
            document.querySelectorAll("input[name='js-stock']")[1].value = stockChange
        }
    };
    xhr.open('POST', '/checkout', true);
    xhr.send(data);
    xhr.addEventListener('load', updateIntent)

    function updateIntent() {
        let clientSecret = $('#id_client_secret').text().slice(1, -1);
        card.update({'disabled': true})
        $('#payment-button').attr('disabled', true)
        try {
            stripe.retrieveSetupIntent(clientSecret)
                .then(function (result) {
                    if (result.setupIntent.description && result.setupIntent.description === "stock_change") {
                        let errorDiv = document.getElementById('card-errors')
                        let html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>Some item(s) in your cart have changed, due to stock updates. Please review your cart and make any necessary adjustments before checking out again.</span>`
                        $(errorDiv).html(html);
                        card.update({'disabled': false})
                        $('#payment-button').attr('disabled', false)
                    } else if (result.setupIntent.description && result.setupIntent.description === "empty_cart") {
                        let js_stock = document.querySelector("input[name='js-stock']").value
                        let json_stock = js_stock.replace(/&quot;/ig, '"')
                        let json_stock_change = JSON.parse(json_stock)
                        $.ajax({
                            method: "POST",
                            url: $('#empty-cart-form').attr('action'),
                            data: {
                                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                                'json_stock_change': json_stock_change
                            },
                            success: function () {
                                $('button.hidden-empty-submit').click()
                            }
                        })
                    }
                })
        } catch {
            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card
                }
            }).then(function (result) {
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
                } else if (result.paymentIntent.status === 'succeeded') {
                    stripeForm.submit()
                }
            })
        }
    }
})