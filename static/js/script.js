function linkedFlavour() {
    let prodFlavour = document.getElementById("prod-flavours");
    let selectedSize = $("#prod-sizes :selected").val()
    for (let i = 0; i < json_prod.length; i++) {
        let obj = json_prod[i]
        if (selectedSize == obj.fields.size) {
            prodFlavour.value=obj.fields.flavour;
        }
    }
}


function linkedSize() {
    let prodSize = document.getElementById("prod-sizes");
    let selectedFlavour = $("#prod-flavours :selected").val()
    for (let i = 0; i < json_prod.length; i++) {
        let obj = json_prod[i]
        if (selectedFlavour == obj.fields.flavour) {
            prodSize.value=obj.fields.size;
        }
    }
}
