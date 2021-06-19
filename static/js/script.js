function getUsedProducts() {
    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var result = window.localStorage.getItem(date);
    return result ? JSON.parse(result) : [];
}

function updateUsedProducts(event) {

    // Get the current list of used products stored on localStorage
    var usedProducts = [];
    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var result = window.localStorage.getItem(date);

    if (result == null) { // storage for today does not exist
        window.localStorage.clear();
    } else {
        usedProducts = JSON.parse(result);
    }

    // Update list of used products based on the checkboxes
    const productName = event.target.id;
    var index = usedProducts.indexOf(productName);
    if (event.target.checked) {
        // Add to used products if not already inside
        if (index == -1) {
            usedProducts.push(productName);
        }
      } else {
        // Remove from used products if it is in the list
        if (index > -1) {
            usedProducts.splice(index, 1);
        }
      }

    // Update list of current used products stored on localStorage
    window.localStorage.setItem(date, JSON.stringify(usedProducts));
}

// When page loads
window.onload = function() {
    var dayProducts = document.getElementsByName('day_product');
    var usedProducts = getUsedProducts();

    dayProducts.forEach(function(product) {
        // Ensure checkbox is checked if product is in the list of used day products
        if (usedProducts.indexOf(product.id) > -1) {
            product.checked = true;
        } 

        product.addEventListener('change', updateUsedProducts);
    })

    var nightProducts = document.getElementsByName('night_product');

    nightProducts.forEach(function(product) {
        // Ensure checkbox is checked if product is in the list of used night products
        if (usedProducts.indexOf(product.id) > -1) {
            product.checked = true;
        } 

        product.addEventListener('change', updateUsedProducts);
    })
}

// When user is about to leave the page
window.onbeforeunload = function() {
    if (typeof(Storage) == "undefined") {
        return "Your browser does not support web storage. Are you sure you want to leave this page? Your beauty routine checklist will be refreshed.";
    }
}