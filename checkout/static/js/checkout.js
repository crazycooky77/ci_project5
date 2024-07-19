// Run all necessary functions once DOM has loaded
window.addEventListener('DOMContentLoaded', () => {
    checkoutSizing()
    checkoutU800()
    checkoutO800()
})

// Run all necessary functions once page content has loaded
window.addEventListener('load', () => {
    checkoutSizing()
    checkoutU800()
    checkoutO800()
})

// Run all necessary functions when page is resized
window.addEventListener('resize', () => {
    checkoutSizing()
    checkoutU800()
    checkoutO800()
})


// Get selected address and fill out the corresponding checkout address form fields
function addressSelection(select, addrForm) {
    let selectedAddr = select.options[select.options.selectedIndex]
    let selectedAddrId = Number(selectedAddr.value.split('-')[0])
    addrForm.querySelectorAll('input').forEach(
    e => json_addr.forEach(
        a =>  { if (a.pk === selectedAddrId) {
            if (e.name === 'first_name')
                e.value = a.fields.first_name
            else if (e.name === 'last_name')
                e.value = a.fields.last_name
            else if (e.name === 'phone_nr')
                e.value = a.fields.phone_nr
            else if (e.name === 'addr_line1')
                e.value = a.fields.addr_line1
            else if (e.name === 'addr_line2')
                e.value = a.fields.addr_line2
            else if (e.name === 'addr_line3')
                e.value = a.fields.addr_line3
            else if (e.name === 'city')
                e.value = a.fields.city
            else if (e.name === 'eir_code')
                e.value = a.fields.eir_code
            else if (e.name === 'county')
                e.value = a.fields.county
        }})
    )
}


// Run the address selection function for the shipping address form fields
function shipAddrSelection(select) {
    let shipForm = document.getElementsByClassName('shipping-addr-form')[0]
    addressSelection(select, shipForm)
}


// Run the address selection function for the billing address form fields
function billAddrSelection(select) {
    let billForm = document.getElementsByClassName('billing-addr-form')[0]
    addressSelection(select, billForm)
}


// Function for users to show/hide cart contents on checkout pages
function toggleCart() {
    let cartTable = document.getElementsByClassName('cart-tbl-prod')
    for (let i = 0; i < cartTable.length; i++) {
        if (window.getComputedStyle(cartTable[i]).display === 'none') {
            cartTable[i].style.display = 'table-row'
        }
        else {
            cartTable[i].style.display = 'none'
        }
    }
}


// Function to POST address and order data when a user is at the checkout confirmation page and wants to Edit Address
function checkoutEditAddr() {
    let shippingAddr = document.querySelector('input[name="shipping-addr"]').value
    let billingAddr = document.querySelector('input[name="billing-addr"]').value
    let checkoutNote = $('#checkout-order-note').val()
    document.querySelector('input[name="checkout-order-note"]').value = checkoutNote

    $.ajax({
        method: 'POST',
        url: $('button.hidden-addr-submit').attr('formaction'),
        data: {'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'checkout-edit-addr': 'checkout-edit-addr',
            'billing-addr': billingAddr,
            'shipping-addr': shippingAddr,
            'checkout-order-note': checkoutNote},
        success: function() {
            $('button.hidden-addr-submit').click()
        }
    })
}


// Function to autofill the billing address with the shipping address details
function addrMatch() {
    let shipForm = document.getElementsByClassName('shipping-addr-form')[0]
    let billForm = document.getElementsByClassName('billing-addr-form')[0]
    shipForm.querySelectorAll('input').forEach(
        sInput => billForm.querySelectorAll('input').forEach(
            bInput =>
            { if (sInput.id === bInput.id)
                bInput.value = sInput.value
            }
        )
    )
}


// Function to resize checkout address input fields for consistency
function resizeCheckoutFields() {
    let formInputs = document.getElementsByClassName('stripe-input')
    if (formInputs.length > 0) {
        let mainWidth = $(formInputs[0].parentElement).outerWidth()
        let astWidth = window.getComputedStyle(formInputs[0].parentElement, '::after').width.split('px', 1)[0]
        let widthDelta = mainWidth - (astWidth * 2)

        for (let i = 0; i < formInputs.length; i++) {
            $(formInputs[i]).outerWidth(widthDelta)
        }
    }
}


// For screens up to 800px width, replace cart headers with icons
function checkoutU800() {
    if (window.innerWidth <= 800) {
        if (window.location.pathname === '/checkout' || window.location.pathname === '/checkout/success') {
            let headers = document.querySelectorAll('th')
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].title === 'Product') {
                    headers[i].innerHTML = '<i class="fa-solid fa-bottle-water"></i>'
                } else if (headers[i].title === 'Size') {
                    headers[i].innerHTML = '<i class="fa-solid fa-weight-scale"></i>'
                } else if (headers[i].title === 'Quantity') {
                    headers[i].innerHTML = '<i class="fa-solid fa-arrow-up-9-1"></i>'
                } else if (headers[i].title === 'Sum') {
                    headers[i].innerHTML = '<i class="fa-solid fa-sack-dollar"></i>'
                }
            }
        }
    }
}


// For screens above 800px width, replace icons with cart headers
function checkoutO800() {
    if (window.innerWidth > 800) {
        if (window.location.pathname === '/checkout' || window.location.pathname === '/checkout/success') {
            let headers = document.querySelectorAll('th')
            for (let i = 0; i < headers.length; i++) {
                headers[i].innerHTML = headers[i].title
            }
        }
    }
}


// Run the function to make checkout field sizes consistent on the checkout page
function checkoutSizing() {
    if (window.location.pathname === '/checkout') {
        resizeCheckoutFields()
    }
}