from pyexpat.errors import messages
from django import forms
from django.forms import widgets
from .models import Especialidad, Sexo, MedioContacto, Estado, Municipio, Localidad, Inscripcion, Telefono, Profile, Usuario, Alumno, AsesorEducativo, Documento, ProyectoAsignacion, ProyectoFinal, ImagenProyecto

from datetime import datetime 
import secrets
import string

class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={'class': 'form__input', 'placeholder': 'Correo electrónico'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form__input', 'placeholder': 'Contraseña'}))

class CustomAlumnoCreationForm(forms.ModelForm):
    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ejemplo.com'}))
    nombre = forms.CharField(label='Nombre(s)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre'}))
    apellidoPaterno = forms.CharField(label='Apellido Paterno', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu apellido paterno'}))
    apellidoMaterno = forms.CharField(label='Apellido Materno', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu apellido materno'}))
    fechaNacimiento = forms.DateField(label='Fecha de nacimiento', widget=widgets.DateInput(attrs={'class': 'form-control','type': 'date', 'placeholder': 'Ingresa tu fecha de nacimiento'}))
    numTelefonico = forms.IntegerField(label='Teléfono', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu número telefónico'}))
    calle = forms.CharField(label='Calle', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu calle'}))
    n_int = forms.IntegerField(label='Número Interior', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu número interior'}))
    n_ext = forms.IntegerField(label='Número Exterior', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu número exterior'}))
        
    especialidad = forms.ModelChoiceField(label='Selecciona tu especialidad', queryset=Especialidad.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    sexo = forms.ModelChoiceField(label='Selecciona tu sexo', queryset=Sexo.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    estado = forms.ModelChoiceField(label='Selecciona tu Estado', queryset=Estado.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_estado'}))
    municipio = forms.ModelChoiceField(label='Selecciona tu Municipio', queryset=Municipio.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_municipio'}))
    localidad = forms.ModelChoiceField(label='Selecciona tu Localidad', queryset=Localidad.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_localidad'}))
    medioContacto = forms.ModelChoiceField(label='Selecciona cómo supiste de nosotros', queryset=MedioContacto.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'apellidoPaterno', 'apellidoMaterno', 'fechaNacimiento', 'calle', 'n_int', 'n_ext', 'localidad', 'sexo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matricula_generada = generar_matricula()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(generar_contraseña())
        if commit:
            user.save()
            alumno = Alumno(
                matricula = self.matricula_generada, 
                usuario=user, 
                medioContacto=self.cleaned_data['medioContacto'])
            alumno.save()
            inscripcion = Inscripcion(
                folio=generar_folio(),
                periodo=generar_periodo(self.cleaned_data['especialidad']),
                alumno=alumno,
                especialidad=self.cleaned_data['especialidad']
            )
            inscripcion.save()
            telefono = Telefono(
                telefono=self.cleaned_data['numTelefonico'],
                usuario=user,
            )
            telefono.save()
        return user
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not nombre.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de nombre.")
        return nombre

    def clean_apellidoPaterno(self):
        apellidoPaterno = self.cleaned_data['apellidoPaterno']
        if not apellidoPaterno.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de apellido paterno.")
        return apellidoPaterno

    def clean_apellidoMaterno(self):
        apellidoMaterno = self.cleaned_data['apellidoMaterno']
        if not apellidoMaterno.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de apellido materno.")
        return apellidoMaterno

class CustomAsesorCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}))

    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ejemplo.com'}))
    nombre = forms.CharField(label='Nombre(s)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre'}))
    apellidoPaterno = forms.CharField(label='Apellido Paterno', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su apellido paterno'}))
    apellidoMaterno = forms.CharField(label='Apellido Materno', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su apellido materno'}))
    fechaNacimiento = forms.DateField(label='Fecha de nacimiento', widget=widgets.DateInput(attrs={'class': 'form-control','type': 'date', 'placeholder': 'Ingrese su fecha de nacimiento'}))
    numTelefonico = forms.IntegerField(label='Teléfono', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su número telefónico'}))
    calle = forms.CharField(label='Calle', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su calle'}))
    n_int = forms.IntegerField(label='Número Interior', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su número interior'}))
    n_ext = forms.IntegerField(label='Número Exterior', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su número exterior'}))
    cedula = forms.CharField(label='Cédula profesional', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su cédula profesional'}))
        
    grado_academico = forms.ChoiceField(label='Seleccione su grado académico',choices=AsesorEducativo.GRADO_ACADEMICO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    especialidad = forms.ModelChoiceField(label='Seleccione la especialidad', queryset=Especialidad.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    sexo = forms.ModelChoiceField(label='Seleccione su sexo', queryset=Sexo.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    estado = forms.ModelChoiceField(label='Seleccione su Estado', queryset=Estado.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_estado'}))
    municipio = forms.ModelChoiceField(label='Seleccione su Municipio', queryset=Municipio.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_municipio'}))
    localidad = forms.ModelChoiceField(label='Seleccione su Localidad', queryset=Localidad.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_localidad'}))

    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'apellidoPaterno', 'apellidoMaterno', 'fechaNacimiento', 'calle', 'n_int', 'n_ext', 'localidad', 'sexo']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            asesor = AsesorEducativo(
                usuario=user, 
                cedula=self.cleaned_data['cedula'],
                grado_academico=self.cleaned_data['grado_academico'],
                especialidad=self.cleaned_data['especialidad'],
            )
            asesor.save()
            telefono = Telefono(
                telefono=self.cleaned_data['numTelefonico'],
                usuario=user,
            )
            telefono.save()
        return user
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not nombre.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de nombre.")
        return nombre

    def clean_apellidoPaterno(self):
        apellidoPaterno = self.cleaned_data['apellidoPaterno']
        if not apellidoPaterno.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de apellido paterno.")
        return apellidoPaterno

    def clean_apellidoMaterno(self):
        apellidoMaterno = self.cleaned_data['apellidoMaterno']
        if not apellidoMaterno.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de apellido materno.")
        return apellidoMaterno

class SetPasswordForm(forms.Form):
    password1 = forms.CharField(max_length=128, widget=forms.PasswordInput(attrs={'class': 'form__input', 'placeholder': 'Ingresa tu contraseña'}))
    password2 = forms.CharField(max_length=128, widget=forms.PasswordInput(attrs={'class': 'form__input', 'placeholder': 'Confirma tu contraseña'}))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, user, commit=True):
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'username_facebook', 'username_instagram', 'username_twitter', 'username_youtube']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class':'form-control-file mt-3'}),
            'bio': forms.Textarea(attrs={'class':'form-control mt-3', 'rows':3, 'placeholder':'Biografía'}),
            'username_facebook': forms.TextInput(attrs={'class':'form-control mt-3','placeholder':'Usuario de Facebook'}),
            'username_instagram': forms.TextInput(attrs={'class':'form-control mt-3','placeholder':'Usuario de Instagram'}),
            'username_twitter': forms.TextInput(attrs={'class':'form-control mt-3','placeholder':'Usuario de Twitter'}),
            'username_youtube': forms.TextInput(attrs={'class':'form-control mt-3','placeholder':'Canal de YouTube'}),
        }

class EmailForm(forms.ModelForm):
    email = forms.EmailField(required=True, max_length=254,
        help_text="Requerido. 254 carácteres como máximo y debe ser un email válido.")
    
    class Meta:
        model = Usuario
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class':'form-control mt-3'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if 'email' in self.changed_data:
            if Usuario.objects.filter(email=email).exists():
                raise forms.ValidationError(u'El email ya está registrado, prueba con otro.')
            return email

class CambiarContrasenaForm(forms.Form):
    contrasena_actual = forms.CharField(label='Contraseña Actual', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nueva_contrasena = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_contrasena = forms.CharField(label='Confirmar Nueva Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class EditarNombreForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellidoPaterno', 'apellidoMaterno']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control mt-3','placeholder':'Nombre(s)','label':'Nombre:'}),
            'apellidoPaterno': forms.TextInput(attrs={'class':'form-control mt-3','placeholder':'Apellido Paterno','label':'Apellido Paterno:'}),
            'apellidoMaterno': forms.TextInput(attrs={'class':'form-control mt-3','placeholder':'Apellido Materno','label':'Apellido Materno:'}),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not nombre.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de nombre.")
        return nombre

    def clean_apellidoPaterno(self):
        apellidoPaterno = self.cleaned_data['apellidoPaterno']
        if not apellidoPaterno.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de apellido paterno.")
        return apellidoPaterno

    def clean_apellidoMaterno(self):
        apellidoMaterno = self.cleaned_data['apellidoMaterno']
        if not apellidoMaterno.isalpha():
            raise forms.ValidationError("Por favor, ingresa solo letras en el campo de apellido materno.")
        return apellidoMaterno

class EditarFechaNacimientoForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['fechaNacimiento']
        widgets = {
            'fechaNacimiento': forms.DateInput(attrs={'class': 'form-control mt-3', 'type': 'date', 'placeholder': 'Fecha de Nacimiento'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(EditarFechaNacimientoForm, self).__init__(*args, **kwargs)
        self.fields['fechaNacimiento'].initial = self.instance.fechaNacimiento.strftime('%Y-%m-%d') if self.instance.fechaNacimiento else None

class EditarSexoForm(forms.ModelForm):
    sexo = forms.ModelChoiceField(
        label='Seleccione su sexo',
        queryset=Sexo.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Usuario
        fields = ['sexo']

class EditarDireccionForm(forms.ModelForm):
    calle = forms.CharField(label='Calle', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su calle'}))
    n_int = forms.IntegerField(label='Número Interior', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su número interior'}))
    n_ext = forms.IntegerField(label='Número Exterior', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su número exterior'}))

    estado = forms.ModelChoiceField(label='Seleccione su Estado', queryset=Estado.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_estado'}))
    municipio = forms.ModelChoiceField(label='Seleccione su Municipio', queryset=Municipio.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_municipio'}))
    localidad = forms.ModelChoiceField(label='Seleccione su Localidad', queryset=Localidad.objects.all(), widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_localidad'}))
    
    class Meta:
        model = Usuario
        fields = ['calle', 'n_int', 'n_ext', 'localidad']

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'uploadedFile']
        widgets = {
            'titulo': forms.TextInput(attrs={'label':'Ingrese el título','class':'form-control mt-3','placeholder':'Título'}),
            'descripcion': forms.TextInput(attrs={'label':'Ingrese una decripción','class':'form-control mt-3','placeholder':'Descripción'}),
            'uploadedFile': forms.ClearableFileInput(attrs={'label':'Seleccione un archivo','class':'form-control-file mt-3'}),
        }

class ProyectoAsignacionForm(forms.ModelForm):
    class Meta:
        model = ProyectoAsignacion
        fields = ['titulo', 'instrucciones'] 
        widgets = {
            'titulo': forms.TextInput(attrs={'label':'Título:','class':'form-control mt-3','placeholder':'Título'}),
            'instrucciones': forms.Textarea(attrs={'label':'Instrucciones:','class':'form-control mt-3','placeholder':'Instrucciones', 'rows':'3'}),
        }

class TelefonoForm(forms.ModelForm):
    class Meta:
        model = Telefono
        fields = ['telefono']
        widgets = {
            'telefono': forms.NumberInput(attrs={'label':'Teléfono:','class':'form-control mt-3','placeholder':'Teléfono'}),
        }

class ProyectoFinalForm(forms.ModelForm):
    class Meta:
        model = ProyectoFinal
        fields = ['titulo', 'descripcion', 'documento_pdf']
        widgets = {
            'titulo': forms.TextInput(attrs={'label':'Título:','class':'form-control mt-3','placeholder':'Título'}),
            'descripcion': forms.Textarea(attrs={'label':'Instrucciones:','class':'form-control mt-3','placeholder':'Instrucciones', 'rows':'3'}),
            'documento_pdf': forms.ClearableFileInput(attrs={'label':'Seleccione un documento','class':'form-control-file mt-3'}),
        }

class EditarImagenForm(forms.ModelForm):
    class Meta:
        model = ImagenProyecto
        fields = ['imagen']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'label':'Selecciona una imagen','class':'form-control-file mt-3'}),
        }

def generar_matricula():
    año_actual = str(datetime.now().year)
    registros_del_año = Alumno.objects.filter(matricula__startswith=año_actual)
    numero_secuencial = registros_del_año.count() + 1
    matricula = f"{año_actual}{numero_secuencial:04d}"
    return matricula

def generar_contraseña():
    longitud = 12 
    caracteres = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    return password

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

def generar_folio():
    try:
        ultimo_registro = Inscripcion.objects.latest('folio')
        ultimo_numero = int(ultimo_registro.folio)
    except Inscripcion.DoesNotExist:
        ultimo_numero = 0

    nuevo_numero = ultimo_numero + 1
    folio = f"{nuevo_numero:05d}"
    return folio