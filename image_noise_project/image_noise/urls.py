from django.urls import path
from . import views
from .views import image_noise_view


urlpatterns = [
    path('', views.image_noise_view, name='image_noise_view'),
    path('save_drawing/', views.save_drawing_view, name='save_drawing_view'),  # Nouvelle URL
]
