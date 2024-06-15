/* Function to sort json data by product flavours */
function jsonSort(json) {
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


function sortFlavours(flavour) {
    if (flavour !== null) {
        let jqFlavour = "#" + flavour.id
        let options = $(jqFlavour + " option")

        options.sort(function (a, b) {
            if (a.text.toUpperCase() > b.text.toUpperCase()) return 1;
            else if (a.text.toUpperCase() < b.text.toUpperCase()) return -1;
            else return 0;
        });

        $(jqFlavour).empty().append(options);

        return document.getElementById(flavour.id);
    }
    else {
        return flavour
    }
}


/* Get current selections */
function currentSelections(prodId) {
    let selectedSize = $("#" + prodId + "-prod-sizes :selected").val()
    let selectedFlavour = $("#" + prodId + "-prod-flavours :selected").val()

    return [selectedSize, selectedFlavour]
}


/* Get main elements for functions */
function initVars(prodId) {
    let prodFlavour = document.getElementById(prodId + "-prod-flavours");
    let price = document.getElementById(prodId + "-prod-price");
    let quantity = document.getElementById(prodId + "-prod-quantity");
    let size = document.getElementById(prodId + "-prod-sizes");
    let cart = document.getElementById(prodId + "-prod-cart");

    let sortedProdFlavour = sortFlavours(prodFlavour)

    return [sortedProdFlavour, price, quantity, size, cart]
}


/* Check for and hide duplicate sizes */
function dupeSizes(idSize) {
    let dupeSizes = {};
    $("select[name=" + idSize + "] > option").each(function () {
        if (dupeSizes[this.text]) {
            $(this).hide();
            $(this).addClass('hidden')
        } else {
            dupeSizes[this.text] = this.value;
        }
    })
}


/* Function to check for duplicate flavours and hide the duplicates */
function flavourMatch(flavour, i) {
    let flavourCheck = flavour.innerText.match(new RegExp(flavour[i].value, 'g'))
    if (flavourCheck.length > 1) {
        if (flavour[i].disabled === true) {
            flavour.options[i].style.display = "none"
            flavour.options[i].classList.add('hidden')
            flavour.options[i].classList.remove('oos')
            flavour.options[i].removeAttribute('selected')
            flavour[i].disabled = false
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
function oosProducts(flavour, size, json) {
    if (flavour) {
        jsonProdSorted = jsonSort(json)
        for (let i = 0; i < jsonProdSorted.length; i++) {
            let obj = jsonProdSorted[i]
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
        flavourSelect(flavour, jsonProdSorted)
    }
}


/* Function to show the prices and availability for selected products */
function prodAvailability(json, price, quantity, psize, cart, stock) {
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
            cart.style.justifyContent = 'center'
        }
    }
}


/* Function accompanying prodAvailability */
function availabilityScenarios(json, ssize, pflavour, sflavour, price, quantity, psize, cart, stock) {
    for (let i = 0; i < json.length; i++) {
        if ((json[i].fields.size === Number(ssize) && pflavour === null) ||
            (json[i].fields.size === Number(ssize) && json[i].fields.flavour === sflavour) ||
            (ssize === undefined)) {
            prodAvailability(json[i], price, quantity, psize, cart, stock)
        }
    }
}


/* Function to dynamically set the height for products in lists */
function prodElSizes(prodClass) {
    let prodList = document.getElementsByClassName(prodClass)
    for (let i = 0; i < prodList.length; i++) {
        if (typeof prodList[i] === 'object') {
            if (i !== 0 && prodList[i].clientWidth > prodList[i - 1].clientWidth) {
                prodList[i].parentElement.style.width = prodList[i - 1].clientWidth + 'px'
                prodList[i].parentElement.style.flex = '0 0 auto'
            }

            if (i !== 0 && prodList[i].getBoundingClientRect().top === prodList[i - 1].getBoundingClientRect().top) {
                if (prodList[i].clientHeight < prodList[i - 1].clientHeight) {
                    prodList[i].style.height = prodList[i - 1].clientHeight + 'px'
                }
                else if (prodList[i].clientHeight > prodList[i - 1].clientHeight) {
                    prodList[i - 1].style.height = prodList[i].clientHeight + 'px'
                    for (let x = 0; x < prodList.length; x++) {
                        if (typeof prodList[x] === 'object') {
                            if (prodList[i].getBoundingClientRect().top === prodList[x].getBoundingClientRect().top) {
                                prodList[x].style.height = prodList[i].clientHeight + 'px'
                            }
                        }
                    }
                }

                if (prodList[i].children[1].innerText === 'Out Of Stock') {
                    prodList[i].children[1].style.height = prodList[i - 1].children[1].getBoundingClientRect().height + 'px'
                }
            }
        }
    }
}


function multiProd(json) {
    // Remove duplicate sizes in linked products
    let sizeIds = []
    for (let i = 0; i < json.length; i++) {
        let sizeId = json[i].fields.product
        if (!(sizeIds.includes(sizeId))) {
            sizeIds.push(sizeId)
            let sizeElement = sizeId + "-prod-sizes"
            dupeSizes(sizeElement)
        }
    }

    let multiJson = {}
    json.forEach(function(splitJson) {
        let pid = splitJson.fields.product;

        if (!multiJson[pid]) {
            multiJson[pid] = []
        }
        multiJson[pid].push(splitJson)
    })

    // Disable/enable product flavours, based on stock, for products
    for (let j in multiJson) {
        let prodFlavour = document.getElementById(multiJson[j][0].fields.product + "-prod-flavours");
        let sortedProdFlavour = sortFlavours(prodFlavour)
        let selectedSize = $("#" + multiJson[j][0].fields.product + "-prod-sizes :selected").val()
        // Disable/enable products in dropdowns according to stock
        oosProducts(sortedProdFlavour, selectedSize, multiJson[j])
    }

    for (let j in multiJson) {
        let [selectedSize,selectedFlavour] = currentSelections(multiJson[j][0].fields.product)
        let [prodFlavour, price, quantity, size, cart] = initVars(multiJson[j][0].fields.product)
        availabilityScenarios(multiJson[j], selectedSize, prodFlavour,
            selectedFlavour, price, quantity, size, cart)
    }
}


/* When selecting other dropdown options on the homepage, check for stock and disable out of stock options */
function featOptions() {
    dupeSizes(json_new_prod[0].fields.product + '-prod-sizes')
    dupeSizes(json_sports_prod[0].fields.product + '-prod-sizes')
    dupeSizes(json_health_prod[0].fields.product + '-prod-sizes')

    let [newFlavour, newPrice, newQuantity, newSize, newCart] = initVars(json_new_prod[0].fields.product)
    let [sportsFlavour, sportsPrice, sportsQuantity, sportsSize, sportsCart] = initVars(json_sports_prod[0].fields.product)
    let [healthFlavour, healthPrice, healthQuantity, healthSize, healthCart] = initVars(json_health_prod[0].fields.product)

    var [newSelectedSize, newSelectedFlavour] = currentSelections(json_new_prod[0].fields.product)
    var [sportsSelectedSize, sportsSelectedFlavour] = currentSelections(json_sports_prod[0].fields.product)
    var [healthSelectedSize, healthSelectedFlavour] = currentSelections(json_health_prod[0].fields.product)

    oosProducts(newFlavour, newSelectedSize,json_new_prod)
    oosProducts(sportsFlavour, sportsSelectedSize,json_sports_prod)
    oosProducts(healthFlavour, healthSelectedSize,json_health_prod)

    var [newSelectedSize, newSelectedFlavour] = currentSelections(json_new_prod[0].fields.product)
    var [sportsSelectedSize, sportsSelectedFlavour] = currentSelections(json_sports_prod[0].fields.product)
    var [healthSelectedSize, healthSelectedFlavour] = currentSelections(json_health_prod[0].fields.product)

    availabilityScenarios(json_new_prod, newSelectedSize, newFlavour,
        newSelectedFlavour, newPrice, newQuantity, newSize, newCart)
    availabilityScenarios(json_sports_prod, sportsSelectedSize, sportsFlavour,
        sportsSelectedFlavour, sportsPrice, sportsQuantity, sportsSize, sportsCart)
    availabilityScenarios(json_health_prod, healthSelectedSize, healthFlavour,
        healthSelectedFlavour, healthPrice, healthQuantity, healthSize, healthCart)
}


/* When changing product dropdown options, disable out of stock flavours */
function productOptions() {
    /* For the main product on the page */
    dupeSizes('prod-sizes')

    let prodFlavour = document.getElementById("prod-flavours");
    let sortedProdFlavour = sortFlavours(prodFlavour)
    var selectedSize = $("#prod-sizes :selected").val()
    oosProducts(prodFlavour, selectedSize, json_prod)

    var selectedSize = $("#prod-sizes :selected").val()
    let selectedFlavour = $("#prod-flavours :selected").val()
    let prodPrice = document.getElementById("prod-price");
    let prodQuantity = document.getElementById("prod-quantity");
    let prodSize = document.getElementById("prod-sizes");
    let prodCart = document.getElementById("prod-cart");
    let prodStock = document.getElementById("prod-stock");
    availabilityScenarios(json_prod, selectedSize, sortedProdFlavour, selectedFlavour, prodPrice, prodQuantity, prodSize, prodCart, prodStock)
}


/* For linked products, when changing product dropdown options, disable out of stock flavours */
function linkedOptions() {
    multiProd(json_linked_prods)
    prodElSizes('linked-details')
}


/* When changing product dropdown options, disable out of stock flavours */
function allOptions() {
    multiProd(json_prods)
    prodElSizes('all-prod-details')
}


/* When changing product dropdown options, disable out of stock flavours */
function sportsOptions() {
    multiProd(json_sports_prods)
    prodElSizes('all-prod-details')
}


/* When changing product dropdown options, disable out of stock flavours */
function healthOptions() {
    multiProd(json_health_prods)
    prodElSizes('all-prod-details')
}


/* When changing product dropdown options, disable out of stock flavours */
function newOptions() {
    multiProd(json_new_prods)
    prodElSizes('all-prod-details')
}


/* On homepage load, disable the product dropdown options for out of stock products */
if (window.location.pathname === "/") {
    $(document).ready(function () {
        featOptions()
    })
}


/* On product page load, hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname.split('=')[0] === '/products/id') {
    $(document).ready(function () {
        productOptions()
        linkedOptions()
    })
}


/* On all product page load, hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname === "/products/all") {
    $(document).ready(function () {
        allOptions()
    })
}


/* On sports product page load, hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname === "/products/sports") {
    $(document).ready(function () {
        sportsOptions()
    })
}


/* On health product page load, hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname === "/products/health") {
    $(document).ready(function () {
        healthOptions()
    })
}


/* On new product page load, hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname === "/products/new") {
    $(document).ready(function () {
        newOptions()
    })
}
