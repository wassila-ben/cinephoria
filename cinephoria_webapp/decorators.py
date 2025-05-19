from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def employee_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('login')
        if not request.user.is_staff or request.user.is_superuser:
            messages.error(request, "Accès réservé aux employés.")
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view