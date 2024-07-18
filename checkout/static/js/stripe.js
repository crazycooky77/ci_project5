function generateCountryMap() {
  const countries = new Intl.DisplayNames(['en'], {type: 'region'})
  const countryMap = {}
  for (let i = 0; i < 26; i++) {
    for (let j = 0; j < 26; j++) {
      let code = String.fromCharCode(65 + i) + String.fromCharCode(65 + j)
      let name = countries.of(code)
      if (name !== code) {
        countryMap[name] = code
      }
    }
  }
  return countryMap
}


function stripeStyle() {
    if (window.innerWidth > 500) {
        return {
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
            },
        }
    }

    if (window.innerWidth <= 500) {
        return {
            base: {
                color: '#000',
                fontFamily: '"Montserrat", sans-serif',
                fontSize: '12px',
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
        }
    }
}

let stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
let stripe = Stripe(stripePublicKey);
let elements = stripe.elements();

let style = stripeStyle()
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
    data.append('shipping-addr', document.querySelector('input[name="shipping-addr"]').value)
    data.append('billing-addr', document.querySelector('input[name="billing-addr"]').value)

    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let updatedSecret = $($.parseHTML(xhr.responseText)).filter('#id_client_secret').get(0).text
            let oldCart = $('#cart-detail').get(0)
            let updatedCart = $($.parseHTML(xhr.responseText)).find('#cart-detail').get(0)
            let oldCartStock = $('#checkout-stock-change').get(0)
            let updatedCartStock = $($.parseHTML(xhr.responseText)).find('#checkout-stock-change').get(0)
            let stockChange = $($.parseHTML(xhr.responseText)).find('input[name="js-stock"]').get(0).value
            oldCart.replaceWith(updatedCart)
            oldCartStock.replaceWith(updatedCartStock)
            $('#id_client_secret').html(updatedSecret)
            document.querySelectorAll('input[name="js-stock"]')[0].value = stockChange
            document.querySelectorAll('input[name="js-stock"]')[1].value = stockChange
            document.querySelector('input[name="client-secret"]').value = updatedSecret
        }
    };
    xhr.open('POST', '/checkout', true);
    xhr.send(data);
    xhr.addEventListener('load', updateIntent)

    function updateIntent() {
        let clientSecret = $('#id_client_secret').text().slice(1, -1);
        card.update({'disabled': true})
        $('#payment-button').attr('disabled', true)
        document.getElementById('pay-process').style.display = 'unset'
        try {
            stripe.retrieveSetupIntent(clientSecret)
                .then(function (result) {
                    if (result.setupIntent.description && result.setupIntent.description === 'stock_change') {
                        let errorDiv = document.getElementById('card-errors')
                        let html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>Some item(s) in your cart have changed, due to stock updates. Please review your cart and make any necessary adjustments before checking out again.</span>`
                        $(errorDiv).html(html);
                        document.getElementById('pay-process').style.display = 'none'
                        card.update({'disabled': false})
                        $('#payment-button').attr('disabled', false)
                    } else if (result.setupIntent.description && result.setupIntent.description === 'empty_cart') {
                        let js_stock = document.querySelector('input[name="js-stock"]').value
                        let json_stock = js_stock.replace(/&quot;/ig, '"')
                        let json_stock_change = JSON.parse(json_stock)
                        $.ajax({
                            method: 'POST',
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
            let ship_value = document.querySelector('input[name="shipping-addr"]').value
            let ship_addr = ship_value.replace(/'/g, '"')
            let ship_addr_json = JSON.parse(ship_addr)
            let bill_value = document.querySelector('input[name="billing-addr"]').value
            let bill_addr = bill_value.replace(/'/g, '"')
            let bill_addr_json = JSON.parse(bill_addr)
            let countries = generateCountryMap()
            let postData = {
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'client_secret': clientSecret,
                'order_note': $('#checkout-order-note').val(),
                'ship_first_name': ship_addr_json['first_name'],
                'bill_first_name': bill_addr_json['first_name'],
                'ship_last_name': ship_addr_json['last_name'],
                'bill_last_name': bill_addr_json['last_name'],
                'ship_addr_line3': ship_addr_json['addr_line3'],
                'bill_addr_line3': bill_addr_json['addr_line3']
            }
            if (document.querySelectorAll('.cart-totals').length === 3) {
                let subtotal = document.querySelectorAll('.cart-totals')[0].lastElementChild.textContent.split(' ')[1]
                let shipping = document.querySelectorAll('.cart-totals')[1].lastElementChild.textContent.split(' ')[1]
                let total = document.querySelectorAll('.cart-totals')[2].lastElementChild.textContent.split(' ')[1]
                postData['subtotal'] = subtotal
                postData['shipping'] = shipping
                postData['grand_total'] = total
            }
            else {
                let total = document.querySelectorAll('.cart-totals')[1].lastElementChild.textContent.split(' ')[1]
                postData['subtotal'] = total
                postData['shipping'] = 0
                postData['grand_total'] = total
            }
            let url = '/checkout/cache_checkout_data/'
            $.post(url, postData).done(function() {
                stripe.confirmCardPayment(clientSecret, {
                    payment_method: {
                        card: card,
                        billing_details: {
                            name: $.trim(bill_addr_json['first_name']) + ' ' + $.trim(bill_addr_json['last_name']),
                            phone: $.trim(bill_addr_json['phone_nr']),
                            email: $.trim(bill_addr_json['email']),
                            address: {
                                line1: $.trim(bill_addr_json['addr_line1']),
                                line2: $.trim(bill_addr_json['addr_line2']),
                                city: $.trim(bill_addr_json['city']),
                                country: $.trim(countries[bill_addr_json['country']]),
                                state: $.trim(bill_addr_json['county'])
                            }
                        }
                    },
                    shipping: {
                        name: $.trim(ship_addr_json['first_name']) + ' ' + $.trim(ship_addr_json['last_name']),
                        phone: $.trim(ship_addr_json['phone_nr']),
                        address: {
                            line1: $.trim(ship_addr_json['addr_line1']),
                            line2: $.trim(ship_addr_json['addr_line2']),
                            city: $.trim(ship_addr_json['city']),
                            country: $.trim(countries[ship_addr_json['country']]),
                            postal_code: $.trim(ship_addr_json['eir_code']),
                            state: $.trim(ship_addr_json['county'])
                        }
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
                        document.getElementById('pay-process').style.display = 'none'
                        card.update({'disabled': false})
                        $('#payment-button').attr('disabled', false)
                    } else if (result.paymentIntent.status === 'succeeded') {
                        stripeForm.submit()
                    }
                })
            }).fail(function() {
                location.reload()
            })
        }
    }
})