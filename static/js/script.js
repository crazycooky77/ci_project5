/* Function to sort json data by product flavours */
function json_sort(json) {
    json.sort((a, b) => {
        const aValue = JSON.stringify(Object.values(a.fields.flavour).sort());
        const bValue = JSON.stringify(Object.values(b.fields.flavour).sort());
        if (aValue < bValue)
            return -1;
        if (aValue > bValue)
            return 1;
        return 0;
    })
    return json
}


/* Check for and hide duplicate sizes */
function dupe_sizes(id_size) {
    let dupeSizes = {};
    $("select[name=" + id_size + "] > option").each(function () {
        if (dupeSizes[this.text]) {
            $(this).hide();
            $(this).addClass('hidden')
        } else {
            dupeSizes[this.text] = this.value;
        }
    })
}


/* Function to check for duplicate flavours and hide the duplicates */
function flavourMatch(prodFlavour, i) {
    let flavourCheck = prodFlavour.innerText.match(new RegExp(prodFlavour[i].value, 'g'))
    if (flavourCheck.length > 1) {
        if (prodFlavour[i].disabled === true) {
            prodFlavour.options[i].style.display = "none"
            prodFlavour.options[i].classList.add('hidden')
            prodFlavour.options[i].classList.remove('oos')
            prodFlavour.options[i].removeAttribute('selected')
            prodFlavour[i].disabled = false
        }
    }
}


/* Function to select the first eligible flavour if none is selected */
function flavourSelect(flavour, json) {
    if (flavour.selectedIndex === -1) {
        for (let i = 0; i < json.length; i++) {
            if (!($(flavour.options[i]).hasClass('hidden')) &&
                !($(flavour.options[i]).hasClass('oos'))) {
                flavour.selectedIndex = i
                flavour.options[i].setAttribute('selected', true)
                break
            }
        }
    }
}


/* Function to check for out of stock flavours and disable the dropdown options */
function oos_products(flavour,size,json) {

            // if (size.options.selectedIndex !== -1) {
            //     size.options[flavour.options.selectedIndex].setAttribute('selected', true)
            // }
    if (flavour) {
        json_prod_sorted = json_sort(json)
        for (let i = 0; i < json_prod_sorted.length; i++) {
            let obj = json_prod_sorted[i]
            if (flavour.options.selectedIndex !== -1) {
                flavour.options[flavour.options.selectedIndex].setAttribute('selected', true)
            }
            if (Number(size) === obj.fields.size) {
                if (flavour[i].value !== obj.fields.flavour) {
                    flavour.options[i].disabled = true
                    flavour.options[i].classList.add('oos')
                    flavour.options[i].removeAttribute('selected')
                    if (flavour.selectedIndex === i) {
                        flavour.selectedIndex = -1
                    }
                } else {
                    flavour.options[i].disabled = false
                    flavour.options[i].classList.remove('hidden')
                    flavour.options[i].classList.remove('oos')
                    flavour.options[i].style.display = 'unset'
                    if (flavour.selectedIndex === -1) {
                        flavour.options[i].setAttribute('selected', true)
                    }
                    else {
                        flavour.options[flavour.selectedIndex].setAttribute('selected', true)
                    }
                    if (i !== flavour.selectedIndex) {
                        flavour.options[i].removeAttribute('selected')
                    }
                }
            }
            else {
                flavour.options[i].disabled = true
                flavour.options[i].classList.add('oos')
                flavour.options[i].removeAttribute('selected')
                if (flavour.selectedIndex === i) {
                    flavour.selectedIndex = -1
                }
            }

            // Hide duplicate flavour options
            flavourMatch(flavour, i)
        }
        // If no option is selected, select the first eligible option
        flavourSelect(flavour, json_prod_sorted)
    }
}


/* Function to show the prices and availability for selected products */
function prod_availability(json, price, quantity, psize, cart, stock) {
    if (stock !== undefined) {
        if (json.fields.stock_count > 0) {
            price.textContent = "Price: € " + json.fields.price
            quantity.setAttribute('max', json.fields.stock_count)
            stock.textContent = "Availability: In Stock"
        } else {
            psize.parentElement.style.display = 'none'
            cart.style.display = 'none'
            stock.textContent = "Availability: Out Of Stock"
        }
    }
    else {
        if (json.fields.stock_count > 0) {
            price.textContent = "€ " + json.fields.price
            quantity.setAttribute('max', json.fields.stock_count)
        } else {
            psize.parentElement.style.display = 'none'
            cart.textContent = "Out Of Stock"
        }
    }
}


/* Function accompanying prod_availability */
function availability_scenarios(json, ssize, pflavour, sflavour, price, quantity, psize, cart, stock) {
    if (json.length !== undefined) {
        for (let i = 0; i < json.length; i++) {
            if ((json[i].fields.size === Number(ssize) && pflavour === null) ||
                (json[i].fields.size === Number(ssize) && json[i].fields.flavour === sflavour) ||
                (ssize === undefined)) {
                prod_availability(json[i], price, quantity, psize, cart, stock)
            }
        }
    }
    else {
        if ((json.fields.size === Number(ssize) && pflavour === null) ||
            (json.fields.size === Number(ssize) && json.fields.flavour === sflavour) ||
            (ssize === undefined)) {
            prod_availability(json, price, quantity, psize, cart)
        }
    }
}


function linked_prod_options() {
    // Remove duplicate sizes in linked products
    let sizeIds = []
    for (let i = 0; i < json_linked_prods.length; i++) {
        let sizeId = json_linked_prods[i].fields.product
        if (!(sizeIds.includes(sizeId))) {
            sizeIds.push(sizeId)
            let sizeElement = sizeId + "-prod-sizes"
            dupe_sizes(sizeElement)
        }
    }

    // Get occurrences for products
    let prod_count = {}
    for (let i = 0; i < json_linked_prods.length; i++) {
        if (json_linked_prods[i]) {
            prod_id = json_linked_prods[i].fields.product
            prod_count[prod_id] = (prod_count[prod_id] + 1) || 1
        }
    }

    // For each product with <2 counts, delete them from the json
    let custom_json = JSON.parse(JSON.stringify(json_linked_prods))
    for (let prod = 0; prod < Object.entries(prod_count).length; prod++) {
        if (Object.entries(prod_count)[prod][1] < 2) {
            for (let i = 0; i < custom_json.length; i++) {
                if (custom_json[i] !== undefined &&
                    Number(custom_json[i].fields.product) === Number(Object.entries(prod_count)[prod][0])) {
                    delete custom_json[i]
                }
            }
        }
    }

    // Update the json object to reset the indexes and object length
    let js_i = 0;
    for (let index in custom_json) {
        custom_json[js_i] = custom_json[index]
        js_i++
    }
    custom_json.length = js_i;

    // Get the unique product IDs for linked products that have multiple flavours
    let prod_ids = []
    for (let entry in custom_json) {
        if (!(prod_ids.includes(custom_json[entry].fields.product))) {
            prod_ids.push(custom_json[entry].fields.product)
        }
    }

    // Disable/enable product flavours, based on stock, for linked products
    for (let id in prod_ids) {
        let linkedProdFlavour = document.getElementById(prod_ids[id] + "-prod-flavours");
        let linkedSelectedSize = $("#" + prod_ids[id] + "-prod-sizes :selected").val()
        // Disable/enable products in dropdowns according to stock
        oos_products(linkedProdFlavour, linkedSelectedSize, custom_json)
    }

    for (let i = 0; i < json_linked_prods.length; i++) {
        let prodId = json_linked_prods[i].fields.product
        let linkedFlavour = document.getElementById(prodId + "-prod-flavours");
        let linkedSelectedSize = $("#" + prodId + "-prod-sizes :selected").val()
        let linkedSelectedFlavour = $("#" + prodId + "-prod-flavours :selected").val()
        let linkedPrice = document.getElementById(prodId + "-prod-price");
        let linkedQuantity = document.getElementById(prodId + "-prod-quantity");
        let linkedSize = document.getElementById(prodId + "-prod-sizes");
        let linkedCart = document.getElementById(prodId + "-prod-cart");
        availability_scenarios(json_linked_prods[i], linkedSelectedSize, linkedFlavour,
            linkedSelectedFlavour, linkedPrice, linkedQuantity, linkedSize, linkedCart)
    }
}


/* On homepage load, disable the product dropdown options for out of stock products */
if (window.location.pathname === "/") {
    $(document).ready(function () {
        let newFlavour = document.getElementById("new-prod-flavours");
        let newSelectedSize = $("#new-prod-sizes :selected").val();
        let sportsFlavour = document.getElementById("sports-prod-flavours");
        let sportsSelectedSize = $("#sports-prod-sizes :selected").val();
        let healthFlavour = document.getElementById("health-prod-flavours");
        let healthSelectedSize = $("#health-prod-sizes :selected").val();

        dupe_sizes('new-prod-sizes')
        dupe_sizes('sports-prod-sizes')
        dupe_sizes('health-prod-sizes')
        oos_products(newFlavour,newSelectedSize,json_new_prod)
        oos_products(sportsFlavour,sportsSelectedSize,json_sports_prod)
        oos_products(healthFlavour,healthSelectedSize,json_health_prod)

        let newSelectedFlavour = $("#new-prod-flavours :selected").val()
        let newProdPrice = document.getElementById("new-prod-price");
        let newProdQuantity = document.getElementById("new-prod-quantity");
        let newProdSize = document.getElementById("new-prod-sizes");
        let newProdCart = document.getElementById("new-prod-cart");
        let sportsSelectedFlavour = $("#sports-prod-flavours :selected").val()
        let sportsProdPrice = document.getElementById("sports-prod-price");
        let sportsProdQuantity = document.getElementById("sports-prod-quantity");
        let sportsProdSize = document.getElementById("sports-prod-sizes");
        let sportsProdCart = document.getElementById("sports-prod-cart");
        let healthSelectedFlavour = $("#health-prod-flavours :selected").val()
        let healthProdPrice = document.getElementById("health-prod-price");
        let healthProdQuantity = document.getElementById("health-prod-quantity");
        let healthProdSize = document.getElementById("health-prod-sizes");
        let healthProdCart = document.getElementById("health-prod-cart");

        availability_scenarios(json_new_prod, newSelectedSize, newFlavour, newSelectedFlavour,
            newProdPrice, newProdQuantity, newProdSize, newProdCart)
        availability_scenarios(json_sports_prod, sportsSelectedSize, sportsFlavour, sportsSelectedFlavour,
            sportsProdPrice, sportsProdQuantity, sportsProdSize, sportsProdCart)
        availability_scenarios(json_health_prod, healthSelectedSize, healthFlavour, healthSelectedFlavour,
            healthProdPrice, healthProdQuantity, healthProdSize, healthProdCart)
    })
}


/* When selecting other dropdown options on the homepage, check for stock and disable out of stock options */
function featOptions() {
    let newFlavour = document.getElementById("new-prod-flavours");
    let newSelectedSize = $("#new-prod-sizes :selected").val();
    let sportsFlavour = document.getElementById("sports-prod-flavours");
    let sportsSelectedSize = $("#sports-prod-sizes :selected").val();
    let healthFlavour = document.getElementById("health-prod-flavours");
    let healthSelectedSize = $("#health-prod-sizes :selected").val();

    oos_products(newFlavour,newSelectedSize,json_new_prod)
    oos_products(sportsFlavour,sportsSelectedSize,json_sports_prod)
    oos_products(healthFlavour,healthSelectedSize,json_health_prod)

    let newSelectedFlavour = $("#new-prod-flavours :selected").val()
    let newProdPrice = document.getElementById("new-prod-price");
    let newProdQuantity = document.getElementById("new-prod-quantity");
    let newProdSize = document.getElementById("new-prod-sizes");
    let newProdCart = document.getElementById("new-prod-cart");
    let sportsSelectedFlavour = $("#sports-prod-flavours :selected").val()
    let sportsProdPrice = document.getElementById("sports-prod-price");
    let sportsProdQuantity = document.getElementById("sports-prod-quantity");
    let sportsProdSize = document.getElementById("sports-prod-sizes");
    let sportsProdCart = document.getElementById("sports-prod-cart");
    let healthSelectedFlavour = $("#health-prod-flavours :selected").val()
    let healthProdPrice = document.getElementById("health-prod-price");
    let healthProdQuantity = document.getElementById("health-prod-quantity");
    let healthProdSize = document.getElementById("health-prod-sizes");
    let healthProdCart = document.getElementById("health-prod-cart");

    availability_scenarios(json_new_prod, newSelectedSize, newFlavour, newSelectedFlavour,
        newProdPrice, newProdQuantity, newProdSize, newProdCart)
    availability_scenarios(json_sports_prod, sportsSelectedSize, sportsFlavour, sportsSelectedFlavour,
        sportsProdPrice, sportsProdQuantity, sportsProdSize, sportsProdCart)
    availability_scenarios(json_health_prod, healthSelectedSize, healthFlavour, healthSelectedFlavour,
        healthProdPrice, healthProdQuantity, healthProdSize, healthProdCart)
}


/* On product page load, hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname.indexOf("/products/") !== -1) {
    $(document).ready(function () {
        /* For the main product on the page */
        let prodFlavour = document.getElementById("prod-flavours");
        let selectedSize = $("#prod-sizes :selected").val()
        dupe_sizes('prod-sizes')
        oos_products(prodFlavour,selectedSize,json_prod)

        let selectedFlavour = $("#prod-flavours :selected").val()
        let prodPrice = document.getElementById("prod-price");
        let prodQuantity = document.getElementById("prod-quantity");
        let prodSize = document.getElementById("prod-sizes");
        let prodCart = document.getElementById("prod-cart");
        let prodStock = document.getElementById("prod-stock");
        availability_scenarios(json_prod, selectedSize, prodFlavour, selectedFlavour, prodPrice, prodQuantity, prodSize, prodCart, prodStock)

        /* For linked products */
        linked_prod_options()
    })
}


/* When changing product dropdown options, disable out of stock flavours */
function productOptions() {
    let prodFlavour = document.getElementById("prod-flavours");
    let selectedSize = $("#prod-sizes :selected").val()
    oos_products(prodFlavour,selectedSize,json_prod)

    let selectedFlavour = $("#prod-flavours :selected").val()
    let prodPrice = document.getElementById("prod-price");
    let prodQuantity = document.getElementById("prod-quantity");
    let prodSize = document.getElementById("prod-sizes");
    let prodCart = document.getElementById("prod-cart");
    let prodStock = document.getElementById("prod-stock");
    availability_scenarios(json_prod, selectedSize, prodFlavour, selectedFlavour, prodPrice, prodQuantity, prodSize, prodCart, prodStock)
}


/* For linked products, when changing product dropdown options, disable out of stock flavours */
function linkedOptions() {
    linked_prod_options()
}
