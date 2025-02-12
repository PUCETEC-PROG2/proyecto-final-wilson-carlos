from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Productos, CatalogoGadgets, CatalogoSmartphones, Clientes, Ventas
from django.utils import timezone
from .forms import ClienteForm

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
    return render(request, 'compras/lista_compras.html', {'compras': compras})

# Vista para agregar las compras
def agregar_compra(request):
    if request.method == 'POST':
        id_cliente = request.POST.get('id_cliente')
        fecha = request.POST.get('fecha')
        productos = request.POST.getlist('productos')  # Lista de productos seleccionados
        cantidades = request.POST.getlist('cantidades')  # Lista de cantidades por producto

        # Obtener el cliente correspondiente
        cliente = Clientes.objects.get(id_cliente=id_cliente)

        # Calcular el total de la compra
        total = 0
        for i, id_producto in enumerate(productos):
            producto = Productos.objects.get(id_producto=id_producto)
            cantidad = int(cantidades[i])
            total += producto.precio * cantidad

        # Crear la venta
        venta = Ventas(id_cliente=cliente, fecha=fecha, total=total)
        venta.save()

        # Crear las transacciones y actualizar el inventario
        for i, id_producto in enumerate(productos):
            producto = Productos.objects.get(id_producto=id_producto)
            cantidad = int(cantidades[i])
            producto.stock -= cantidad
            producto.save()

            # Guardar transacción
            transaccion = Transacciones(id_producto=producto, tipo='venta', cantidad=cantidad, fecha=timezone.now())
            transaccion.save()

        return redirect('compras')  # Redirigir a la lista de compras después de guardar

    else:
        clientes = Clientes.objects.all()
        productos = Productos.objects.all()
        return render(request, 'compras/agregar_compra.html', {'clientes': clientes, 'productos': productos})
    
# Vista para detalles de las compras
def detalle_compra(request, id_venta):
    compra = get_object_or_404(Ventas, id_venta=id_venta)
    return render(request, 'compras/detalle_compra.html', {'compra': compra})


