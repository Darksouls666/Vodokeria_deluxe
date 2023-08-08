import json
from . models import Product, Customer, Order, OrderItem

def cookieCart(request):
    try:
        cart_json = request.COOKIES['cart']
        cart = json.loads(cart_json)
    except KeyError:
        cart = {}

    print('Cart:', cart)
    items = []
    order = {"get_cart_total": 0, "get_cart_items": 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:

            if (cart[i]['quantity'] > 0):
                cartItems += cart[i]['quantity']

                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'product':{
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'imageURL': product.imageURL
                    },
                    'quantity': cart[i]['quantity'],
                    'get_total': total,
                }
                items.append(item)

                if product.digital is False:
                    order['shipping'] = True           
        except ImportError:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}

def cartData(request):
    """Obtener los datos del carrito para un usuario"""

    if request.user.is_authenticated:
        # Si el usuario está autenticado, obtenemos los datos del carrito desde la base de datos
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Si el usuario no está autenticado, obtenemos los datos del carrito desde las cookies
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}

def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    # Creamos un cliente (Customer) y una orden (Order) para el usuario invitado
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    items = data['items']

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )

    return customer, order
