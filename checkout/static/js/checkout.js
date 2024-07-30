// Run all necessary functions once page content has loaded
window.addEventListener('DOMContentLoaded', () => {
    initAddrSel();
    checkoutU800();
    checkoutO800();
});


// Run all necessary functions once page content has loaded
window.addEventListener('load', () => {
    checkoutSizing();
});


// Run all necessary functions when page width is resized
window.addEventListener('resize', () => {
    let curWidth = window.innerWidth;
    if (curWidth !== prvWidth) {
        checkoutSizing();
        checkoutU800();
        checkoutO800();
    }
});


// Set checkout address dropdown selection to index 0
function removeAddrSel(select) {
    select.options[select.options.selectedIndex].removeAttribute('selected');
    select.options.selectedIndex = 0;
    select.options[0].setAttribute('selected', true);
}


// Function to update selected dropdown option once user starts changing any autofilled address fields
if (window.location.pathname === '/checkout' && document.getElementById('shipping-addr-list')) {
    let addrForm = document.getElementsByClassName('checkout-addr')[0];
    let shipSelect = document.getElementById('shipping-addr-list');
    let billSelect = document.getElementById('billing-addr-list');
    addrForm.addEventListener('input', (e) => {
        if (e.target.localName === 'input') {
            if (e.target.parentElement.parentElement.className === 'shipping-addr-form' &&
                shipSelect.options.selectedIndex !== 0) {
                removeAddrSel(shipSelect);
            }
            else if (e.target.parentElement.parentElement.className === 'billing-addr-form' &&
                billSelect.options.selectedIndex !== 0) {
                removeAddrSel(billSelect);
            }
        }
    });
}


// Get selected address and fill out the corresponding checkout address form fields
function addressSelection(select, addrForm) {
    let selectedAddr = select.options[select.options.selectedIndex];
    selectedAddr.setAttribute('selected', true);
    if (select.options.selectedIndex !== 0) {
        let selectedAddrId = Number(selectedAddr.value.split('-')[0]);
        addrForm.querySelectorAll('input').forEach(
            e => json_addr.forEach(
                a => {
                    if (selectedAddrId) {
                        if (a.pk === selectedAddrId) {
                            if (e.name.slice(5) === 'first_name')
                                e.value = a.fields.first_name;
                            else if (e.name.slice(5) === 'last_name')
                                e.value = a.fields.last_name;
                            else if (e.name.slice(5) === 'phone_nr')
                                e.value = a.fields.phone_nr;
                            else if (e.name.slice(5) === 'addr_line1')
                                e.value = a.fields.addr_line1;
                            else if (e.name.slice(5) === 'addr_line2')
                                e.value = a.fields.addr_line2;
                            else if (e.name.slice(5) === 'addr_line3')
                                e.value = a.fields.addr_line3;
                            else if (e.name.slice(5) === 'city')
                                e.value = a.fields.city;
                            else if (e.name.slice(5) === 'eir_code')
                                e.value = a.fields.eir_code;
                            else if (e.name.slice(5) === 'county')
                                e.value = a.fields.county;
                        }
                    }
                }
            )
        );
    }
}


// Run the address selection function for address form fields
function selectAddr(addrList, addrForm) {
    let select = document.getElementById(addrList);
    let form = document.getElementsByClassName(addrForm)[0];
    for (let i = 0; i < select.options.length; i++) {
        if (select.options[i].getAttribute('selected')) {
            select.options[i].removeAttribute('selected');
        }
    }
    addressSelection(select, form);
}


// Run address selection functions (for initial page load)
function initAddrSel() {
    if (window.location.pathname === '/checkout' && document.getElementById('shipping-addr-list')) {
        if (sessionStorage['ajax-post'] !== undefined) {
            sessionStorage.removeItem('ajax-post');
            let shipSelect = document.getElementById('shipping-addr-list');
            let billSelect = document.getElementById('billing-addr-list');
            removeAddrSel(shipSelect);
            removeAddrSel(billSelect);
        } else {
            selectAddr('shipping-addr-list', 'shipping-addr-form');
            selectAddr('billing-addr-list', 'billing-addr-form');
        }
    }
}


// Function to empty inputs from checkout address form
function emptyAddr(value, formClass) {
    if (value === 'New Address') {
        let form = document.getElementsByClassName(formClass)[0];
        form.querySelectorAll('input').forEach(
            i => {
                i.value = '';
            }
        );
    }
}


// Function for users to show/hide cart contents on checkout pages
function toggleCart() {
    let cartTable = document.getElementsByClassName('cart-tbl-prod');
    for (let i = 0; i < cartTable.length; i++) {
        if (window.getComputedStyle(cartTable[i]).display === 'none') {
            cartTable[i].style.display = 'table-row';
        }
        else {
            cartTable[i].style.display = 'none';
        }
    }
}


// Function to POST address and order data when a user is at the checkout confirmation page and wants to Edit Address
function checkoutEditAddr() {
    let shippingAddr = document.querySelector('input[name="shipping-addr"]').value;
    let billingAddr = document.querySelector('input[name="billing-addr"]').value;
    let checkoutNote = $('#checkout-order-note').val();
    document.querySelector('input[name="checkout-order-note"]').value = checkoutNote;

    $.ajax({
        method: 'POST',
        url: $('#checkout-edit-addr').attr('action'),
        data: {'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'checkout-edit-addr': 'checkout-edit-addr',
            'billing-addr': billingAddr,
            'shipping-addr': shippingAddr,
            'checkout-order-note': checkoutNote},
        success: function() {
            sessionStorage.setItem('ajax-post', 'editAddr');
            $('button.hidden-addr-submit').click();
        }
    });
}


// Function to autofill the billing address with the shipping address details
function addrMatch() {
    let shipForm = document.getElementsByClassName('shipping-addr-form')[0];
    let billForm = document.getElementsByClassName('billing-addr-form')[0];
    let shipSelect = document.getElementById('shipping-addr-list');
    let billSelect = document.getElementById('billing-addr-list');
    shipForm.querySelectorAll('input').forEach(
        sInput => billForm.querySelectorAll('input').forEach(
            bInput => {
                if (sInput.id.slice(7) === bInput.id.slice(7))
                    bInput.value = sInput.value;
            }
        )
    );
    if (shipSelect) {
        let shipSelectIndex = shipSelect.options.selectedIndex;
        billSelect.options[billSelect.options.selectedIndex].removeAttribute('selected');
        billSelect.options.selectedIndex = shipSelectIndex;
        billSelect.options[shipSelectIndex].setAttribute('selected', true);
    }
}


// Function to resize checkout address input fields for consistency
function resizeCheckoutFields() {
    let formInputs = document.getElementsByClassName('stripe-input');
    if (formInputs.length > 0) {
        let mainWidth = $(formInputs[0].parentElement).outerWidth();
        let astWidth = window.getComputedStyle(formInputs[0].parentElement, '::after').width.split('px', 1)[0];
        let widthDelta = mainWidth - (astWidth * 2);

        for (let i = 0; i < formInputs.length; i++) {
            $(formInputs[i]).outerWidth(widthDelta);
        }
    }
}


// For screens up to 800px width, replace cart headers with icons
function checkoutU800() {
    if (window.innerWidth <= 800) {
        if (window.location.pathname === '/checkout' || window.location.pathname === '/checkout/success') {
            let headers = document.querySelectorAll('th');
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].title === 'Product') {
                    headers[i].innerHTML = '<i class="fa-solid fa-bottle-water" title="Product"></i>';
                } else if (headers[i].title === 'Size') {
                    headers[i].innerHTML = '<i class="fa-solid fa-weight-scale" title="Size"></i>';
                } else if (headers[i].title === 'Quantity') {
                    headers[i].innerHTML = '<i class="fa-solid fa-arrow-up-9-1" title="Quantity"></i>';
                } else if (headers[i].title === 'Sum') {
                    headers[i].innerHTML = '<i class="fa-solid fa-sack-dollar" title="Sum"></i>';
                }
            }
        }
    }
}


// For screens above 800px width, replace icons with cart headers
function checkoutO800() {
    if (window.innerWidth > 800) {
        if (window.location.pathname === '/checkout' || window.location.pathname === '/checkout/success') {
            let headers = document.querySelectorAll('th');
            for (let i = 0; i < headers.length; i++) {
                headers[i].innerHTML = headers[i].title;
            }
        }
    }
}


// Run the function to make checkout field sizes consistent on the checkout page
function checkoutSizing() {
    if (window.location.pathname === '/checkout') {
        resizeCheckoutFields();
    }
}