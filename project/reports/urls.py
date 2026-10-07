from django.urls import path
from . import views

urlpatterns = [
    # Citizen Auth
    path('',           views.home_view,     name='home'),
    path('register/',  views.register_view, name='register'),
    path('login/',     views.login_view,    name='login'),
    path('logout/',    views.logout_view,   name='logout'),

    # Citizen Pages
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reports/new/',                         views.report_create_view,    name='report_create'),
    path('reports/submitted/<uuid:report_id>/',  views.report_submitted_view, name='report_submitted'),
    path('track/', views.track_view, name='track'),

    # Police Auth (login & logout only — NO register)
    path('police/login/',  views.police_login_view,  name='police_login'),
    path('police/logout/', views.police_logout_view, name='police_logout'),

    # Police registration (superuser only)
    path('police/register/', views.police_register_view, name='police_register'),

    # Police Portal
    path('police/dashboard/',        views.police_dashboard_view,     name='police_dashboard'),
    path('police/reports/',          views.police_report_list_view,   name='police_report_list'),
    path('police/reports/<int:pk>/', views.police_report_detail_view, name='police_report_detail'),
]
