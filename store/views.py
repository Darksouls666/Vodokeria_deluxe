from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import SesionForm, CustomUserCreationForm
import json
import datetime
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

from . models import ShippingAddress, Order, OrderItem, Product, Customer

from .utils import cookieCart, cartData, guestOrder

# Create your views here.


def store(request):

    data = cartData(request)

    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, "store/store.html", context)

def cart(request):

    data = cartData(request)  
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']              

    context = {"items": items, "order": order, 'cartItems': cartItems}
    return render(request, "store/cart.html", context)


def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']       

    context = {"items": items, "order": order, 'cartItems': cartItems}
    return render(request, "store/checkout.html", context)


def main(request):
    context = {}
    return render(request, "store/main.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,
                                                 complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order,
                                                         product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)

    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item añadido", safe=False)

@csrf_protect
def processOrder(request):
    if request.method == 'POST':
        transaction_id = datetime.datetime.now().timestamp()
        data = json.loads(request.body)

        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                telephone=data['shipping']['telephone'],
            )

        return JsonResponse("Pago completado", safe=False)



# PRUEBA INICIO DE SESION
@csrf_protect
def customerCreated(request):

    data = {
    'form': SesionForm()
    }
    return render(request, 'registration/login.html', data)

@csrf_protect
def registro(request):
    data = {
        'form': CustomUserCreationForm()
    }

    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            user = formulario.save()

            # Autenticar al usuario recién registrado
            user = authenticate(username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            login(request, user)

            # Crear un nuevo objeto Customer relacionado con el usuario
            customer = Customer.objects.create(
                user=user,
                name=user.username,
                email=user.username + "@gmail.com"
            )

            messages.success(request, "Te has registrado correctamente")
            return redirect('store')  # Redireccionar a la vista adecuada

        data['form'] = formulario

    return render(request, 'registration/registro.html', data)