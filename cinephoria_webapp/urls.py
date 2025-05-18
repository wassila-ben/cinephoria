from . import views
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from cinephoria_webapp import views_admin


urlpatterns = [
    path('', views.index, name='index'),
    path('base/', views.base, name='base'),
    path('film/<int:film_id>/', views.details_film, name='details_film'),
    path('films/', views.films_view, name='films'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path("reset-password/", auth_views.PasswordResetView.as_view(
        template_name="cinephoria_webapp/password_reset.html"
    ), name="password_reset"),

    path("reset-password/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="cinephoria_webapp/password_reset_done.html"
    ), name="password_reset_done"),

    path("reset-password/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="cinephoria_webapp/password_reset_confirm.html"
    ), name="password_reset_confirm"),

    path("reset-password/complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name="cinephoria_webapp/password_reset_complete.html"
    ), name="password_reset_complete"),
    path("choisir_cinema/", views.choisir_cinema, name="choisir_cinema"),

    path('reservation/', views.reservation, name='reservation'),
    path('admin-panel/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/films/', views_admin.film_list, name='admin_film_list'),
    path('admin-panel/films/create/', views_admin.film_create, name='admin_film_create'),
    path('admin-panel/films/<int:film_id>/edit/', views_admin.film_update, name='admin_film_edit'),
    path('admin-panel/films/<int:film_id>/delete/', views_admin.film_delete, name='admin_film_delete'),
    path('seances/', views_admin.seance_list, name='admin_seance_list'),
    path('seances/create/', views_admin.seance_create, name='admin_seance_create'),
    path('seances/<int:seance_id>/edit/', views_admin.seance_update, name='admin_seance_edit'),
    path('seances/<int:seance_id>/delete/', views_admin.seance_delete, name='admin_seance_delete'),
    path('salles/', views_admin.salle_list, name='admin_salle_list'),
    path('salles/create/', views_admin.salle_create, name='admin_salle_create'),
    path('salles/<int:salle_id>/edit/', views_admin.salle_update, name='admin_salle_edit'),
    path('salles/<int:salle_id>/delete/', views_admin.salle_delete, name='admin_salle_delete'),
    path('employes/create/', views_admin.employe_create, name='admin_employe_create'),
    path('employes/reset-password/', views_admin.employe_reset_password, name='admin_employe_reset_password'),
    path('dashboard/', views_admin.dashboard_reservations, name='admin_dashboard_reservations'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)