from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_page, name='chatbot'),
    path('get/', views.get_chat_response, name='get_chat_response'),
]