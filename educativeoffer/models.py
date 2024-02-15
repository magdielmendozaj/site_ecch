from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage

# Create your models here.

class Escuela(models.Model):
    nombre = models.CharField(max_length=50)
    calle = models.CharField(max_length=20)
    numero = models.IntegerField()
    localidad = models.ForeignKey('Localidad', on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    username_facebook = models.CharField(unique=True, max_length=128)
    username_instagram = models.CharField(unique=True, max_length=128)
    username_twitter = models.CharField(unique=True, max_length=128)
    username_youtube = models.CharField(unique=True, max_length=128)
    mision = models.CharField(max_length=300, unique=True)
    vision = models.CharField(max_length=300, unique=True)
    telefonos = models.CharField(max_length=50, unique=True, null=True, blank=True) 

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural=u'Datos de la escuela' 

class Valor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural=u'Valores' 

class Estado(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural=u'Estados'

class Municipio(models.Model):
    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey('Estado', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural=u'Municipios'

class Localidad(models.Model):
    nombre = models.CharField(max_length=200)
    municipio = models.ForeignKey('Municipio', on_delete=models.CASCADE)
    codigoPostal = models.IntegerField(5, default=00000)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural=u'Localidades'

class Sexo(models.Model):
    descripcion = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.descripcion
    
    class Meta:
        verbose_name_plural=u'Sexos'
    
class MedioContacto(models.Model):
    descripcion = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.descripcion
    
    class Meta:
        verbose_name_plural=u'Medios de Contacto'

def custom_upload_to_es(instance, filename):
    if instance.pk:
        try:
            old_instance = Especialidad.objects.get(pk=instance.pk)
            old_instance.imagen.delete()
        except Especialidad.DoesNotExist:
            pass
    return 'desc/' + filename

class Especialidad(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=350)
    imagen = models.ImageField(upload_to=custom_upload_to_es, null=True, blank=True)
    DIVISION_PERIODO = [
        ('4', 'Cuartrimestre'),
        ('6', 'Semestre'),
    ]
    
    division = models.CharField(max_length=1, choices=DIVISION_PERIODO, null=True, blank=True, help_text="Meses de duración de cada periodo")
    num_periodo = models.IntegerField(null=True, blank=True, help_text="El número de periodos que consta la carrera")

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural=u'Especialidades'

@receiver(pre_delete, sender=Especialidad)
def especialidad_delete(sender, instance, **kwargs):
    if instance.imagen:
        default_storage.delete(instance.imagen.path)

class Asignatura(models.Model):
    nombre = models.CharField(max_length=180)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.SET_NULL, null=True, related_name='asignaturas')
    periodo = models.IntegerField(null=True, blank=True, help_text="Periodo de la carrera al que pertenece la asignatura")
    habilitada = models.BooleanField(default=True, null=True, help_text="Habilitar o deshabilitar las asignaturas")

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural=u'Asignaturas'
        unique_together = ('nombre', 'especialidad','periodo')

class Categoria(models.Model):
    descripcion = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.descripcion
    
    class Meta:
        verbose_name_plural=u'Categorías'

def custom_upload_to_do(instance, filename):
    if instance.pk:
        try:
            old_instance = Documento.objects.get(pk=instance.pk)
            old_instance.uploadedFile.delete()
        except Documento.DoesNotExist:
            pass
    return 'files/' + filename

class Documento(models.Model):
    titulo = models.CharField(max_length=120, unique=True)
    descripcion = models.CharField(max_length=300, null=True, blank=True)
    uploadedFile = models.FileField(upload_to=custom_upload_to_do)
    dateTimeOfUpload = models.DateTimeField(auto_now=True)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name_plural=u'Documentos'

@receiver(pre_delete, sender=Documento)
def documento_delete(sender, instance, **kwargs):
    if instance.uploadedFile:
        default_storage.delete(instance.uploadedFile.path)

def custom_upload_to_ga(instance, filename):
    if instance.pk:
        try:
            old_instance = Galeria.objects.get(pk=instance.pk)
            old_instance.imagen.delete()
        except Galeria.DoesNotExist:
            pass
    return 'galery/' + filename

class Galeria(models.Model):
    titulo = models.CharField(max_length=120)
    imagen = models.ImageField(upload_to=custom_upload_to_ga, null=True, blank=True)
    habilitada = models.BooleanField(default=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name_plural=u'Galería'

@receiver(pre_delete, sender=Galeria)
def galeria_delete(sender, instance, **kwargs):
    if instance.imagen:
        default_storage.delete(instance.imagen.path)

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo de correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=50)
    apellidoPaterno = models.CharField(max_length=50)
    apellidoMaterno = models.CharField(max_length=50)
    fechaNacimiento = models.DateField()
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    calle = models.CharField(max_length=100)
    n_int = models.IntegerField()
    n_ext = models.IntegerField()
    localidad = models.ForeignKey('Localidad', on_delete=models.CASCADE)
    sexo = models.ForeignKey('Sexo', on_delete=models.CASCADE)

    register_date = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=timezone.now)

    groups = models.ManyToManyField(
        'auth.Group', 
        blank=True,
        related_name='user_groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_permissions',
        blank=True,
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellidoPaterno', 'apellidoMaterno', 'fechaNacimiento', 'calle', 'n_int', 'n_ext', 'localidad', 'sexo']

    def __str__(self):
        return str(self.email)
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellidoPaterno} {self.apellidoMaterno}"
    
    class Meta:
        verbose_name_plural=u'Usuarios'

class Alumno(models.Model):
    matricula = models.CharField(primary_key=True, max_length=12, unique=True, help_text="Mátricula única para el alumno")
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    medioContacto = models.ForeignKey('MedioContacto', on_delete=models.CASCADE)
    status = models.BooleanField(default=True, help_text="En caso de dar de baja al alumno, desmarcar")

    def __str__(self):
        return str(self.usuario.email)

    class Meta:
        verbose_name_plural=u'Alumnos'

class Inscripcion(models.Model):
    folio = models.IntegerField(unique=True)
    aceptada = models.BooleanField(default=False)
    periodo = models.CharField(max_length=7)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE)
    asesor = models.ForeignKey('AsesorEducativo', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.alumno.usuario.email)

    class Meta:
        verbose_name_plural=u'Inscripciones'

class AsesorEducativo(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    cedula = models.CharField(max_length=45, unique=True)
    GRADO_ACADEMICO_CHOICES = [
        ('Licenciatura', 'Licenciatura'),
        ('Maestría', 'Maestría'),
        ('Doctorado', 'Doctorado'),
    ]
    
    grado_academico = models.CharField(max_length=20, choices=GRADO_ACADEMICO_CHOICES)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.usuario.email)

    class Meta:
        verbose_name_plural=u'Asesores Educativos'

def custom_upload_to(instance, filename):
    if instance.pk:
        try:
            old_instance = Profile.objects.get(pk=instance.pk)
            old_instance.avatar.delete()
        except Profile.DoesNotExist:
            pass
    return 'profiles/' + filename

class Profile(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=custom_upload_to, null=True, blank=True)
    bio = models.TextField(null=True, blank=True, max_length=128)
    username_facebook = models.CharField(unique=True, max_length=128, null=True, blank=True)
    username_instagram = models.CharField(unique=True, max_length=128, null=True, blank=True)
    username_twitter = models.CharField(unique=True, max_length=128, null=True, blank=True)
    username_youtube = models.CharField(unique=True, max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.usuario.email)

    class Meta:
        verbose_name_plural=u'Perfiles'

@receiver(pre_delete, sender=Profile)
def profile_delete(sender, instance, **kwargs):
    if instance.avatar:
        default_storage.delete(instance.avatar.path)

class Telefono(models.Model):
    telefono = models.IntegerField(unique=True)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.usuario.email)

    class Meta:
        verbose_name_plural=u'Teléfonos'

class Calificacion(models.Model):
    asesor = models.ForeignKey('AsesorEducativo', on_delete=models.CASCADE)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    periodo = models.CharField(max_length=7)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.alumno.usuario.email} - {self.asignatura.nombre} - {self.periodo}"

    class Meta:
        verbose_name_plural = u'Calificaciones'
        unique_together = ('asesor', 'alumno', 'asignatura')

class Aviso(models.Model):
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    disponible = models.BooleanField(default=True, help_text="Desmarcar para que no aparezca en la notificaciones.")
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name_plural=u'Avisos'

class Mensaje(models.Model):
    emisor = models.ForeignKey(Usuario, related_name='mensajes_enviados', on_delete=models.CASCADE)
    receptor = models.ForeignKey(Usuario, related_name='mensajes_recibidos', on_delete=models.CASCADE)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emisor} a {self.receptor} - {self.timestamp}"

class ProyectoAsignacion(models.Model):
    titulo = models.CharField(max_length=100)
    instrucciones = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    asesor = models.ForeignKey('AsesorEducativo', on_delete=models.CASCADE)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = 'Asignación de Proyectos'

class ProyectoAlumno(models.Model):
    proyecto = models.ForeignKey(ProyectoAsignacion, on_delete=models.CASCADE)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)

    def __str__(self):
        return f'Relación: Proyecto - {self.proyecto.titulo} / Alumno - {self.alumno.usuario.get_full_name()}'

    class Meta:
        verbose_name_plural = 'Relación Proyectos - Alumno'
        unique_together = ('proyecto', 'alumno')

def custom_upload_to_pf(instance, filename):
    if instance.pk:
        try:
            old_instance = ProyectoFinal.objects.get(pk=instance.pk)
            old_instance.documento_pdf.delete()
        except ProyectoFinal.DoesNotExist:
            pass
    return 'proyectos/pdfs/' + filename

class ProyectoFinal(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    documento_pdf = models.FileField(upload_to=custom_upload_to_pf)
    aprobado = models.BooleanField(default=False)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    proyecto_asignado = models.OneToOneField('ProyectoAsignacion', on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = 'Proyectos Finales'
        unique_together = ('alumno', 'proyecto_asignado')

def custom_upload_to_pi(instance, filename):
    if instance.pk:
        try:
            old_instance = ImagenProyecto.objects.get(pk=instance.pk)
            old_instance.imagen.delete()
        except ImagenProyecto.DoesNotExist:
            pass
    return 'proyectos/imagenes/' + filename

class ImagenProyecto(models.Model):
    titulo = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to=custom_upload_to_pi)
    proyecto = models.ForeignKey('ProyectoFinal', on_delete=models.CASCADE)

    def __str__(self):
        return f'Relación: Proyecto - {self.proyecto.titulo} - {self.titulo}'

    class Meta:
        verbose_name_plural = 'Imágenes de Proyectos Finales'

@receiver(post_save, sender=Usuario)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        Profile.objects.create(usuario=instance)

@receiver(post_save, sender=Usuario)
def save_user_profile(sender, instance, **kwargs):
    if not instance.is_superuser:
        instance.profile.save()
