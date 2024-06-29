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
                    for (let x = 0; x < i; x++) {
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


/* Function to reposition dynamic sort window dropdown */
function sortDD(sortForm) {
    let buttonPosition = sortForm.children[1].getBoundingClientRect().bottom
    let sortWindow = document.getElementsByClassName("sort-dd")[0]
    let sortPosition = sortWindow.getBoundingClientRect().top

    if (sortPosition && !(sortPosition === buttonPosition + 10)) {
        sortWindow.style.top = buttonPosition + 'px'
    }
}


function sortScroll() {
    let sortForm = document.getElementById('sort-form')
    $(document).scroll(function() {
        sortDD(sortForm)
    })
}


function sortProds() {
    let prodSort = document.getElementsByClassName("prod-sort")[0]
    let sortOpts = document.getElementsByClassName("sort-dd")[0]
    let sortStyle = window.getComputedStyle(sortOpts).getPropertyValue("display")
    let sortForm = document.getElementById('sort-form')

    if (sortStyle === "none") {
        sortOpts.style.display = "flex"
        sortDD(sortForm)
    }
    else {
        sortOpts.style.display = "none"
    }

    document.body.addEventListener('click', function (e) {
        if (!(sortOpts.contains(e.target)) && !(prodSort).contains(e.target)) {
            sortOpts.style.display = "none"
        }
    })
}


function searchSelection(json) {
    if (json.length > 0) {
        json.sort(function(a, b) {
            return a.fields.product - b.fields.product
        })
        for (let prod in json) {
            if (Number(prod) === 0 ||
                (Number(prod) > 0 && json[prod].fields.product !== json[prod - 1].fields.product)) {
                let prodId = json[prod].fields.product
                let prodFlavours = document.getElementById(prodId + '-prod-flavours')
                if (prodFlavours.options.length > 1) {
                    for (let i = 0; i < prodFlavours.options.length; i++) {
                        if ((!($(prodFlavours.options[i]).hasClass('hidden'))) &&
                            (json[prod].fields.flavour === prodFlavours.options[i].value) &&
                            (json[prod].fields.stock_count > 0) &&
                            (prodFlavours.options[i].selected !== true)) {
                            let prodSizes = document.getElementById(prodId + '-prod-sizes')
                            for (let j = 0; j < prodSizes.options.length; j++) {
                                if (Number(json[prod].fields.size) === Number(prodSizes.options[j].value)) {
                                    prodFlavours.options[i].setAttribute('selected', true)
                                    prodFlavours.options[i].selectedIndex = i
                                    prodSizes.options[j].setAttribute('selected', true)
                                    prodSizes.options[j].selectedIndex = j
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


function removeClasses(json) {
    for (let i = 0; i < json.length; i++) {
        let prodId = json[i].fields.product
        let flavours = document.getElementById(prodId + '-prod-flavours')
        let sizes = document.getElementById(prodId + '-prod-sizes')
        $($(sizes)[0].options).removeClass()
        if (flavours) {
            $($(flavours)[0].options).removeClass()
        }
    }
}


function sortFlavours(json) {
    for (let i = 0; i < json.length; i++) {
        let prodId = json[i].fields.product
        if (json[i].fields.flavour !== null) {
            let flavours = "#" + prodId + '-prod-flavours'
            let options = $(flavours + " option")

            options.sort(function (a, b) {
                if (a.text.toUpperCase() > b.text.toUpperCase()) return 1;
                else if (a.text.toUpperCase() < b.text.toUpperCase()) return -1;
                else return 0;
            });

            $(flavours).empty().append(options);
        }
    }
}


function SizeSelect(sizes) {
    for (let s = 0; s < sizes.length; s++) {
        if (sizes.selectedIndex === -1) {
            if (!($(sizes.options[s]).hasClass('hidden')) &&
                !($(sizes.options[s]).hasClass('oos'))) {
                sizes.selectedIndex = s
                sizes.options[s].setAttribute('selected', true)
            }
        } else {
            sizes.options[sizes.selectedIndex].setAttribute('selected', true)
        }
    }
}


function flavourSelect(json) {
    if (window.location.pathname !== "/products/search") {
        for (let i = 0; i < json.length; i++) {
            let flavours = document.getElementById(json[i].fields.product + '-prod-flavours')
            let selectedSize = $("#" + json[i].fields.product + "-prod-sizes :selected").val()
            if (flavours) {
                for (let f = 0; f < flavours.length; f++) {
                    flavours.options[f].removeAttribute('selected')
                    if (json[i].fields.flavour === flavours.options[f].value &&
                        Number(json[i].fields.size) === Number(selectedSize)) {
                        if (flavours.selectedIndex === -1) {
                            if (!($(flavours.options[f]).hasClass('hidden')) &&
                                !($(flavours.options[f]).hasClass('oos')) &&
                                !($(flavours.options[f]).hasClass('na')) &&
                                flavours.options[f].disabled === false) {
                                $(flavours.options[f]).removeClass()
                                flavours.selectedIndex = f
                                flavours.options[f].classList.add('stock')
                                flavours.options[f].setAttribute('selected', true)
                            }
                            else if ($(flavours.options[f]).hasClass('hidden')) {
                                $(flavours.options[f]).removeClass()
                                flavours.options[f].disabled = false
                                flavours.selectedIndex = f
                                flavours.options[f].classList.add('stock')
                                flavours.options[f].setAttribute('selected', true)
                            }
                        }
                        else if (flavours.selectedIndex !== -1 &&
                            flavours.options[flavours.selectedIndex].disabled === false) {
                            flavours.options[flavours.selectedIndex].setAttribute('selected', true)
                        }
                    }
                    else if (flavours.selectedIndex !== -1 &&
                        flavours.options[flavours.selectedIndex].disabled === true) {
                        flavours.selectedIndex = -1
                    }
                }
            }
        }
    }
}


function oosFlavours(flavours, obj) {
    let selectedSize = $("#" + obj.fields.product + "-prod-sizes :selected").val()
    for (let f = 0; f < flavours.length; f++) {
        if (Number(obj.fields.size) === Number(selectedSize)) {
            if (flavours.options[f].value === obj.fields.flavour &&
                obj.fields.stock_count === 0) {
                flavours.options[f].disabled = true
                flavours.options[f].classList.add('oos')
                flavours.options[f].removeAttribute('selected')
                if (flavours.selectedIndex === f) {
                    flavours.selectedIndex = -1
                }
            } else if (flavours.options[f].value === obj.fields.flavour &&
                obj.fields.stock_count > 0) {
                flavours.options[f].disabled = false
                flavours.options[f].classList.add('stock')
                if (flavours.selectedIndex === -1 || flavours.options[flavours.selectedIndex].disabled) {
                    flavours.selectedIndex = f
                    flavours.options[f].setAttribute('selected', true)
                }
            }
        }
    }
}


function oosProducts(json) {
    for (let i = 0; i < json.length; i++) {
        let obj = json[i]
        let sizes = document.getElementById(obj.fields.product + "-prod-sizes")
        let flavours = document.getElementById(obj.fields.product + "-prod-flavours")

        for (let s = 0; s < sizes.length; s++) {
            if (Number(obj.fields.size) === Number(sizes.options[s].value) &&
                (obj.fields.flavour === null || (flavours && flavours.options[s].value === obj.fields.flavour))) {
                if (obj.fields.stock_count === 0) {
                    sizes.options[s].disabled = true
                    sizes.options[s].classList.add('oos')
                    sizes.options[s].removeAttribute('selected')
                    if (sizes.selectedIndex === s) {
                        sizes.selectedIndex = -1
                    }
                }
            }
        }
        SizeSelect(sizes)
        if (flavours) {
            oosFlavours(flavours, obj)
        }
    }
    for (let i = 0; i < json.length; i++) {
        let obj = json[i]
        let flavours = document.getElementById(obj.fields.product + "-prod-flavours")
        if (flavours) {
            for (let f = 0; f < flavours.length; f++) {
                if (flavours.options[f].classList.length === 0) {
                    flavours.options[f].disabled = true
                    flavours.options[f].classList.add('na')
                    flavours.options[f].removeAttribute('selected')
                    if (flavours.selectedIndex === f) {
                        flavours.selectedIndex = -1
                    }
                }
            }
        }
    }
    flavourSelect(json)
}


function prodDetails(json) {
    for (let i = 0; i < json.length; i++) {
        let obj = json[i]
        let selectedFlavour = $("#" + obj.fields.product + "-prod-flavours :selected").val()
        let selectedSize = $("#" + obj.fields.product + "-prod-sizes :selected").val()
        let flavours = document.getElementById(obj.fields.product + "-prod-flavours");
        let sizes = document.getElementById(obj.fields.product + "-prod-sizes");
        let price = document.getElementById(obj.fields.product + "-prod-price");
        let quantity = document.getElementById(obj.fields.product + "-prod-quantity");
        let cart = document.getElementById(obj.fields.product + "-prod-cart");
        let stock = document.getElementById(obj.fields.product + "-prod-stock");


        if (obj.fields.stock_count > 0 &&
            (obj.fields.flavour === null || obj.fields.flavour === selectedFlavour) &&
            Number(obj.fields.size) === Number(selectedSize)) {
            price.textContent = "€ " + obj.fields.price
            quantity.setAttribute('max', obj.fields.stock_count)
            if (stock !== null) {
                stock.textContent = "Availability: In Stock"
            }
        }
        let disabledOpts = 0;
        for (let s = 0; s < sizes.length; s++) {
            if (sizes.options[s].disabled) {
                disabledOpts++
            }
        }
        if (sizes.length === disabledOpts) {
            if (stock !== null) {
                sizes.parentElement.style.display = 'none'
                cart.style.display = 'none'
                stock.textContent = "Availability: Out Of Stock"
            }
            else {
                sizes.parentElement.style.display = 'none'
                cart.textContent = "Out Of Stock"
                cart.style.justifyContent = 'center'
                if (flavours) {
                    flavours.parentElement.style.display = 'none'
                }
            }
        }
    }
}


function dupeOpts(json, option) {
    for (let i = 0; i < json.length; i++) {
        let fieldId = json[i].fields.product + "-prod-" + option
        let dupeOpts = {};
        $("select[name=" + fieldId + "] > option").each(function () {
            if (dupeOpts[this.text]) {
                $(this).hide();
                $(this).addClass('hidden')
                $(this).removeClass('oos')
                $(this).removeClass('stock')
                $(this).removeClass('na')
                $(this).prop('disabled', false)
            } else {
                dupeOpts[this.text] = this.value;
            }

            if (($(this).prop('selected')) && ($(this).hasClass('hidden'))) {
                let selectedOpt = $(this).prop('innerText')
                $("select[name=" + fieldId + "] > option").each(function () {
                    if ((!($(this).prop('selected'))) &&
                        (!($(this).hasClass('hidden'))) &&
                        ($(this).prop('innerText') === selectedOpt)) {

                        $(this).prop('selectedIndex', $(this).prop('index'))
                        $(this).prop('selected', true)
                    }
                })
                $(this).removeAttr('selected')
                $(this).prop('selectedIndex', -1)
            }
        })
    }
}


function prodFunctions(json) {
    removeClasses(json)
    sortFlavours(json)
    oosProducts(json)
    dupeOpts(json, 'flavours')
    dupeOpts(json, 'sizes')
    prodDetails(json)
}


function multiProd(json) {
    // Check if any products are visible on the page
    let noResults = document.getElementsByClassName('prod-oos')
    if (noResults.length > 0) {
        // Center content for no results
        let prodPage = document.getElementsByClassName('all-prod-page')[0]
        prodPage.style.marginLeft = 'auto'
    }
    else {
        prodFunctions(json)
    }
}


function featOptions() {
    prodFunctions(json_new_prod)
    prodFunctions(json_sports_prod)
    prodFunctions(json_health_prod)
}


function productOptions() {
    prodFunctions(json_prod)
}


function linkedOptions() {
    if (typeof json_linked_prods !== 'undefined') {
        multiProd(json_linked_prods)
        prodElSizes('linked-details')
    }
}


function allOptions() {
    multiProd(json_prods)
    prodElSizes('all-prod-details')
}


/* On homepage load, disable the product dropdown options for out of stock products */
if (window.location.pathname === "/") {
    $(document).ready(function () {
        featOptions()
        sortScroll()
    })
}


/* On product page load, hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname.split('=')[0] === '/products/id') {
    $(document).ready(function () {
        productOptions()
        linkedOptions()
        window.onresize = function() {
            prodElSizes('linked-details')
        }
    })
}


/* When certain product pages load, hide duplicate and out of stock flavours in dropdowns */
if ((window.location.pathname === "/products/health") ||
(window.location.pathname === "/products/new") ||
(window.location.pathname === "/products/sports") ||
(window.location.pathname === "/products/all")) {
    $(document).ready(function () {
        allOptions()
        window.onresize = function() {
            prodElSizes('all-prod-details')
        }
        sortScroll()
    })
}


/* On search product page load, select the searched flavour, and hide duplicate and out of stock flavours in dropdowns */
if (window.location.pathname === "/products/search") {
    $(document).ready(function () {
        if (json_prods !== null) {
            searchSelection(json_searched_prods)
            allOptions()
            window.onresize = function() {
                prodElSizes('all-prod-details')
            }
            sortScroll()
        }
    })
}