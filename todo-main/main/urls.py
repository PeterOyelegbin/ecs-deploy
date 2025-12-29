from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('create', views.addItem, name='create'),
    path('<int:pk>', views.detailItem, name='details'),
    path('edit/<int:pk>', views.updateItem, name='update'),
    path('delete/<int:pk>', views.deleteItem, name='delete'),
]