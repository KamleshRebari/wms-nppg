from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('add/', views.add_worker, name='add_worker'),

    path('display/', views.display, name='display'),

    path('edit/<int:worker_id>/', views.edit_worker, name='edit_worker'),

    path('manage-slots/', views.manage_slots, name='manage_slots'),

    path('user/', views.user_dashboard, name='user_dashboard'),

    path('profile/', views.profile_view, name='profile'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('register/', views.register_view, name='register'),
]
