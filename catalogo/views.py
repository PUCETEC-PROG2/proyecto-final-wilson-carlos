from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Productos, CatalogoGadgets, CatalogoSmartphones, Clientes, Ventas, Transacciones, Salidas, MovimientosInventario
from django.utils import timezone
from .forms import ClienteForm
from django.contrib import messages
from django.db import IntegrityError

# Create your views here.

# Vista para mostrar el home
def home(request):
    productos = Productos.objects.all()[:4]  # Solo los 4 primeros productos
    return render(request, 'home.html', {'productos': productos})

# Vista para mostrar la categoria de gadgets
def categoria_gadgets(request):
    gadgets = CatalogoGadgets.objects.all()  # Recupera todos los productos de la categoría Gadgets
    return render(request, 'gadgets.html', {'productos': gadgets})

# Vista para mostrar la categoria de celulares
def categoria_celulares(request):
    celulares = CatalogoSmartphones.objects.all()  # Recupera todos los productos de la categoría Celulares
    return render(request, 'celulares.html', {'productos': celulares})

# Vista para mostrar clientes
def lista_clientes(request):
    clientes = Clientes.objects.all()
    form = ClienteForm()
    return render(request, 'clientes.html', {'clientes': clientes, 'form': form})

# Vista para agregar cliente
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'mensaje': 'Cliente agregado correctamente'}, status=200)
    return JsonResponse({'error': 'Formulario no válido'}, status=400)

# Vista para editar cliente
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
def eliminar_cliente(request, id_cliente):
    cliente = get_object_or_404(Clientes, id_cliente=id_cliente)
    cliente.delete()
    return JsonResponse({'mensaje': 'Cliente eliminado correctamente'}, status=200)

# Vista para listar las compras
def lista_compras(request):
    compras = Ventas.objects.all().order_by('-fecha')  # Ordenar por fecha descendente
    print(compras)  # Agregar esta línea para verificar que se están obteniendo las compras
    return render(request, 'compras/lista_compras.html', {'compras': compras})

# Vista para agregar las compras
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
def detalle_compra(request, id_venta):
    compra = get_object_or_404(Ventas, id_venta=id_venta)
    
    # Obtener todos los productos relacionados con esta compra
    productos_comprados = Ventas.objects.filter(id_venta=id_venta)
    
    # Calcular el total de la compra sumando los totales de cada producto
    total_compra = sum([venta.id_producto.precio * venta.cantidad for venta in productos_comprados])
    
    # Calcular los totales por producto para pasarlos al template
    productos_totales = [
        {
            'nombre': venta.id_producto.nombre,
            'precio': venta.id_producto.precio,
            'cantidad': venta.cantidad,
            'total_producto': venta.id_producto.precio * venta.cantidad
        }
        for venta in productos_comprados
    ]
    
    return render(request, 'compras/detalle_compra.html', {
        'compra': compra,
        'productos_totales': productos_totales,
        'total_compra': total_compra
    })

