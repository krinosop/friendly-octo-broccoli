from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .admin import admin_site

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='theater/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('directors/', views.director_list, name='director_list'),
    path('directors/create/', views.director_create, name='director_create'),
    path('directors/<int:pk>/', views.director_detail, name='director_detail'),
    path('directors/<int:pk>/update/', views.director_update, name='director_update'),
    path('directors/<int:pk>/delete/', views.director_delete, name='director_delete'),
    
    path('plays/', views.play_list, name='play_list'),
    path('plays/create/', views.play_create, name='play_create'),
    path('plays/<int:pk>/', views.play_detail, name='play_detail'),
    path('plays/<int:pk>/update/', views.play_update, name='play_update'),
    path('plays/<int:pk>/delete/', views.play_delete, name='play_delete'),
    
    path('actors/', views.actor_list, name='actor_list'),
    path('actors/create/', views.actor_create, name='actor_create'),
    path('actors/<int:pk>/', views.actor_detail, name='actor_detail'),
    path('actors/<int:pk>/update/', views.actor_update, name='actor_update'),
    path('actors/<int:pk>/delete/', views.actor_delete, name='actor_delete'),
    
    path('castings/', views.casting_list, name='casting_list'),
    path('castings/<int:pk>/', views.casting_detail, name='casting_detail'),
    path('castings/create/', views.casting_create, name='casting_create'),
    path('castings/<int:pk>/update/', views.casting_update, name='casting_update'),
    path('castings/<int:pk>/delete/', views.casting_delete, name='casting_delete'),
    path('castings/<int:pk>/delete/confirm/', views.casting_confirm_delete, name='casting_confirm_delete'),
    
    path('performances/', views.performance_list, name='performance_list'),
    path('performances/create/', views.performance_create, name='performance_create'),
    path('performances/<int:pk>/', views.performance_detail, name='performance_detail'),
    path('performances/<int:pk>/update/', views.performance_update, name='performance_update'),
    path('performances/<int:pk>/delete/', views.performance_delete, name='performance_delete'),
    path('performances/export/', views.export_performances_excel, name='export_performances_excel'),
    path('statistics/', views.statistics_view, name='statistics'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 