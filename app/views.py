from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, OrderItem, Order, Payment
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from accounts.models import CustomUser
from django.conf import settings
import stripe


class IndexView(ListView):
    model = Item
    template_name = 'app/index.html'

class testView(TemplateView):
    template_name='app/test.html'

class ItemDetailView(DetailView):
    model = Item
    template_name = 'app/product.html'


class ThanksView(LoginRequiredMixin, TemplateView):
    template_name = 'app/thanks.html'


class OrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            context = {
                'order': order
            }
            return render(request, 'app/order.html', context)
        except ObjectDoesNotExist:
            return render(request, 'app/order.html')

class ThanksOverView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app/order.html')


class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=request.user, ordered=False)
        user_data = CustomUser.objects.get(id=request.user.id)
        context = {
            'order': order,
            'user_data': user_data
        }
        return render(request, 'app/payment.html', context)

    def post(self, request, *args, **kwargs):
    
        order = Order.objects.get(user=request.user, ordered=False)
        
        amount = order.get_total()
        order_items = order.items.all()
        item_list = []
        for order_item in order_items:
            item_list.append(str(order_item.item) + ':' + str(order_item.quantity))
        description = ' '.join(item_list)

      

        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        
        order.save()
        return redirect('thanks')


@login_required
def addItem(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order = Order.objects.filter(user=request.user, ordered=False)

    if order.exists():
        order = order[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        order.items.add(order_item)

    return redirect('order')


@login_required
def removeItem(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order.exists():
        order = order[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            return redirect("order")

    return redirect("product", slug=slug)


@login_required
def removeSingleItem(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order.exists():
        order = order[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            return redirect("order")

    return redirect("product", slug=slug)