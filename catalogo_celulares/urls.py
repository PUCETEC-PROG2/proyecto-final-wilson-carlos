"""
URL configuration for catalogo_celulares project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from catalogo import views  # Importa las vistas desde el archivo views.py

urlpatterns = [
    path('', views.home, name='home'),
    path('categoria/gadgets/', views.categoria_gadgets, name='categoria_gadgets'),
    path('categoria/celulares/', views.categoria_celulares, name='categoria_celulares'),
    path('clientes/', views.lista_clientes, name='clientes'),
    path('clientes/agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('clientes/editar/<int:id_cliente>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:id_cliente>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('compras/', views.lista_compras, name='compras'),
    path('compras/agregar/', views.agregar_compra, name='agregar_compra'),
    path('compras/detalle/<int:id_venta>/', views.detalle_compra, name='detalle_compra'),
    path('admin/', admin.site.urls),
]
