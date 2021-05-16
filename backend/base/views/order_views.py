from django.shortcuts import render
from datetime import datetime

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from ..models import Product, Order, OrderItem, ShippingAddress
from ..serializers import OrderSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data

    orderItems = data['orderItems']

    if orderItems and len(orderItems)==0:
        return Response({'detail':'No order items'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        #Create order
        order = Order.objects.create(
            user=user,
            paymentMethod=data['paymentMethod'],
            taxPrice=data['taxPrice'],
            shippingPrice=data['shippingPrice'],
            totalPrice= data['totalPrice']
        )
        #Shipping address

        shipping = ShippingAddress.objects.create(
            order=order,
            address=data['shippingAddress']['address'],
            city = data['shippingAddress']['city'],
            postalCode = data['shippingAddress']['postalCode'],
            country = data['shippingAddress']['country'],
        )
        #Create order items
        for item in orderItems:
            product = Product.objects.get(_id=item['product'])
            order_item= OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                quantity=item['qty'],
                price=item['price'],
                image=product.image.url,

            )

        #Update stock

        product.countInStock -= int(order_item.quantity)
        product.save()

        serializer = OrderSerializer(order,many=False)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user
    try:
        order=Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            Response({'detail':'notauthorized to view this order'},status = status.http.status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail':'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request,pk):
    order = Order.objects.get(_id=pk)

    order.isPaid=True
    order.paidAt = datetime.now()

    order.save()

    return Response('Order was paid')
