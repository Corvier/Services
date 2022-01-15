/* VARIABLE PARA INICIALIZAR EL MAPA */
let map = L.map('map').setView([12.116112996824123, -86.23889456370239], 8);


/******************************************************************************
*                      CONFIGURACiÓN DEL MAPA                                *
******************************************************************************/
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

document.getElementById('_select-ubicacion').addEventListener('change', function(e){
    console.log(e);
    let coords = e.target.value.split(',');
    map.flyTo(coords, 18);
});