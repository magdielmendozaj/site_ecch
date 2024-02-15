$(document).ready(function () {
    var estadoSelect = $('#id_estado');
    var municipioSelect = $('#id_municipio');
    var localidadSelect = $('#id_localidad');
    var codigoPostalInput = $('#c_postal');

    estadoSelect.on('change', function () {
        var estadoSeleccionado = estadoSelect.val();
        if (estadoSeleccionado) {
            $.ajax({
                url: '/obtener_municipios/', 
                data: { estado_id: estadoSeleccionado },
                success: function (data) {
                    console.log('Datos recibidos:', data);
                    municipioSelect.empty();
                    $.each(data.municipios, function (key, value) {
                        municipioSelect.append($("<option></option>")
                            .attr("value", value.id)
                            .text(value.nombre));
                    });

                    cargarLocalidades();
                }
            });
        }
    });

    municipioSelect.on('change', function () {
        cargarLocalidades();
    });

    function cargarLocalidades() {
        var municipioSeleccionado = municipioSelect.val();
        if (municipioSeleccionado) {
            $.ajax({
                url: '/obtener_localidades/', 
                data: { municipio_id: municipioSeleccionado },
                success: function (data) {
                    localidadSelect.empty();
                    $.each(data.localidades, function (key, value) {
                        var option = $("<option></option>")
                            .attr("value", value.id)
                            .text(value.nombre);
                        localidadSelect.append(option);
                    });

                    actualizarCodigoPostal();
                }
            });
        }
    }

    localidadSelect.on('change', actualizarCodigoPostal);

    function actualizarCodigoPostal() {
        var localidadSeleccionada = localidadSelect.val();
        if (localidadSeleccionada) {
            $.ajax({
                url: '/obtener_codigo_postal/',  
                data: { localidad_id: localidadSeleccionada },
                success: function (data) {
                    codigoPostalInput.val(data.codigoPostal);
                }
            });
        }
    }
});