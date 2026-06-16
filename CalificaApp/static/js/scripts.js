document.addEventListener("DOMContentLoaded", function() {
    console.log("Sistema escolar cargado correctamente.");


    window.cambiarFormulario = function() {
        var seleccion = document.getElementById("tipo_formulario").value;
        var secciones = document.getElementsByClassName("seccion-formulario");
        
        for (var i = 0; i < secciones.length; i++) {
            secciones[i].style.display = "none";
            // Quitar el 'required' a los inputs ocultos para que no den error al enviar
            var inputs = secciones[i].querySelectorAll("input, select");
            inputs.forEach(input => input.removeAttribute("required"));
        }
        
        if (seleccion) {
            var seccionActiva = document.getElementById("form_" + seleccion);
            if (seccionActiva) {
                seccionActiva.style.display = "block";
                // Poner 'required' a los inputs visibles
                var inputsActivos = seccionActiva.querySelectorAll("input, select");
                inputsActivos.forEach(input => input.setAttribute("required", "required"));
            }
        }
    };
});