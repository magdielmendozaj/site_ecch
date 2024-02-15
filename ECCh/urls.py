"""ECCh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from educativeoffer.views import home_view, index_view, index_or_home_view, about_view, login_view, logout_view, inscripcion_view, asesor_view, especialidad_view, set_password_view, obtener_municipios, obtener_localidades, obtener_codigo_postal, profile_view, message_view, galery_view, calificaciones_view, asignar_calificacion, editar_calificacion, cambiar_contrasena_view, editar_nombre, editar_fecha_nacimiento, editar_sexo, editar_direccion, documentos_por_asignatura, registrar_documento, editar_documento, eliminar_documento, confirmar_eliminar_foto, crear_asignacion_proyecto, editar_proyecto_asignacion, eliminar_asignacion_proyecto, eliminar_proyecto_alumno, asignar_alumnos, material_view, documentos_view, proyectos_asignados, agregar_proyecto_final, editar_telefono, editar_proyecto, editar_imagen, aprobar_proyecto, ver_calificaciones, ver_mas_proyecto, view_pdf, ProfileUpdate, EmailUpdate
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_or_home_view, name='index_or_home'),
    path('home/',home_view, name='home'),
    path('index/',index_view, name='index'),
    path('perfil/<str:usuario_email>/',profile_view, name='profile_view'),
    path('calificaciones/<str:usuario_email>/',calificaciones_view, name='calificaciones_view'),
    path('asignar_calificacion/<str:usuario_email>/<int:asignatura_id>/',asignar_calificacion, name='asignar_calificacion'),
    path('editar_calificacion/<int:calificacion_id>/', editar_calificacion, name='editar_calificacion'),
    path('cambiar-contrasena/', cambiar_contrasena_view, name='cambiar_contrasena'),
    path('editar_nombre/', editar_nombre, name='editar_nombre'),
    path('editar_fecha_nacimiento/', editar_fecha_nacimiento, name='editar_fecha_nacimiento'),
    path('editar_sexo', editar_sexo, name='editar_sexo'),
    path('editar_direccion', editar_direccion, name='editar_direccion'),
    path('documentos/<int:asignatura_id>/', documentos_por_asignatura, name='documentos_por_asignatura'),
    path('registrar_documento/<int:asignatura_id>/', registrar_documento, name='registrar_documento'),
    path('editar_documento/<int:documento_id>/', editar_documento, name='editar_documento'),
    path('eliminar_documento/<int:documento_id>/', eliminar_documento, name='eliminar_documento'),
    path('confirmar_eliminar_foto/', confirmar_eliminar_foto, name='confirmar_eliminar_foto'),
    path('crear_asignacion_proyecto/', crear_asignacion_proyecto, name='crear_asignacion_proyecto'),
    path('editar_proyecto_asignacion/<int:proyecto_id>/', editar_proyecto_asignacion, name='editar_proyecto_asignacion'),
    path('eliminar_asignacion_proyecto/<int:proyecto_id>/', eliminar_asignacion_proyecto, name='eliminar_asignacion_proyecto'),
    path('proyecto/<int:proyecto_id>/alumno/<int:alumno_id>/eliminar/', eliminar_proyecto_alumno, name='eliminar_proyecto_alumno'),
    path('proyecto/<int:proyecto_id>/asignar_alumnos/', asignar_alumnos, name='asignar_alumnos'),
    path('view_pdf/<int:proyecto_id>/', view_pdf, name='view_pdf'),
    path('documents/<int:asignatura_id>/', documentos_view, name='documents'),
    path('aboutus/',about_view, name='aboutus'),
    path('material/',material_view, name='material'),
    path('proyectos_asignados/', proyectos_asignados, name='proyectos_asignados'),
    path('proyecto_final/agregar/<int:proyecto_id>/', agregar_proyecto_final, name='agregar_proyecto_final'),
    path('proyecto/<int:proyecto_id>/editar/', editar_proyecto, name='editar_proyecto'),
    path('editar_imagen/<int:imagen_id>/', editar_imagen, name='editar_imagen'),
    path('aprobar_proyecto/<int:proyecto_id>/', aprobar_proyecto, name='aprobar_proyecto'),
    path('proyecto/<int:proyecto_id>/', ver_mas_proyecto, name='ver_mas_proyecto'),
    path('editar_telefono/<int:telefono_id>/', editar_telefono, name='editar_telefono'), 
    path('ver_calificaciones/', ver_calificaciones, name='ver_calificaciones'),
    path('message/<int:usuario_destino_id>/', message_view, name='message_view'),
    path('inscripcion/', inscripcion_view, name='inscripcion'),
    path('asesoreducativo/', asesor_view, name='asesoreducativo'),
    path('login/', login_view, name='login'),
    path('logout/',logout_view, name='logout'),
    path('obtener_municipios/', obtener_municipios, name='obtener_municipios'),
    path('obtener_localidades/', obtener_localidades, name='obtener_localidades'),
    path('obtener_codigo_postal/', obtener_codigo_postal, name='obtener_codigo_postal'),
    path('set_password/<str:email>/<str:activation_key>/', set_password_view, name='set_password'),
    path('especialidad/<str:nombre>/', especialidad_view, name='especialidad_view'),
    path('profile/', ProfileUpdate.as_view(), name='profile'),
    path('profile/email', EmailUpdate.as_view(), name='profile_email'),
    path('galery/', galery_view, name='galery'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
