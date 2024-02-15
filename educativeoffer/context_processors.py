from datetime import datetime
from .models import Especialidad, Aviso, AsesorEducativo, Alumno, Usuario, Escuela, Valor, Categoria, Inscripcion, Asignatura, ProyectoAsignacion, ProyectoAlumno, Telefono, ImagenProyecto, ProyectoFinal

def current_year(request):
    year = datetime.now().year
    return {'current_year': year}

def usuario(request):
    usuariosListados = Usuario.objects.all()
    return {'alumnos': usuariosListados}

def asesor(request):
    asesoresListados = AsesorEducativo.objects.all()
    return {'asesores': asesoresListados}

def alumno(request):
    alumnosListados = Alumno.objects.all()
    return {'alumnos': alumnosListados}

def valor(request):
    valoresListados = Valor.objects.all()
    return {'valores': valoresListados}

def escuela(request):
    escuela = Escuela.objects.first()
    return {'escuela': escuela}

def especialidad(request):
    especialidadesListadas = Especialidad.objects.all()
    return {'especialidades': especialidadesListadas}

def inscripcion(request):
    inscripcionesListadas = Inscripcion.objects.all()
    return {'inscripciones': inscripcionesListadas}

def categoria(request):
    categoriasListadas = Categoria.objects.all()
    return {'categorias': categoriasListadas}

def asignatura(request):
    asignaturasListadas = Asignatura.objects.all()
    return {'asignaturas': asignaturasListadas}

def proyectoasignacion(request):
    proyectosListados = ProyectoAsignacion.objects.all()
    return {'proyectos_asignados': proyectosListados}

def proyectoalumno(request):
    proyectosAlumnos = ProyectoAlumno.objects.all()
    return {'proyecto_alumno': proyectosAlumnos}

def proyectofinal(request):
    proyectosFinales = ProyectoFinal.objects.all()
    return {'proyectos_finales': proyectosFinales}

def telefono(request):
    telefonosListados = Telefono.objects.all()
    return {'telefonos': telefonosListados}

def imagen(request):
    imagenesListadas = ImagenProyecto.objects.all()
    return {'imagenes': imagenesListadas}

def galeria(request):
    categorias = Categoria.objects.all()
    galerias_por_categoria = []

    for categoria in categorias:
        galerias = categoria.galeria_set.filter(habilitada=True)
        galerias_por_categoria.append((categoria, galerias))

    return {'categorias': categorias, 'galerias_por_categoria': galerias_por_categoria}

def aviso(request):
    avisosListados = Aviso.objects.filter(disponible=True)
    cantidad_avisos_disponibles = avisosListados.count()
    return {'avisos': avisosListados, 'cantidad_avisos_disponibles': cantidad_avisos_disponibles}
