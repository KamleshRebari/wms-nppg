from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('add/', views.add_worker, name='add_worker'),

    path('edit/<int:worker_id>/', views.edit_worker, name='edit_worker'),

    path('display/', views.display, name='display'),

    path('manage-slots/', views.manage_slots, name='manage_slots'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    path('user/', views.user_dashboard, name='user_dashboard'),
path('make-admin/', views.create_admin, name='create_admin'),
path('edit/<int:id>/', views.edit_worker, name='edit_worker'),

    path('profile/', views.profile_view, name='profile'),
]
