from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Productos, CatalogoGadgets, CatalogoSmartphones, Clientes, Ventas, Transacciones, Salidas, MovimientosInventario
from .forms import ClienteForm
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

# Create your views here.

# Vista para mostrar el home
def home(request):
    gadgets = CatalogoGadgets.objects.all()[:3]  # Los 3 primeros productos de gadgets
    celulares = CatalogoSmartphones.objects.all()[:3]  # Los 3 primeros productos de celulares
    return render(request, 'home.html', {'gadgets': gadgets, 'celulares': celulares})

# Vista para mostrar la categoria de gadgets
def categoria_gadgets(request):
    gadgets = CatalogoGadgets.objects.all()  # Recupera todos los productos de la categoría Gadgets
    return render(request, 'gadgets.html', {'productos': gadgets})

# Vista para mostrar la categoria de celulares
def categoria_celulares(request):
    celulares = CatalogoSmartphones.objects.all()  # Recupera todos los productos de la categoría Celulares
    return render(request, 'celulares.html', {'productos': celulares})

# Vista para mostrar clientes
@login_required
def lista_clientes(request):
    clientes = Clientes.objects.all()
    form = ClienteForm()
    return render(request, 'clientes.html', {'clientes': clientes, 'form': form})

# Vista para agregar cliente
@login_required
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'mensaje': 'Cliente agregado correctamente'}, status=200)
    return JsonResponse({'error': 'Formulario no válido'}, status=400)

# Vista para editar cliente
@login_required
def editar_cliente(request, id_cliente):
    cliente = get_object_or_404(Clientes, id_cliente=id_cliente)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({'mensaje': 'Cliente actualizado correctamente'}, status=200)
        else:
            return JsonResponse({'error': 'Formulario no válido'}, status=400)
    
    # Si la solicitud es GET, devolver los datos del cliente en formato JSON
    if request.method == 'GET':
        return JsonResponse({
            'id_cliente': cliente.id_cliente,
            'nombre': cliente.nombre,
            'apellido': cliente.apellido,
            'correo_electronico': cliente.correo_electronico,
            'telefono': cliente.telefono
        })

# Vista para eliminar cliente
@login_required
def eliminar_cliente(request, id_cliente):
    cliente = get_object_or_404(Clientes, id_cliente=id_cliente)
    cliente.delete()
    return JsonResponse({'mensaje': 'Cliente eliminado correctamente'}, status=200)

# Vista para listar las compras
@login_required
def lista_compras(request):
    compras = Ventas.objects.all().order_by('-fecha')  # Ordenar por fecha descendente
    print(compras)  # Agregar esta línea para verificar que se están obteniendo las compras
    return render(request, 'compras/lista_compras.html', {'compras': compras})

# Vista para agregar las compras
@login_required
def agregar_compra(request):
    if request.method == "POST":
        try:
            cliente_id = request.POST.get("id_cliente")
            fecha = request.POST.get("fecha")
            productos_seleccionados = request.POST.getlist("productos[]")
            cantidades = request.POST.getlist("cantidades[]")

            # Validaciones básicas
            if not cliente_id:
                raise ValueError("Debe seleccionar un cliente.")
            if not fecha:
                raise ValueError("Debe seleccionar una fecha.")
            if not productos_seleccionados:
                raise ValueError("Debe seleccionar al menos un producto.")

            cliente = Clientes.objects.get(id_cliente=cliente_id)

            for i, producto_id in enumerate(productos_seleccionados):
                try:
                    cantidad = int(cantidades[i].strip()) if i < len(cantidades) and cantidades[i].strip() else 1
                except ValueError:
                    cantidad = 1  # Si el usuario ingresó un valor no numérico

                producto = Productos.objects.get(id_producto=producto_id)

                # Registrar la venta en la tabla Ventas
                venta = Ventas.objects.create(
                    id_cliente=cliente,
                    id_producto=producto,
                    cantidad=cantidad,
                    fecha=fecha,
                    total=producto.precio * cantidad
                )

                # Registrar la salida en la tabla Salidas
                Salidas.objects.create(
                    id_producto=producto,
                    cantidad=cantidad,
                    fecha=fecha,
                    comentario=f"Venta registrada (ID Venta: {venta.id_venta})"
                )

                # Registrar el movimiento en la tabla MovimientosInventario
                MovimientosInventario.objects.create(
                    producto=producto,
                    fecha=fecha,
                    cantidad=-cantidad,  # Se resta del inventario
                    tipo_movimiento="Salida",
                    comentario=f"Venta registrada (ID Venta: {venta.id_venta})"
                )

                # Registrar la transacción en la tabla Transacciones
                Transacciones.objects.create(
                    id_producto=producto,
                    tipo="Venta",
                    cantidad=cantidad,
                    fecha=fecha,
                    comentario=f"Venta realizada para el cliente {cliente.id_cliente}"
                )

            messages.success(request, "Compra registrada exitosamente y el inventario actualizado.")
            return redirect("compras")  

        except Clientes.DoesNotExist:
            messages.error(request, "El cliente seleccionado no existe.")
        except Productos.DoesNotExist:
            messages.error(request, "Uno o más productos seleccionados no existen.")
        except ValueError as e:
            messages.error(request, str(e))
        except IntegrityError:
            messages.error(request, "Error en la base de datos.")

    # Obtener datos para el formulario
    clientes = Clientes.objects.all()
    productos = Productos.objects.all()
    return render(request, "compras/agregar_compra.html", {"clientes": clientes, "productos": productos})
    
# Vista para detalles de las compras
@login_required
def detalle_compra(request, id_venta):
    # Obtener la venta específica
    compra = get_object_or_404(Ventas, id_venta=id_venta)
    
    # Obtener el producto relacionado con esta compra
    producto_comprado = compra.id_producto
    
    # Calcular el total de la compra
    total_compra = producto_comprado.precio * compra.cantidad
    
    # Crear el diccionario con los detalles del producto
    producto_detalle = {
        'id_producto': producto_comprado.id_producto,
        'nombre': producto_comprado.nombre,
        'marca': producto_comprado.marca,
        'modelo': producto_comprado.modelo,
        'precio': producto_comprado.precio,
        'cantidad': compra.cantidad,
        'total_producto': total_compra
    }
    
    return render(request, 'compras/detalle_compra.html', {
        'compra': compra,
        'producto_detalle': producto_detalle,
        'total_compra': total_compra
    })
