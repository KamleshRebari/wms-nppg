from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('add-worker/', views.add_worker, name='add_worker'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('register/', views.register_view, name='register'),

    path('user/', views.user_dashboard, name='user_dashboard'),

    

    path('slots/', views.manage_slots, name='manage_slots'),

    # ONLY include routes that ACTUALLY EXIST in views.py

]
