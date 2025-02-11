from django.shortcuts import render
from .models import Productos, CatalogoGadgets, CatalogoSmartphones

# Create your views here.

def home(request):
    productos = Productos.objects.all()[:3]  # Solo los 3 primeros productos
    return render(request, 'home.html', {'productos': productos})

def categoria_gadgets(request):
    gadgets = CatalogoGadgets.objects.all()  # Recupera todos los productos de la categoría Gadgets
    return render(request, 'gadgets.html', {'productos': gadgets})

def categoria_celulares(request):
    celulares = CatalogoSmartphones.objects.all()  # Recupera todos los productos de la categoría Celulares
    return render(request, 'celulares.html', {'productos': celulares})

