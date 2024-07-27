// Run all necessary functions once DOM has loaded
window.addEventListener('DOMContentLoaded', () => {
    featProds();
    allProds();
    searchedProds();
    prodPage();
    prodResizeScroll();
});

// Run all necessary functions once page content has loaded
window.addEventListener('load', () => {
    featProds();
    allProds();
    searchedProds();
    prodPage();
    prodResizeScroll();
});

// Run all necessary functions when page width is resized
window.addEventListener('resize', () => {
    let curWidth = window.innerWidth;
    if (curWidth !== prvWidth) {
        prodResizeScroll();
    }
});


// Function to show/hide description and ingredient text on button click on product pages
if (window.location.pathname.split('=')[0] === '/products/id') {
    document.body.addEventListener('click', function (e) {
        let descLink = document.getElementById('prod-desc-link');
        let descText = document.getElementById('prod-desc');
        let ingLink = document.getElementById('prod-ing-link');
        let ingText = document.getElementById('prod-ing');
        if (descLink === e.target && (descText.style.display === '' || descText.style.display === 'none')) {
            descText.style.display = 'block';
            descLink.innerHTML = 'Hide description <i class="fa-solid fa-square-caret-up"></i>';
        } else if (descLink === e.target && descText.style.display === 'block') {
            descText.style.display = 'none';
            descLink.innerHTML = 'Show description <i class="fa-solid fa-square-caret-down"></i>';
        }
        if (ingLink === e.target && (ingText.style.display === '' || ingText.style.display === 'none')) {
            ingText.style.display = 'block';
            ingLink.innerHTML = 'Hide description <i class="fa-solid fa-square-caret-up"></i>';
        } else if (ingLink === e.target && ingText.style.display === 'block') {
            ingText.style.display = 'none';
            ingLink.innerHTML = 'Show description <i class="fa-solid fa-square-caret-down"></i>';
        }
    });
}


// Function to dynamically set the height for products in lists
function prodElSizes(prodClass) {
    let prodList = document.getElementsByClassName(prodClass);
    for (let i = 1; i < prodList.length; i++) {
        if (typeof prodList[i] === 'object') {
            if (prodList[i].clientWidth > prodList[i - 1].clientWidth) {
                prodList[i].parentElement.style.width = prodList[i - 1].clientWidth + 'px';
                prodList[i].parentElement.style.flex = '0 0 auto';
            }
            if (prodList[i].getBoundingClientRect().top === prodList[i - 1].getBoundingClientRect().top) {
                if (prodList[i].clientHeight < prodList[i - 1].clientHeight) {
                    prodList[i].style.height = prodList[i - 1].clientHeight + 'px';
                }
                else if (prodList[i].clientHeight > prodList[i - 1].clientHeight) {
                    prodList[i - 1].style.height = prodList[i].clientHeight + 'px';
                    for (let x = 0; x < i; x++) {
                        if (typeof prodList[x] === 'object') {
                            if (prodList[i].getBoundingClientRect().top === prodList[x].getBoundingClientRect().top) {
                                prodList[x].style.height = prodList[i].clientHeight + 'px';
                            }
                        }
                    }
                }
                if (prodList[i].children[1].clientHeight < prodList[i - 1].children[1].clientHeight) {
                    prodList[i].children[1].style.height = prodList[i - 1].children[1].clientHeight + 'px';
                }
                else if (prodList[i].children[1].clientHeight > prodList[i - 1].children[1].clientHeight) {
                    prodList[i - 1].children[1].style.height = prodList[i].children[1].clientHeight + 'px';
                }
                for (let y = 0; y < i; y++) {
                    if (typeof prodList[y].children[1] === 'object') {
                        if ($(prodList[y].children[1]).find('.add-cart')[0].textContent !== 'Out Of Stock') {
                            prodList[y].children[1].removeAttribute('style')
                        }
                    }
                }
            }
        }
    }
}


// Function to reposition dynamic sort window dropdown
function sortDD(sortForm) {
    let buttonPosition = sortForm.children[1].getBoundingClientRect().bottom;
    let sortWindow = document.getElementsByClassName('sort-dd')[0];
    let sortPosition = sortWindow.getBoundingClientRect().top;

    if (sortPosition && sortPosition !== buttonPosition + 10) {
        sortWindow.style.top = buttonPosition + 'px';
    }
}


// Run the function to reposition the sort window dropdown when scrolling
function sortScroll() {
    let sortForm = document.getElementById('sort-form');
    $(document).scroll(function() {
        sortDD(sortForm);
    });
}


// Show/hide the Sort Products dropdown window based on button click
function sortProds() {
    let prodSort = document.getElementsByClassName('prod-sort')[0];
    let sortOpts = document.getElementsByClassName('sort-dd')[0];
    let sortStyle = window.getComputedStyle(sortOpts).getPropertyValue('display');
    let sortForm = document.getElementById('sort-form');

    if (sortStyle === 'none') {
        sortOpts.style.display = 'flex';
        sortDD(sortForm);
    }
    else {
        sortOpts.style.display = 'none';
    }

    document.body.addEventListener('click', function (e) {
        if (!(sortOpts.contains(e.target)) && !(prodSort).contains(e.target)) {
            sortOpts.style.display = 'none';
        }
    });
}


// If a user searched for a flavour, select that flavour for the products in the displayed search results
function searchSelection(json) {
    if (json.length > 0) {
        json.sort(function(a, b) {
            return a.fields.product - b.fields.product;
        });
        for (let prod in json) {
            if (Number(prod) === 0 ||
                (Number(prod) > 0 && json[prod].fields.product !== json[prod - 1].fields.product)) {
                let prodId = json[prod].fields.product;
                let prodFlavours = document.getElementById(prodId + '-prod-flavours');
                if (prodFlavours.options.length > 1) {
                    for (let i = 0; i < prodFlavours.options.length; i++) {
                        if ((!($(prodFlavours.options[i]).hasClass('hidden'))) &&
                            (json[prod].fields.flavour === prodFlavours.options[i].value) &&
                            (json[prod].fields.stock_count > 0) &&
                            (prodFlavours.options[i].selected !== true)) {
                            let prodSizes = document.getElementById(prodId + '-prod-sizes');
                            for (let j = 0; j < prodSizes.options.length; j++) {
                                if (Number(json[prod].fields.size) === Number(prodSizes.options[j].value)) {
                                    prodFlavours.options[i].setAttribute('selected', true);
                                    prodFlavours.options[i].selectedIndex = i;
                                    prodSizes.options[j].setAttribute('selected', true);
                                    prodSizes.options[j].selectedIndex = j;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


// Function to remove all classes for product sizes and flavours
function removeClasses(json) {
    for (let i = 0; i < json.length; i++) {
        let prodId = json[i].fields.product;
        let flavours = document.getElementById(prodId + '-prod-flavours');
        let sizes = document.getElementById(prodId + '-prod-sizes');
        $($(sizes)[0].options).removeClass();
        if (flavours) {
            $($(flavours)[0].options).removeClass();
        }
    }
}


// Sort product flavour options alphabetically
function sortFlavours(json) {
    for (let i = 0; i < json.length; i++) {
        let prodId = json[i].fields.product;
        if (json[i].fields.flavour !== null) {
            let flavours = '#' + prodId + '-prod-flavours';
            let options = $(flavours + ' option');

            options.sort(function (a, b) {
                if (a.text.toUpperCase() > b.text.toUpperCase()) return 1;
                else if (a.text.toUpperCase() < b.text.toUpperCase()) return -1;
                else return 0;
            });

            $(flavours).empty().append(options);
        }
    }
}


// Set the selected index and attribute for the available in-stock size
function sizeSelect(sizes) {
    for (let s = 0; s < sizes.length; s++) {
        if (sizes.selectedIndex === -1) {
            if (!($(sizes.options[s]).hasClass('hidden')) &&
                !($(sizes.options[s]).hasClass('oos'))) {
                sizes.selectedIndex = s;
                sizes.options[s].setAttribute('selected', true);
            }
        } else {
            sizes.options[sizes.selectedIndex].setAttribute('selected', true);
        }
    }
}


// Set the selected index and attribute for the available in-stock flavour
function flavourSelect(json) {
    for (let i = 0; i < json.length; i++) {
        let flavours = document.getElementById(json[i].fields.product + '-prod-flavours');
        let selectedSize = $('#' + json[i].fields.product + '-prod-sizes :selected').val();
        if (flavours) {
            for (let f = 0; f < flavours.length; f++) {
                flavours.options[f].removeAttribute('selected');
                if (json[i].fields.flavour === flavours.options[f].value &&
                    Number(json[i].fields.size) === Number(selectedSize)) {
                    if (flavours.selectedIndex === -1) {
                        if (!($(flavours.options[f]).hasClass('hidden')) &&
                            !($(flavours.options[f]).hasClass('oos')) &&
                            !($(flavours.options[f]).hasClass('na')) &&
                            flavours.options[f].disabled === false) {
                            $(flavours.options[f]).removeClass();
                            flavours.options[f].setAttribute('selected', true);
                            flavours.selectedIndex = f;
                            flavours.options[f].classList.add('stock');

                        }
                        else if ($(flavours.options[f]).hasClass('hidden')) {
                            $(flavours.options[f]).removeClass();
                            flavours.options[f].setAttribute('selected', true);
                            flavours.options[f].disabled = false;
                            flavours.selectedIndex = f;
                            flavours.options[f].classList.add('stock');

                        }
                    }
                }
                else if (flavours.selectedIndex !== -1 &&
                    flavours.options[flavours.selectedIndex].disabled === true) {
                    flavours.selectedIndex = -1;
                }
            }
        }
    }
    for (let i = 0; i < json.length; i++) {
        let flavours = document.getElementById(json[i].fields.product + '-prod-flavours');
        if (flavours) {
            if (flavours.selectedIndex !== -1 &&
                flavours.options[flavours.selectedIndex].disabled === false) {
                flavours.options[flavours.selectedIndex].setAttribute('selected', true);
            }
        }
    }
}


// Add/remove classes and attributes for product size options based on stock availability and selections
function oosSizes(json) {
    for (let i = 0; i < json.length; i++) {
        let obj = json[i];
        let sizes = document.getElementById(obj.fields.product + '-prod-sizes');
        let flavours = document.getElementById(obj.fields.product + '-prod-flavours');
        for (let s = 0; s < sizes.length; s++) {
            if (Number(obj.fields.size) === Number(sizes.options[s].value) &&
                (obj.fields.flavour === null || flavours.options[s] != null && flavours.options[s].value === obj.fields.flavour)) {
                if (obj.fields.stock_count < 1 && !($(sizes.options[s]).hasClass('hidden'))) {
                    sizes.options[s].disabled = true;
                    sizes.options[s].classList.add('oos');
                    sizes.options[s].removeAttribute('selected');
                    if (sizes.selectedIndex === s) {
                        sizes.selectedIndex = -1;
                    }
                } else if (obj.fields.stock_count > 0) {
                    sizes.options[s].classList.add('stock');
                }
            }
        }
    }
     for (let i = 0; i < json.length; i++) {
         let obj = json[i];
         let sizes = document.getElementById(obj.fields.product + '-prod-sizes');
         for (let s = 0; s < sizes.length; s++) {
             if ($(sizes.options[s]).hasClass('stock') &&
                 $(sizes.options[s]).val() !== $(sizes.options[s]).siblings().not('.hidden').filter('.stock').val()) {
                 sizes.options[s].classList.remove('hidden');
                 sizes.options[s].style.display = 'unset';
             }
             if ($(sizes.options[s]).val() === $(sizes.options[s]).siblings().not('.hidden').filter('.stock').val() &&
                 ($(sizes.options[s]).hasClass('hidden stock') || $(sizes.options[s]).hasClass('stock hidden'))) {
                 sizes.options[s].classList.remove('stock');
             }
             if ($(sizes.options[s]).val() === $(sizes.options[s]).siblings().filter('.stock').val() &&
                 $(sizes.options[s]).hasClass('oos')) {
                 sizes.options[s].classList.add('hidden');
                 sizes.options[s].style.display = 'none';
                 sizes.options[s].disabled = false;
                 sizes.options[s].classList.remove('oos');
             }
             // Run the function to select an available size option
             sizeSelect(sizes);
         }
     }
}


// Add/remove classes and attributes for product flavour options based on stock availability and selections
function oosFlavours(flavours, obj) {
    let selectedSize = $('#' + obj.fields.product + '-prod-sizes :selected').val();
    for (let f = 0; f < flavours.length; f++) {
        if (Number(obj.fields.size) === Number(selectedSize)) {
            if (flavours.options[f].value === obj.fields.flavour &&
                obj.fields.stock_count < 1) {
                flavours.options[f].disabled = true;
                flavours.options[f].classList.add('oos');
                flavours.options[f].removeAttribute('selected');
                if (flavours.selectedIndex === f) {
                    flavours.selectedIndex = -1;
                }
            } else if (flavours.options[f].value === obj.fields.flavour &&
                obj.fields.stock_count > 0) {
                flavours.options[f].disabled = false;
                flavours.options[f].classList.add('stock');
                if (flavours.selectedIndex === -1 || flavours.options[flavours.selectedIndex].disabled) {
                    flavours.selectedIndex = f;
                    flavours.options[f].setAttribute('selected', true);
                }
            }
        }
    }
}


// Run the functions to check for out of stock sizes and flavours, check for unavailable flavours, and select available flavour option
function oosProducts(json) {
    oosSizes(json);

    for (let i = 0; i < json.length; i++) {
        let obj = json[i];
        let flavours = document.getElementById(obj.fields.product + '-prod-flavours');
        if (flavours) {
            oosFlavours(flavours, obj);
        }
    }
    for (let i = 0; i < json.length; i++) {
        let obj = json[i];
        let flavours = document.getElementById(obj.fields.product + '-prod-flavours');
        if (flavours) {
            for (let f = 0; f < flavours.length; f++) {
                if (flavours.options[f].classList.length === 0) {
                    flavours.options[f].disabled = true;
                    flavours.options[f].classList.add('na');
                    flavours.options[f].removeAttribute('selected');
                    if (flavours.selectedIndex === f) {
                        flavours.selectedIndex = -1;
                    }
                }
            }
        }
    }
    flavourSelect(json);
}


// Customise display for product details based on selections
function prodDetails(json) {
    for (let i = 0; i < json.length; i++) {
        let obj = json[i];
        let selectedFlavour = $('#' + obj.fields.product + '-prod-flavours :selected').val();
        let selectedSize = $('#' + obj.fields.product + '-prod-sizes :selected').val();
        let flavours = document.getElementById(obj.fields.product + '-prod-flavours');
        let sizes = document.getElementById(obj.fields.product + '-prod-sizes');
        let price = document.getElementById(obj.fields.product + '-prod-price');
        let quantity = document.getElementById(obj.fields.product + '-prod-quantity');
        let cart = document.getElementById(obj.fields.product + '-prod-cart');
        let stock = document.getElementById(obj.fields.product + '-prod-stock');

        // Add price, max quantity, and in stock text
        if (obj.fields.stock_count > 0 &&
            (obj.fields.flavour === null || obj.fields.flavour === selectedFlavour) &&
            Number(obj.fields.size) === Number(selectedSize)) {
            price.textContent = 'Price: € ' + obj.fields.price;
            quantity.setAttribute('max', obj.fields.stock_count);
            if (stock !== null) {
                stock.textContent = 'Availability: In Stock';
            }
        }

        // Count how many options are disabled and hidden (unavailable)
        let disabledOpts = 0;
        for (let s = 0; s < sizes.length; s++) {
            if (sizes.options[s].disabled) {
                disabledOpts++;
            }
            else if ($(sizes.options[s]).hasClass('hidden')) {
                disabledOpts++;
            }
        }

        // If all options are disabled/hidden, remove size/flavour options, cart section, and add Out Of Stock text
        if (sizes.length === disabledOpts) {
            if (stock !== null) {
                sizes.parentElement.style.display = 'none';
                cart.style.display = 'none';
                stock.textContent = 'Availability: Out Of Stock';
                if (flavours) {
                    flavours.parentElement.style.display = 'none';
                }
            }
            else {
                sizes.parentElement.style.display = 'none';
                cart.textContent = 'Out Of Stock';
                cart.style.justifyContent = 'center';
                if (flavours) {
                    flavours.parentElement.style.display = 'none';
                }
            }
        }
    }
}


// Hide duplicate select options
function dupeOpts(json, option) {
    for (let i = 0; i < json.length; i++) {
        let fieldId = json[i].fields.product + '-prod-' + option;
        let dupes = {};
        $('select[name=' + fieldId + '] > option').each(function() {
            if (dupes[this.text]) {
                $(this).hide();
                $(this).addClass('hidden');
                $(this).prop('disabled', false);
            } else {
                dupes[this.text] = this.value;
            }
        });
    }
}


// Function to unwrap hidden select options in a span for Safari/IE
function safariUnhideDupes() {
    let hiddenOpts = document.getElementsByClassName('hidden');
    for (let i = 0; i < hiddenOpts.length; i++) {
        if ($(hiddenOpts[i]).parent().is('span')) {
            $(hiddenOpts[i]).unwrap();
        }
    }
}


// Function to wrap hidden select options in a span for Safari/IE
function safariHideDupes() {
    let hiddenOpts = document.querySelectorAll('.hidden');
    for (let i = 0; i < hiddenOpts.length; i++) {
        if (!($(hiddenOpts[i]).parent().is('span'))) {
            $(hiddenOpts[i]).wrap('<span>');
        }
    }
}


// Main function to run all product functions
function prodFunctions(json) {
    if (json) {
        safariUnhideDupes();
        removeClasses(json);
        sortFlavours(json);
        dupeOpts(json, 'flavours');
        dupeOpts(json, 'sizes');
        oosProducts(json);
        prodDetails(json);
        safariHideDupes();
    }
}


// Function to check if any products on the product browser pages are available before running the main product function
function multiProd(json) {
    // Check if any products are visible on the page
    let noResults = document.getElementsByClassName('prod-oos');
    if (noResults.length > 0) {
        // Center content for no results
        let prodPage = document.getElementsByClassName('all-prod-page')[0];
        prodPage.style.marginLeft = 'auto';
    }
    else {
        prodFunctions(json);
    }
}


// Run the main product function for each featured product
function featOptions() {
    prodFunctions(json_new_prod);
    prodFunctions(json_sports_prod);
    prodFunctions(json_health_prod);
}


// Run the main product function for the product on the individual product page, which in turn runs the main product function
function productOptions() {
    prodFunctions(json_prod);
}


// For linked products on individual product pages, run the function for multi-product pages, which in turn runs the main product function
function linkedOptions() {
    if (typeof json_linked_prods !== 'undefined') {
        multiProd(json_linked_prods);
    }
}


// Run the function for multi-product pages
function allOptions() {
    multiProd(json_prods);
}


// On the individual product pages, run relevant functions that in turn run the main product function
function prodPage() {
    if (window.location.pathname.split('=')[0] === '/products/id') {
        productOptions();
        linkedOptions();
    }
}


// On the homepage, run relevant function that in turn runs the main product function
function featProds() {
    if (window.location.pathname === '/') {
        featOptions();
    }
}


// On the multi-product pages, run relevant function that in turn runs the main product function
function allProds() {
    if ((window.location.pathname === '/products/health') ||
        (window.location.pathname === '/products/new') ||
        (window.location.pathname === '/products/sports') ||
        (window.location.pathname === '/products/all')) {
        allOptions();
    }
}


// On the product search page, run relevant functions that in turn run the main product function
function searchedProds() {
    if (window.location.pathname === '/products/search') {
        if (window.json_searched_prods && json_searched_prods) {
            allOptions();
            searchSelection(json_searched_prods);
        }
    }
}


// On all product pages, run the function to resize heights for product rows and the sort window repositioning function
function prodResizeScroll() {
    if ((window.location.pathname === '/products/health') ||
        (window.location.pathname === '/products/new') ||
        (window.location.pathname === '/products/sports') ||
        (window.location.pathname === '/products/all') ||
        (window.location.pathname === '/products/search')) {
        prodElSizes('all-prod-details');
        sortScroll();
    }
    if (window.location.pathname.split('=')[0] === '/products/id') {
        prodElSizes('linked-details');
    }
}