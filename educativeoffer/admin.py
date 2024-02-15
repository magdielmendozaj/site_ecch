from django.contrib import admin

from .models import Estado, Municipio, Localidad, Usuario, Alumno, AsesorEducativo, Sexo, MedioContacto, Especialidad, Inscripcion, Asignatura, Aviso, Profile, Telefono, Escuela, Valor, Galeria, Categoria, Calificacion, Documento, ProyectoAsignacion, ProyectoFinal, ImagenProyecto, ProyectoAlumno
# Register your models here.

admin.site.register(Estado)
admin.site.register(Municipio)
admin.site.register(Localidad)
admin.site.register(Usuario)
admin.site.register(Alumno)
admin.site.register(AsesorEducativo)
admin.site.register(Sexo)
admin.site.register(MedioContacto)
admin.site.register(Especialidad)
admin.site.register(Inscripcion)
admin.site.register(Asignatura)
admin.site.register(Aviso)
admin.site.register(Profile)
admin.site.register(Telefono)
admin.site.register(Escuela)
admin.site.register(Valor)
admin.site.register(Galeria)
admin.site.register(Categoria)
admin.site.register(Calificacion)
admin.site.register(Documento)
admin.site.register(ProyectoFinal)
admin.site.register(ProyectoAsignacion)
admin.site.register(ImagenProyecto)
admin.site.register(ProyectoAlumno)