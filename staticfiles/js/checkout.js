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
                e.value = '0' + a.fields.phone_nr
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


function shipAddrSelection(select) {
    let shipForm = document.getElementsByClassName('shipping-addr-form')[0]
    addressSelection(select, shipForm)
}


function billAddrSelection(select) {
    let billForm = document.getElementsByClassName('billing-addr-form')[0]
    addressSelection(select, billForm)
}


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


function checkoutEditAddr() {
    let shippingAddr = document.querySelector('input[name="shipping-addr"]').value
    let billingAddr = document.querySelector('input[name="billing-addr"]').value

    $.ajax({
        method: "POST",
        url: $('button.hidden-submit').attr('formaction'),
        data: {'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'checkout-edit-addr': 'checkout-edit-addr',
            'billing-addr': billingAddr,
            'shipping-addr': shippingAddr},
        success: function() {
            $('button.hidden-submit').click()
        }
    })
}


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


if (window.location.pathname === "/checkout") {
    $(document).ready(function() {
        resizeCheckoutFields()
        window.onresize = function() {
            resizeCheckoutFields()
        }
    })
}