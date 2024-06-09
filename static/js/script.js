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


if (window.location.pathname === "/") {
    $(document).ready(function () {
        let newFlavour = document.getElementById("new-prod-flavours");
        let sportsFlavour = document.getElementById("sports-prod-flavours");
        let healthFlavour = document.getElementById("health-prod-flavours");
        if (newFlavour) {
            let newSelectedSize = $("#new-prod-sizes :selected").val().slice(0, -2);
            for (let i = 0; i < json_new_prod.length; i++) {
                let obj = json_new_prod[i]
                if (newSelectedSize == obj.fields.size &&
                    newFlavour.value != obj.fields.flavour) {
                    newFlavour.options[i].disabled = true
                } else if (newSelectedSize != obj.fields.size &&
                    newFlavour.value != obj.fields.flavour) {
                    newFlavour.options[i].disabled = true
                }
            }
        }
        if (sportsFlavour) {
            let sportsSelectedSize = $("#sports-prod-sizes :selected").val().slice(0, -2);
            for (let i = 0; i < json_sports_prod.length; i++) {
                let obj = json_sports_prod[i]
                if (sportsSelectedSize == obj.fields.size &&
                    sportsFlavour.value != obj.fields.flavour) {
                    sportsFlavour.options[i].disabled = true
                } else if (sportsSelectedSize != obj.fields.size &&
                    sportsFlavour.value != obj.fields.flavour) {
                    sportsFlavour.options[i].disabled = true
                }
            }
        }
        if (healthFlavour) {
            let healthSelectedSize = $("#health-prod-sizes :selected").val().slice(0, -2);
            for (let i = 0; i < json_health_prod.length; i++) {
                let obj = json_health_prod[i]
                if (healthSelectedSize == obj.fields.size &&
                    healthFlavour.value != obj.fields.flavour) {
                    healthFlavour.options[i].disabled = true
                } else if (healthSelectedSize != obj.fields.size &&
                    healthFlavour.value != obj.fields.flavour) {
                    healthFlavour.options[i].disabled = true
                }
            }
        }
    })
}


function featProductFlavour() {
    let newFlavour = document.getElementById("new-prod-flavours");
    let sportsFlavour = document.getElementById("sports-prod-flavours");
    let healthFlavour = document.getElementById("health-prod-flavours");
    if (newFlavour) {
        let newSelectedSize = $("#new-prod-sizes :selected").val().slice(0, -2);
        for (let i = 0; i < json_new_prod.length; i++) {
            let obj = json_new_prod[i]
            if (newSelectedSize == obj.fields.size) {
                newFlavour.value = obj.fields.flavour
                newFlavour.options[i].disabled = false;
            } else if (newSelectedSize != obj.fields.size) {
                newFlavour.options[i].disabled = true
            }
        }
    }
    if (sportsFlavour) {
        let sportsSelectedSize = $("#sports-prod-sizes :selected").val().slice(0, -2);
        for (let i = 0; i < json_sports_prod.length; i++) {
            let obj = json_sports_prod[i]
            if (sportsSelectedSize == obj.fields.size) {
                sportsFlavour.value = obj.fields.flavour
                sportsFlavour.options[i].disabled = false;
            } else if (sportsSelectedSize != obj.fields.size) {
                sportsFlavour.options[i].disabled = true
            }
        }
    }
    if (healthFlavour) {
        let healthSelectedSize = $("#health-prod-sizes :selected").val().slice(0, -2);
        for (let i = 0; i < json_health_prod.length; i++) {
            let obj = json_health_prod[i]
            if (healthSelectedSize == obj.fields.size) {
                healthFlavour.value = obj.fields.flavour
                healthFlavour.options[i].disabled = false;
            } else if (healthSelectedSize != obj.fields.size) {
                healthFlavour.options[i].disabled = true
            }
        }
    }
}


function featProductSize() {
    let prodFlavour = document.getElementById("prod-flavours");
    let prodSize = document.getElementById("prod-sizes");
    let selectedFlavour = $("#prod-flavours :selected").val()
    for (let i = 0; i < json_prod.length; i++) {
        let obj = json_prod[i]
        if (selectedFlavour == obj.fields.flavour) {
            prodSize.value = obj.fields.size;
            prodFlavour.options[i].disabled = false
        }
        if (selectedFlavour != obj.fields.flavour) {
            prodFlavour.options[i].disabled = true
        }
    }
}


function linkedProdDict() {
    let products = {}
    for (let i = 0; i < json_linked_prods.length; i++) {
        if (json_linked_prods[i]) {
            let obj = json_linked_prods[i]
            let prod_id = obj.fields.product.toString()
            if (products[prod_id] && !(products[prod_id])) {
                products[prod_id] = {}
                products[prod_id] = Object.assign(products[prod_id], {'prod_id': prod_id})
                products[prod_id] = Object.assign(products[prod_id], {'flavours': []})

            } else if (!(products[prod_id])) {
                products[prod_id] = {}
                products[prod_id] = Object.assign(products[prod_id], {'prod_id': prod_id})
                products[prod_id] = Object.assign(products[prod_id], {'flavours': []})
            }
            if (products[prod_id]['flavours'] &&
                !(obj.fields.flavour in products[prod_id]['flavours'])) {
                products[prod_id]['flavours'].push(obj.fields.flavour)
            } else {
                products[prod_id]['flavours'] = [obj.fields.flavour]
            }
            if (products[prod_id]['sizes'] &&
                !(obj.fields.size in products[prod_id]['sizes'])) {
                products[prod_id]['sizes'].push(obj.fields.size)
            } else {
                products[prod_id]['sizes'] = [obj.fields.size]
            }
        }
    }
    return products
}


if (window.location.pathname.indexOf("/products/") !== -1) {
    $(document).ready(function () {
        let prodFlavour = document.getElementById("prod-flavours");
        let dupeFlavours = {};
        $("select > option").each(function () {
            if(dupeFlavours[this.text]) {
                $(this).hide();
                $(this).addClass('hidden')
            } else {
                dupeFlavours[this.text] = this.value;
            }
        })

        if (prodFlavour) {
            let json_prod_sorted = json_sort(json_prod)
            for (let i = 0; i < json_prod_sorted.length; i++) {
                let obj = json_prod_sorted[i]
                let selectedSize = $("#prod-sizes :selected").val()
                if (selectedSize == obj.fields.size) {
                    if (prodFlavour[i].value != obj.fields.flavour) {
                        prodFlavour.options[i].disabled = true
                        if (!($(prodFlavour[i]).hasClass('hidden'))) {
                            prodFlavour.options[i].classList.add('oos')
                        }
                    }
                }
                else if (selectedSize != obj.fields.size) {
                    prodFlavour.options[i].disabled = true
                    if (!($(prodFlavour[i]).hasClass('hidden'))) {
                        prodFlavour.options[i].classList.add('oos')
                    }
                }
            }
        }

        let products = linkedProdDict()
        for (let prod in products) {
            let linkedProdFlavour = document.getElementById(products[prod]['prod_id'] + "-prod-flavours");
            if (linkedProdFlavour) {
                let linkedSelectedSize = $("#" + products[prod]['prod_id'] + "-prod-sizes :selected").val()
                for (let opt = 0; opt < products[prod]['flavours'].length; opt++) {
                    if (linkedProdFlavour && linkedProdFlavour[opt] && products[prod]['flavours']) {
                        if (linkedSelectedSize == products[prod]['sizes'][opt] &&
                            linkedProdFlavour.options[opt].value != products[prod]['flavours'][opt]) {
                            linkedProdFlavour.options[opt].disabled = true;
                            $(linkedProdFlavour.options[opt]).addClass('oos');
                        } else if (linkedSelectedSize != products[prod]['sizes'][opt] &&
                            linkedProdFlavour.options[opt].value != products[prod]['flavours'][opt]) {
                            linkedProdFlavour.options[opt].disabled = true;
                            $(linkedProdFlavour.options[opt]).addClass('oos');
                        } else {
                            linkedProdFlavour.value = products[prod]['flavours'][opt];
                        }
                    }
                }
            }
        }
    })
}


function flavourMatch(prodFlavour, i) {
    let flavourCheck = prodFlavour.innerText.match(new RegExp(prodFlavour[i].value, 'g'))
    if (flavourCheck.length > 1) {
        if (prodFlavour[i].disabled == true) {
            prodFlavour.options[i].style.display = "none"
            prodFlavour.options[i].classList.add('hidden')
            prodFlavour.options[i].classList.remove('oos')
            prodFlavour[i].disabled = false
        }
    }
}


function productOptions() {
    let prodFlavour = document.getElementById("prod-flavours");
    if (prodFlavour) {
        let selectedSize = $("#prod-sizes :selected").val()
        for (let i = 0; i < json_prod.length; i++) {
            let obj = json_prod[i]
            if (selectedSize == obj.fields.size) {
                if (prodFlavour[i].value != obj.fields.flavour) {
                    prodFlavour.options[i].disabled = true
                    prodFlavour.options[i].classList.add('oos')
                } else {
                    prodFlavour.options[i].disabled = false
                    prodFlavour.options[i].classList.remove('hidden')
                    prodFlavour.options[i].classList.remove('oos')
                    prodFlavour.options[i].style.display = 'unset'
                }
            }
            else {
                prodFlavour.options[i].disabled = true
                prodFlavour.options[i].classList.add('oos')
            }

            flavourMatch(prodFlavour, i)
        }
    }
}


function linkedOptions() {
    products = linkedProdDict()
    for (let prod in products) {
        let linkedProdFlavour = document.getElementById(products[prod]['prod_id'] + "-prod-flavours");
        if (linkedProdFlavour) {
            let linkedSelectedSize = $("#" + products[prod]['prod_id'] + "-prod-sizes :selected").val()
            for (let opt in products[prod]['flavours']) {
                if (linkedProdFlavour && linkedProdFlavour[opt] && products[prod]['flavours']) {
                    linkedProdFlavour.options[opt].disabled = false;
                    if (linkedSelectedSize == products[prod]['sizes'][opt] &&
                        linkedProdFlavour.options[opt].value != products[prod]['flavours'][opt]) {
                        linkedProdFlavour.options[opt].disabled = true;
                        linkedProdFlavour.value = products[prod]['flavours'][opt];
                    }
                }
            }
        }
    }
}