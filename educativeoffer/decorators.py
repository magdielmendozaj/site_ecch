from functools import wraps
from django.shortcuts import redirect

def is_asesor_educativo(user):
    return hasattr(user, 'asesoreducativo')

def asesor_educativo_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_asesor_educativo(request.user):
            return redirect('home')  
        return view_func(request, *args, **kwargs)
    return _wrapped_view