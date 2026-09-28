from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/chat/', views.chat_gateway, name='chat_gateway'),
]