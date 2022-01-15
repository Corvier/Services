console.info("Conexión exitosa!");
/******************************************************************************
 *                             VARIABLES                                      *
 ******************************************************************************/
/*  VARIABLE PARA LA BARRA DE NAVEGACIÓN  */
let ubicacionPrincipal  = window.pageYOffset;

/*  VARIABLES PARA EL USO DEL SERVIDOR CLOUDINARY */
const imagenPreview = document.getElementById("img-preview");
const imageUploader = document.getElementById("img-uploader");
const imagenPreviewBusiness = document.getElementById("img-preview2");
const imageUploaderBusiness = document.getElementById("img-uploader2");
const CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/cloudinary-vruiz/image/upload";
const CLOUDINARY_UPLOAD_PRESET = "bjmdnh0j";

function eliminarDato(id){
    Swal.fire({
        icon: 'question',
        title: '¿Estás seguro de eliminar este dato?',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si, Eliminar!'
    
    }).then((result) => {
        
        if (result.isConfirmed) {
            window.location = `/admin/delete_products/${id}`;
            // Swal.fire(
            // 'Deleted!',
            // 'Your file has been deleted.',
            // 'success'
            // )
        }
    })
}

/******************************************************************************
 *                             FUNCIONES                                 *
 ******************************************************************************/
// 1) Función de JavaScript para deshabilitar el envío de formularios si hay campos no válidos
(function() {
    'use strict'

    // Obtener todos los formularios a los que queremos aplicar estilos de validación de Bootstrap personalizados
    var forms = document.querySelectorAll('.needs-validation')

    // los recorremos y evitar la presentación
    Array.prototype.slice.call(forms)
    .forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            
            form.classList.add('was-validated')
        }, false)
    })
})()

// 2. Función de JavaScript para esconder y mostrar la barra de navegacion
window.onscroll = function() {
    let Desplazamiento_Actual = window.pageYOffset;
    if(ubicacionPrincipal >= Desplazamiento_Actual){
        document.getElementById('navbar').style.top = '0';
    }
    else{
        document.getElementById('navbar').style.top = '-100px';
    }
    ubicacionPrincipal = Desplazamiento_Actual;
}

/******************************************************************************
 *                             EVENT LISTENER                                 *
 ******************************************************************************/

/* EVENTO PARA ENVIAR Y RECIBIR INFORMACIÓN DE CLUDINARY SOBRE LA IMAGEN DEL USUARIO */
imageUploader.addEventListener("change", async (e) => {
    // console.log(e);
    const file = e.target.files[0];
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("upload_preset", CLOUDINARY_UPLOAD_PRESET);

    const url = await axios.post(CLOUDINARY_URL, formData, {
        headers: {
            "Content-Type": "multipart/form-data"
        }
    });
    
    console.log(url);
    document.getElementById("imagen").value = url.data.secure_url;
    imagenPreview.src = url.data.secure_url;
});

/* EVENTO PARA ENVIAR Y RECIBIR INFORMACIÓN DE CLUDINARY SOBRE LA IMAGEN DEL BUSINESS */
imageUploaderBusiness.addEventListener("change", async (e) => {
    // console.log(e);
    const file2 = e.target.files[0];
    
    const formData2 = new FormData();
    formData2.append("file", file2);
    formData2.append("upload_preset", CLOUDINARY_UPLOAD_PRESET);

    const url = await axios.post(CLOUDINARY_URL, formData2, {
        headers: {
            "Content-Type": "multipart/form-data"
        }
    });
    
    console.log(url);
    document.getElementById("imagen2").value = url.data.secure_url;
    imagenPreviewBusiness.src = url.data.secure_url;
});