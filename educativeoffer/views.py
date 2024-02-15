from django.shortcuts import render, redirect, get_object_or_404
from .models import Municipio, Localidad, Inscripcion, Especialidad, Profile, Alumno, Usuario, AsesorEducativo, Asignatura, Calificacion, Documento, ProyectoAsignacion, ProyectoAlumno, ProyectoFinal, ImagenProyecto, Telefono 
from django.http import JsonResponse
from django.contrib import messages

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import authenticate, login, logout

from django.conf import settings

from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from .forms import LoginForm, CustomAlumnoCreationForm, SetPasswordForm, ProfileForm, CustomAsesorCreationForm, EmailForm, CambiarContrasenaForm, EditarNombreForm, EditarFechaNacimientoForm, EditarSexoForm, EditarDireccionForm, DocumentoForm, ProyectoAsignacionForm, TelefonoForm, ProyectoFinalForm, EditarImagenForm
from django.urls import reverse, reverse_lazy

import hashlib, datetime, random
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView
from django.views.decorators.csrf import csrf_exempt

from .decorators import asesor_educativo_required

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Mensaje, Usuario
from django.db.models import Q
from django import forms 

from datetime import datetime
from datetime import date
from django.shortcuts import render

from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpResponseNotFound

# Create your views here. 

def home_view(request):
    return render(request,'home.html')

@login_required
@asesor_educativo_required 
def calificaciones_view(request, usuario_email):
    usuario = get_object_or_404(Usuario, email=usuario_email)
    asesor = request.user.asesoreducativo
    especialidad_alumno = None

    if hasattr(usuario, 'alumno'):
        alumno = usuario.alumno
        inscripcion = Inscripcion.objects.filter(alumno=alumno).first()

        if inscripcion:
            especialidad_alumno = inscripcion.especialidad
            asignaturas_especialidad = Asignatura.objects.filter(especialidad=especialidad_alumno)
        
        asignaturas_sin_calificacion = [asignatura for asignatura in asignaturas_especialidad
        if not asignatura.calificacion_set.filter(asesor=request.user.asesoreducativo, alumno=alumno).exists()
        ]
        calificaciones_alumno = Calificacion.objects.filter(alumno=usuario.alumno)
        proyectos_alumno = ProyectoFinal.objects.filter(proyecto_asignado__asesor=asesor, alumno=alumno)

        return render(request, 'calificaciones.html', {'usuario': usuario, 'especialidad_alumno': especialidad_alumno, 'asignaturas_especialidad': asignaturas_especialidad, 'asignaturas_sin_calificacion': asignaturas_sin_calificacion, 'calificaciones_alumno': calificaciones_alumno, 'proyectos_alumno': proyectos_alumno})

@login_required
@asesor_educativo_required   
def asignar_calificacion(request, usuario_email, asignatura_id):
    usuario = get_object_or_404(Usuario, email=usuario_email)
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    especialidad_alumno = None

    if hasattr(usuario, 'alumno'):
        alumno = usuario.alumno
        inscripcion = Inscripcion.objects.filter(alumno=alumno).first()

        if inscripcion:
            especialidad_alumno = inscripcion.especialidad
            periodo=generar_periodo(especialidad_alumno)
    if request.method == 'POST':    
        calificacion_existente = Calificacion.objects.filter(
            alumno=usuario.alumno,
            asesor=request.user.asesoreducativo,
            asignatura=asignatura,
            periodo=periodo
        ).first()

        if calificacion_existente:
            calificacion_existente.calificacion = request.POST.get('calificacion')
            calificacion_existente.save()
        else:
            calificacion_nueva = Calificacion(
                alumno=usuario.alumno,
                asesor=request.user.asesoreducativo,
                asignatura=asignatura,
                periodo=periodo,
                calificacion=request.POST.get('calificacion')
            )
            calificacion_nueva.save()
            messages.success(request, 'Calificación guardada exitosamente.')
            return redirect('calificaciones_view', usuario_email=alumno.usuario.email)

        return render(request, 'asignar.html', {'usuario': usuario, 'asignatura': asignatura})
    
    return render(request, 'asignar.html', {'usuario': usuario, 'asignatura': asignatura, 'periodo': periodo})

def generar_periodo(especialidad):
    año_actual = datetime.now().year
    mes_actual = datetime.now().month

    if especialidad.division == 4:
        if mes_actual <= 3:
            periodo = f"{año_actual}-1"
        elif mes_actual <= 6:
            periodo = f"{año_actual}-2"
        elif mes_actual <= 9:
            periodo = f"{año_actual}-3"
        else:
            periodo = f"{año_actual}-4"
    elif especialidad.division == 6:
        if mes_actual <= 6:
            periodo = f"{año_actual}-1"
        else:
            periodo = f"{año_actual}-2"
    else:
        periodo = f"{año_actual}-1"

    return periodo

@login_required
@asesor_educativo_required   
def editar_calificacion(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id)

    if request.method == 'POST':
        calificacion.calificacion = request.POST.get('nueva_calificacion')
        calificacion.save()
        messages.success(request, 'Calificación editada exitosamente.')
        return redirect('calificaciones_view', usuario_email=calificacion.alumno.usuario.email)

    return render(request, 'editar_calificacion.html', {'calificacion': calificacion})

def profile_view(request, usuario_email):
    usuario = get_object_or_404(Usuario, email=usuario_email)
    especialidad_alumno = None

    if hasattr(usuario, 'alumno'):
        alumno = usuario.alumno
        inscripcion = Inscripcion.objects.filter(alumno=alumno).first()

        if inscripcion:
            especialidad_alumno = inscripcion.especialidad
            proyectos_aprobados = ProyectoFinal.objects.filter(alumno=alumno, aprobado=True)

        return render(request, 'perfil.html', {'usuario': usuario, 'especialidad_alumno': especialidad_alumno, 'proyectos_aprobados': proyectos_aprobados})
    
    else:
        return render(request, 'perfil.html', {'usuario': usuario})
    
def ver_mas_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoFinal, pk=proyecto_id)
    imagenes_proyecto = ImagenProyecto.objects.filter(proyecto=proyecto)

    context = {
        'proyecto': proyecto,
        'imagenes_proyecto': imagenes_proyecto,
    }
    return render(request, 'detalles_proyecto.html', context)

def view_pdf(request, proyecto_id):
    proyecto = ProyectoFinal.objects.get(pk=proyecto_id)
    try:
        with open(proyecto.documento_pdf.path, 'rb') as pdf_file:
            response = FileResponse(pdf_file)
            return response
    except FileNotFoundError:
        return HttpResponseNotFound('El archivo PDF no se encontró en el servidor.')

def about_view(request):
    usuariosListados = Usuario.objects.all()
    alumnosListados = Alumno.objects.all()
    asesoresListados = AsesorEducativo.objects.all()
    return render(request,'about.html', {'usuarios': usuariosListados, 'asesores': asesoresListados, 'alumnos': alumnosListados})

@login_required
@csrf_exempt
def message_view(request, usuario_destino_id):
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '')
        usuario_destino = get_object_or_404(Usuario, id=usuario_destino_id)

        mensaje = Mensaje(emisor=request.user, receptor=usuario_destino, contenido=contenido)
        mensaje.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{usuario_destino_id}",
            {
                "type": "chat.message",
                "message": contenido,
                "usuario_emisor": request.user.email,
            },
        )

        return JsonResponse({'status': 'success'})

    usuario_destino = get_object_or_404(Usuario, id=usuario_destino_id)
    mensajes = Mensaje.objects.filter(
        (Q(emisor=request.user) & Q(receptor=usuario_destino)) | 
        (Q(emisor=usuario_destino) & Q(receptor=request.user))
    ).order_by('timestamp')

    return render(request, 'message.html', {'usuario_destino': usuario_destino, 'mensajes': mensajes})

@login_required
def cambiar_contrasena_view(request):
    form = CambiarContrasenaForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        contrasena_actual = form.cleaned_data['contrasena_actual']
        nueva_contrasena = form.cleaned_data['nueva_contrasena']
        confirmar_contrasena = form.cleaned_data['confirmar_contrasena']

        if request.user.check_password(contrasena_actual):
            if nueva_contrasena == confirmar_contrasena:
                request.user.set_password(nueva_contrasena)
                request.user.save()
                update_session_auth_hash(request, request.user) 
                messages.success(request, 'Contraseña cambiada exitosamente.')
                return redirect('profile') 
            else:
                messages.error(request, 'Las contraseñas no coinciden.')
        else:
            messages.error(request, 'La contraseña actual es incorrecta.')

    return render(request, 'cambiar_contrasena.html', {'form': form})

@login_required
def editar_nombre(request):
    if request.method == 'POST':
        form = EditarNombreForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nombre modificado exitosamente.')
            return redirect('profile') 
    else:
        form = EditarNombreForm(instance=request.user)

    return render(request, 'editar_nombre.html', {'form': form})

@login_required 
def editar_fecha_nacimiento(request):
    usuario = request.user
    form = EditarFechaNacimientoForm(instance=usuario)

    if request.method == 'POST':
        form = EditarFechaNacimientoForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fecha de nacimiento modificada exitosamente.')
            return redirect('profile')  
    else:
        form = EditarFechaNacimientoForm(instance=usuario)

    return render(request, 'editar_fecha_nacimiento.html', {'form': form})

@login_required  
def editar_sexo(request):
    usuario = request.user
    form = EditarSexoForm(instance=usuario)

    if request.method == 'POST':
        form = EditarSexoForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sexo modificado exitosamente.')
            return redirect('profile')
        else:
            form = EditarFechaNacimientoForm(instance=usuario)  

    return render(request, 'editar_sexo.html', {'form': form})

@login_required
def editar_direccion(request):
    if request.method == 'POST':
        form = EditarDireccionForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección modificada exitosamente.')
            return redirect('profile')
    else:
        form = EditarDireccionForm(instance=request.user)

    return render(request, 'editar_direccion.html', {'form': form})

@login_required 
@asesor_educativo_required 
def documentos_por_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    documentos = Documento.objects.filter(asignatura=asignatura)

    return render(request, 'documentos_por_asignatura.html', {'asignatura': asignatura, 'documentos': documentos})

@login_required
@asesor_educativo_required 
def registrar_documento(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.asignatura_id = asignatura_id
            documento.save()
            messages.success(request, 'Documento registrado exitosamente.')
            return redirect('index')
    else:
        form = DocumentoForm()

    return render(request, 'registrar_documento.html', {'form': form, 'asignatura': asignatura})

@login_required
@asesor_educativo_required
def editar_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento modificado exitosamente.')
            return redirect('index')
    else:
        form = DocumentoForm(instance=documento)

    return render(request, 'editar_documento.html', {'form': form, 'documento': documento})

@login_required
@asesor_educativo_required
def eliminar_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    if request.method == 'POST':
        documento.uploadedFile.delete()
        documento.delete()
        messages.success(request, 'Documento eliminado.')
        return redirect('index')

    return render(request, 'eliminar_documento.html', {'documento': documento})

@login_required
@asesor_educativo_required
def crear_asignacion_proyecto(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        instrucciones = request.POST['instrucciones']
        alumnos_seleccionados = request.POST.getlist('alumnos')
        print(alumnos_seleccionados)

        proyecto_asignacion = ProyectoAsignacion.objects.create(
            titulo=titulo,
            instrucciones=instrucciones,
            asesor=request.user.asesoreducativo,
            especialidad=request.user.asesoreducativo.especialidad
        )

        for correo_alumno in alumnos_seleccionados:
            usuario_alumno = Usuario.objects.get(email=correo_alumno)
            try:
                alumno = Alumno.objects.get(usuario=usuario_alumno)
            except Alumno.DoesNotExist:
                print(f"No se encontró el alumno asociado al usuario con correo: {correo_alumno}")
                continue
            ProyectoAlumno.objects.create(proyecto=proyecto_asignacion, alumno=alumno)

        messages.success(request, 'Proyecto asignado exitosamente.')
        return redirect('index')

    return render(request, 'crear_asignacion_proyecto.html')

@login_required
@asesor_educativo_required
def editar_proyecto_asignacion(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoAsignacion, id=proyecto_id)

    if request.method == 'GET':
        form = ProyectoAsignacionForm(instance=proyecto)
        return render(request, 'editar_proyecto_asignacion.html', {'form': form, 'proyecto': proyecto})
    
    if request.method == 'POST':
        form = ProyectoAsignacionForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proyecto actualizado exitosamente.')
            return redirect('index')

    return render(request, 'editar_proyecto_asignacion.html', {'form': form, 'proyecto': proyecto})

@login_required
@asesor_educativo_required
def eliminar_asignacion_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoAsignacion, id=proyecto_id)

    if proyecto.asesor != request.user.asesoreducativo:
        messages.error(request, 'No tienes permisos para eliminar este proyecto.')
        return redirect('index')

    if request.method == 'POST':
        proyecto.delete()
        messages.success(request, 'Proyecto alumno eliminado exitosamente.')
        return redirect('index')

    return render(request, 'eliminar_asignacion_proyecto.html', {'proyecto': proyecto})

@login_required
@asesor_educativo_required
def eliminar_proyecto_alumno(request, proyecto_id, alumno_id):
    proyecto_alumno = get_object_or_404(ProyectoAlumno, proyecto_id=proyecto_id, alumno_id=alumno_id)

    if request.method == 'POST':
        proyecto_alumno.delete()
        messages.success(request, 'Se eliminó de forma correcta la asignación.')
        return redirect('editar_proyecto_asignacion', proyecto_id=proyecto_id)

    return render(request, 'eliminar_proyecto_alumno.html', {'proyecto_alumno':proyecto_alumno})

@login_required
@asesor_educativo_required
def asignar_alumnos(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoAsignacion, id=proyecto_id)
    alumnos_disponibles = Alumno.objects.exclude(proyectoalumno__proyecto=proyecto)

    if request.method == 'POST':
        alumnos_seleccionados = request.POST.getlist('alumnos')
        for correo_alumno in alumnos_seleccionados:
            usuario_alumno = Usuario.objects.get(email=correo_alumno)
            try:
                alumno = Alumno.objects.get(usuario=usuario_alumno)
            except Alumno.DoesNotExist:
                print(f"No se encontró el alumno asociado al usuario con correo: {correo_alumno}")
                continue
            ProyectoAlumno.objects.create(proyecto=proyecto, alumno=alumno)

        return redirect('editar_proyecto_asignacion', proyecto_id=proyecto_id)

    return render(request, 'asignar_alumnos.html', {'proyecto': proyecto, 'alumnos_disponibles': alumnos_disponibles})

@login_required
def material_view(request):
    return render(request,'material.html')

@login_required 
def documentos_view(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    documentos = Documento.objects.filter(asignatura=asignatura)

    return render(request, 'documentos.html', {'asignatura': asignatura, 'documentos': documentos})

@login_required
def proyectos_asignados(request):
    alumno = request.user.alumno
    proyectos_asignados = ProyectoAlumno.objects.filter(alumno=alumno)
    
    return render(request, 'proyectos_asignados.html', {'proyectos_asignados': proyectos_asignados})

@login_required
def agregar_proyecto_final(request, proyecto_id):
    proyecto_asignado = get_object_or_404(ProyectoAsignacion, id=proyecto_id)

    proyecto_existente = ProyectoFinal.objects.filter(
        alumno=request.user.alumno,
        proyecto_asignado=proyecto_asignado
    ).first()
    
    if proyecto_existente:
        messages.warning(request, 'Ya has registrado tu Proyecto Final.')
        return redirect('proyectos_asignados')
    
    if request.method == 'POST':
        titulo = request.POST['titulo']
        descripcion = request.POST['descripcion']
        documento_pdf = request.FILES['documento_pdf']

        proyecto_final = ProyectoFinal.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            documento_pdf=documento_pdf,
            alumno=request.user.alumno,
            proyecto_asignado=proyecto_asignado
        )

        images = request.FILES.getlist('imagen')

        for i, image in enumerate(images, start=1):
            ImagenProyecto.objects.create(
                titulo=f'Imagen {i}',
                imagen=image,
                proyecto=proyecto_final
            )

        messages.success(request, 'Proyecto Final registrado correctamente.')
        return redirect('proyectos_asignados')
    return render(request, 'agregar_proyecto_final.html', {'proyecto_asignado': proyecto_asignado})

@login_required
def editar_telefono(request, telefono_id):
    telefono = get_object_or_404(Telefono, id=telefono_id)

    if request.method == 'POST':
        form = TelefonoForm(request.POST, instance=telefono)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teléfono editado correctamente.')
            return redirect('profile')
    else:
        form = TelefonoForm(instance=telefono)

    return render(request, 'editar_telefono.html', {'form': form})

@login_required
def editar_proyecto(request, proyecto_id):
    proyecto_asignado = get_object_or_404(ProyectoAsignacion, id=proyecto_id)

    proyecto = ProyectoFinal.objects.filter(
        alumno=request.user.alumno,
        proyecto_asignado=proyecto_asignado
    ).first()

    if proyecto is None:
        messages.warning(request, 'Primero registra tu Proyecto Final.')
        return redirect('proyectos_asignados')

    imagenes_proyecto = ImagenProyecto.objects.filter(proyecto=proyecto)

    if request.method == 'POST':
        form = ProyectoFinalForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proyecto editado correctamente.')
            return redirect('proyectos_asignados')
    else:
        form = ProyectoFinalForm(instance=proyecto)
    return render(request, 'editar_proyecto.html', {'form': form, 'imagenes_proyecto':imagenes_proyecto})

@login_required
def editar_imagen(request, imagen_id):
    imagen = get_object_or_404(ImagenProyecto, pk=imagen_id)
    
    if request.method == 'POST':
        if 'imagen' in request.FILES:
            imagen_nueva = request.FILES['imagen']
            imagen.imagen = imagen_nueva
            imagen.save()
            messages.success(request, 'Imagen editada correctamente.')
            return redirect('proyectos_asignados')
        else:
            messages.error(request, 'No se proporcionó ninguna imagen para editar.')
    
    return render(request, 'editar_imagen.html', {'imagen': imagen})

@login_required
@asesor_educativo_required
def aprobar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoFinal, id=proyecto_id)
    proyecto.aprobado = True
    proyecto.save()
    messages.success(request, 'Proyecto Aprobado correctamente.')
    return redirect('index')

@login_required
def ver_calificaciones(request):
    calificaciones = Calificacion.objects.filter(alumno=request.user.alumno)
    return render(request, 'ver_calificaciones.html', {'calificaciones': calificaciones})

@login_required
@asesor_educativo_required
def index_view(request):
    return render(request,'index.html')

def index_or_home_view(request):
    if hasattr(request.user, 'asesoreducativo'):
        return redirect('index')
    else:
        return home_view(request)    

def inscripcion_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomAlumnoCreationForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            sexo = str(form.cleaned_data['sexo'])
            matricula = form.matricula_generada
            
            confirmation_mail = create_mail(
                    email,
                    'Correo de confirmación',
                    'mails/info.html',
                    {
                        'nombre': nombre,
                        'matricula': matricula,
                        'sexo': sexo,
                    }
                )
            try:
                confirmation_mail.send(fail_silently=False)
            except Exception as e:
                print(f"Error al enviar correo de confirmación: {e}")
                messages.warning(request, 'Hubo un problema al enviar el correo de confirmación.')
            form.save()
            messages.success(request, '¡Registro exitoso! En breve te llegará un correo con más información.')
            return redirect('login')
        else: 
            print(f"Errores en el formulario: {form.errors}")
            messages.error(request, 'Hubo un problema al procesar el formulario. Por favor, revisa los errores.')
    else:
        form = CustomAlumnoCreationForm()
    
    return render(request,'inscripcion.html', {'form': form})

def asesor_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomAsesorCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso!')
            return redirect('login')
        else: 
            print(f"Errores en el formulario: {form.errors}")
            messages.error(request, 'Hubo un problema al procesar el formulario. Por favor, revise los datos.')
    else:
        form = CustomAsesorCreationForm()
    
    return render(request,'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                if hasattr(user, 'alumno'):
                    messages.success(request, '¡Bienvenido! Sesión iniciada.')
                    return redirect('home')
                elif hasattr(user, 'asesoreducativo'):
                    messages.success(request, '¡Bienvenido! Sesión iniciada.')
                    return redirect('index')
            else:
                messages.error(request, 'Error, usuario o contraseña incorrecto.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def especialidad_view(request, nombre):
    especialidad = get_object_or_404(Especialidad, nombre=nombre)
    asignaturas = especialidad.asignaturas.all()
    return render(request, 'especialidad.html', {'especialidad': especialidad, 'asignaturas': asignaturas})

@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy('profile')
    template_name = "profile_form.html"

    def get_object(self, queryset=None):
        try:
            return Profile.objects.get(usuario=self.request.user)
        except Profile.DoesNotExist:
            return Profile.objects.create(usuario=self.request.user)

@method_decorator(login_required, name='dispatch')
class EmailUpdate(UpdateView):
    form_class = EmailForm
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user
    
    def get_form(self, form_class=None):
        form = super(EmailUpdate, self).get_form()
        form.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control mb-2', 'placeholder':'Email'})
        return form
    
    template_name = "profile_email_form.html"

@login_required
def confirmar_eliminar_foto(request):
    if request.method == 'GET':
        return render(request, 'confirmar_eliminar_foto.html')

    elif request.method == 'POST':
        profile = request.user.profile
        avatar_path = profile.avatar.path

        if avatar_path:
            default_storage.delete(avatar_path)

        profile.avatar = None
        profile.save()

        messages.success(request, 'La foto de perfil ha sido eliminada correctamente.')
        return redirect('profile')

def galery_view(request):

    return render(request, 'galery.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def obtener_municipios(request):
    estado_id = request.GET.get('estado_id')
    municipios = Municipio.objects.filter(estado_id=estado_id).order_by('nombre')
    municipios_data = [{'id': municipio.id, 'nombre': municipio.nombre} for municipio in municipios]
    return JsonResponse({'municipios': municipios_data})

def obtener_localidades(request):
    municipio_id = request.GET.get('municipio_id')
    localidades = Localidad.objects.filter(municipio_id=municipio_id).order_by('nombre')
    localidades_data = [{'id': localidad.id, 'nombre': localidad.nombre, 'codigoPostal': localidad.codigoPostal} for localidad in localidades]
    return JsonResponse({'localidades': localidades_data})

def obtener_codigo_postal(request):
    localidad_id = request.GET.get('localidad_id')
    
    try:
        localidad = Localidad.objects.get(id=localidad_id)
        codigo_postal = localidad.codigoPostal
        data = {'codigoPostal': codigo_postal}
        return JsonResponse(data)
    except Localidad.DoesNotExist:
        data = {'error': 'Localidad no encontrada'}
        return JsonResponse(data, status=404)

def create_mail(email, subject, template_path, context):
    template = get_template(template_path)
    content = template.render(context)

    mail = EmailMultiAlternatives(
        subject = subject,
        body = '',
        from_email = settings.EMAIL_HOST_USER,
        to = {
            email
        },
        cc = []
    )
    mail.attach_alternative(content, 'text/html')
    return mail

@receiver(post_save, sender=Inscripcion)
def enviar_correo_aceptacion(sender, instance, **kwargs):
    if instance.aceptada:
        try:
            usuario = instance.alumno.usuario
            email = usuario.email
            nombre = usuario.nombre
            sexo = str(usuario.sexo)
            matricula = usuario.alumno.matricula

            salt = hashlib.sha1(str(random.random()).encode()).hexdigest()[:5]  
            activation_key = hashlib.sha1((salt + email).encode()).hexdigest()         
            key_expires = date.today() + timezone.timedelta(2)

            usuario.activation_key = activation_key
            usuario.key_expires = key_expires
            usuario.save()

            reset_password_link = reverse('set_password', kwargs={'email': email, 'activation_key': activation_key})

            enviar_correo_aceptacion = create_mail(
            email,
            'Correo de aceptación de inscripción',
            'mails/aceptacion.html',
            {
                'nombre': nombre,
                'matricula': matricula,
                'sexo': sexo,
                'reset_password_link': reset_password_link,
            }
            )
            enviar_correo_aceptacion.send(fail_silently=False)
        except Usuario.DoesNotExist:
            pass
            print('No se encontró un usuario asociado a la inscripción.')

def set_password_view(request, email, activation_key):
    UserModel = get_user_model()
    usuario = get_object_or_404(Usuario, activation_key=activation_key)

    if usuario.key_expires < timezone.now():
        messages.error(request, 'Error, el link ha expirado.')
        return redirect('login')

    if request.method == 'POST':

        form = SetPasswordForm(request.POST)

        if form.is_valid():
                
            form.save(UserModel.objects.get(email=email))
            messages.success(request, '¡Se estableció su contraseña! Ya puede iniciar sesión.')
            return redirect('login')
    else:
        form = SetPasswordForm()

    return render(request, 'reset.html', {'form': form, 'email': email, 'activation_key': activation_key})
