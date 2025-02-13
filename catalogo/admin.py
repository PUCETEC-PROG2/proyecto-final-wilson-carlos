from django.contrib import admin
from .models import Productos, CatalogoGadgets, CatalogoSmartphones, CatalogoGeneral, Clientes, Ventas

# Register your models here.

admin.site.register(Productos)
admin.site.register(CatalogoGadgets)
admin.site.register(CatalogoSmartphones)
admin.site.register(CatalogoGeneral)
admin.site.register(Clientes)
admin.site.register(Ventas)