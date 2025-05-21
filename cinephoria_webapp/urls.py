from . import views
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from cinephoria_webapp import views_admin, views_employee, views_api


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
    path('api/seance-infos/', views_api.get_seance_infos, name='get_seance_infos'),
    path('reservation/choix_sièges/', views.choix_sieges, name='choix_sieges'),
    path('reservation/confirmation/', views.reservation_confirmation, name='reservation_confirmation'),

    # espace Admin
    path('admin-panel/', views_admin.admin_dashboard, name='admin_dashboard'),

    # CRUD pour les films
    path('admin-panel/films/', views_admin.film_list, name='admin_film_list'),
    path('admin-panel/films/create/', views_admin.film_create, name='admin_film_create'),
    path('admin-panel/films/<int:film_id>/edit/', views_admin.film_update, name='admin_film_edit'),
    path('admin-panel/films/<int:film_id>/delete/', views_admin.film_delete, name='admin_film_delete'),
    # CRUD pour les séances
    path('seances/', views_admin.seance_list, name='admin_seance_list'),
    path('seances/create/', views_admin.seance_create, name='admin_seance_create'),
    path('seances/<int:seance_id>/edit/', views_admin.seance_update, name='admin_seance_edit'),
    path('seances/<int:seance_id>/delete/', views_admin.seance_delete, name='admin_seance_delete'),
    # CRUD pour les salles
    path('salles/', views_admin.salle_list, name='admin_salle_list'),
    path('salles/create/', views_admin.salle_create, name='admin_salle_create'),
    path('salles/<int:salle_id>/edit/', views_admin.salle_update, name='admin_salle_edit'),
    path('salles/<int:salle_id>/delete/', views_admin.salle_delete, name='admin_salle_delete'),

    # Gestion des employés
    path('employes/create/', views_admin.employe_create, name='admin_employe_create'),
    path('employes/reset-password/', views_admin.employe_reset_password, name='admin_employe_reset_password'),

    # Dashboard réservations
    path('dashboard/', views_admin.dashboard_reservations, name='admin_dashboard_reservations'),

    # Espace employé
    path('intranet/', views_employee.employee_dashboard, name='employee_dashboard'),

    # Accueil espace employé
    path('intranet/', views_employee.employee_dashboard, name='employee_dashboard'),

    # CRUD pour les films
    path('intranet/films/', views_employee.employee_film_list, name='employee_film_list'),
    path('intranet/films/ajouter/', views_employee.employee_film_create, name='employee_film_create'),
    path('intranet/films/<int:film_id>/modifier/', views_employee.employee_film_update, name='employee_film_update'),
    path('intranet/films/<int:film_id>/supprimer/', views_employee.employee_film_delete, name='employee_film_delete'),

    # CRUD pour les séances 
    path('intranet/seances/', views_employee.employee_seance_list, name='employee_seance_list'),
    path('intranet/seances/ajouter/', views_employee.employee_seance_create, name='employee_seance_create'),
    path('intranet/seances/<int:seance_id>/modifier/', views_employee.employee_seance_update, name='employee_seance_update'),
    path('intranet/seances/<int:seance_id>/supprimer/', views_employee.employee_seance_delete, name='employee_seance_delete'),

    # CRUD pour les salles
    path('intranet/salles/', views_employee.employee_salle_list, name='employee_salle_list'),
    path('intranet/salles/ajouter/', views_employee.employee_salle_create, name='employee_salle_create'),
    path('intranet/salles/<int:salle_id>/modifier/', views_employee.employee_salle_update, name='employee_salle_update'),
    path('intranet/salles/<int:salle_id>/supprimer/', views_employee.employee_salle_delete, name='employee_salle_delete'),

    # Modération des avis
    path('intranet/avis/', views_employee.employee_review_list, name='employee_review_list'),
    path('intranet/avis/<int:avis_id>/valider/', views_employee.employee_review_validate, name='employee_review_validate'),
    path('intranet/avis/<int:avis_id>/supprimer/', views_employee.employee_review_delete, name='employee_review_delete'),


    # API pour les incidents
    path('api/incidents/', views_api.api_incident_list_create, name='api_incident_list_create'),
    path('api/incidents/<int:pk>/', views_api.api_incident_resolve, name='api_incident_resolve'),
    path('api/salles/', views_api.api_salles_list),

    # Url pour token d'authentification
    path('api/token-auth/', views_api.token_auth_view, name='api_token_auth'),

    # Espace utilisateur
    path("mon-espace/", views.mon_espace, name="mon_espace"),
    path("noter/<int:film_id>/", views.noter_film, name="noter_film"),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)