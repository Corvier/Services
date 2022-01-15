// crear funcion y le paso un argumento 
function addToCart(form) {
    data = new FormData(form); // toma solo los inputs del formulario
    let request = new XMLHttpRequest();
    request.open('POST', '/cart');
    request.send(data);

    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            dataresponse = request.responseText;

            alert(dataresponse);
            return false;
        }
    }
};

function incrementarValue(selector) {
    var valor = parseInt(document.querySelector(selector).value, 10);
    valor = isNaN(valor) ? 0 : valor;
    valor++;
    // document.getElementById('number').value = valor;
    document.querySelector(selector).value = valor;
}

function decrementarValue(selector) {
    var valor = parseInt(document.querySelector(selector).value, 10);
    valor = isNaN(valor) ? 0 : valor;
    valor < 1 ? valor = 1 : valor;
    valor != 1 ? valor--  : valor;
    // document.getElementById('number').value = valor;
    document.querySelector(selector).value = valor;
}