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
    console.log($("select[name=id_size]"))
    $("select[name=" + id_size + "] > option").each(function () {
        console.log($(this))
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
    for (let prod = 0; prod < Object.entries(prod_count).length; prod++) {
        if (Object.entries(prod_count)[prod][1] < 2) {
            for (let i = 0; i < json_linked_prods.length; i++) {
                if (json_linked_prods[i] !== undefined &&
                    Number(json_linked_prods[i].fields.product) === Number(Object.entries(prod_count)[prod][0])) {
                    delete json_linked_prods[i]
                }
            }
        }
    }

    // Update the json object to reset the indexes and object length
    let js_i = 0;
    for (let index in json_linked_prods) {
        json_linked_prods[js_i] = json_linked_prods[index]
        js_i++
    }
    json_linked_prods.length = js_i;

    // Get the unique product IDs for linked products that have multiple flavours
    let prod_ids = []
    for (let entry in json_linked_prods) {
        if (!(prod_ids.includes(json_linked_prods[entry].fields.product))) {
            prod_ids.push(json_linked_prods[entry].fields.product)
        }
    }

    // Disable/enable product flavours, based on stock, for linked products
    for (let id in prod_ids) {
        let linkedProdFlavour = document.getElementById(prod_ids[id] + "-prod-flavours");
        let linkedSelectedSize = $("#" + prod_ids[id] + "-prod-sizes :selected").val()
        // Disable/enable products in dropdowns according to stock
        oos_products(linkedProdFlavour, linkedSelectedSize, json_linked_prods)
    }
}


/* On homepage load, disable the product dropdown options for out of stock products */
if (window.location.pathname === "/") {
    $(document).ready(function () {
        let newFlavour = document.getElementById("new-prod-flavours");
        let newSelectedSize = $("#new-prod-sizes :selected").val().slice(0, -2);
        let sportsFlavour = document.getElementById("sports-prod-flavours");
        let sportsSelectedSize = $("#sports-prod-sizes :selected").val().slice(0, -2);
        let healthFlavour = document.getElementById("health-prod-flavours");
        let healthSelectedSize = $("#health-prod-sizes :selected").val().slice(0, -2);

        oos_products(newFlavour,newSelectedSize,json_new_prod)
        oos_products(sportsFlavour,sportsSelectedSize,json_sports_prod)
        oos_products(healthFlavour,healthSelectedSize,json_health_prod)
    })
}


/* When selecting other dropdown options on the homepage, check for stock and disable out of stock options */
function featOptions() {
    let newFlavour = document.getElementById("new-prod-flavours");
    let newSelectedSize = $("#new-prod-sizes :selected").val().slice(0, -2);
    let sportsFlavour = document.getElementById("sports-prod-flavours");
    let sportsSelectedSize = $("#sports-prod-sizes :selected").val().slice(0, -2);
    let healthFlavour = document.getElementById("health-prod-flavours");
    let healthSelectedSize = $("#health-prod-sizes :selected").val().slice(0, -2);

    oos_products(newFlavour,newSelectedSize,json_new_prod)
    oos_products(sportsFlavour,sportsSelectedSize,json_sports_prod)
    oos_products(healthFlavour,healthSelectedSize,json_health_prod)
}


/* On product page load, hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname.indexOf("/products/") !== -1) {
    $(document).ready(function () {
        /* For the main product on the page */
        let prodFlavour = document.getElementById("prod-flavours");
        let selectedSize = $("#prod-sizes :selected").val()
        dupe_sizes('prod-sizes')
        oos_products(prodFlavour,selectedSize,json_prod)

        /* For linked products */
        linked_prod_options()
    })
}


/* When changing product dropdown options, disable out of stock flavours */
function productOptions() {
    let prodFlavour = document.getElementById("prod-flavours");
    let selectedSize = $("#prod-sizes :selected").val()
    oos_products(prodFlavour,selectedSize,json_prod)
}


/* For linked products, when changing product dropdown options, disable out of stock flavours */
function linkedOptions() {
    linked_prod_options()
}
