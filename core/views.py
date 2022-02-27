from itertools import count
from django.shortcuts import get_object_or_404, redirect, render,reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Items,OrderItems,Order,BillingAddress
from django.utils import timezone
from django.views.generic import ListView, DetailView,View
from django.contrib import messages
from .forms import CheckoutForm
from django.conf import settings


def item_list(request):
    context={
        "items":Items.objects.all()
    }
    return render(request,"home.html",context)

class CheckoutView(View):
    def get(self,*args,**kwargs):
        #form
        form=CheckoutForm()
        order=Order.objects.get(user=self.request.user , ordered=False)
        context={
            'form':form,
            'object':order
        }
        return render(self.request,"checkout.html",context)
    
    def post(self,*args,**kwargs):
        form=CheckoutForm(self.request.POST or None)
        try:
            order=Order.objects.get(user=self.request.user , ordered=False)
            if form.is_valid():
                street_address=form.cleaned_data.get('street_address')
                appartment_address=form.cleaned_data.get('appartment_address')
                country=form.cleaned_data('country')
                zip=form.cleaned_data.get('zip')
                # same_shipping_address=form.cleaned_data.get('same_shipping_address')
                # save_info=form.cleaned_data.get('save_info')
                # payment_option=form.cleaned_data.get('payment_option')
                billing_address=BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    appartment_address=appartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address=billing_address
                order.save()
                return redirect('core:checkout')
            messages.warning(self.request, "Failed Checkout")     
            return redirect('core:checkout')
        except ObjectDoesNotExist :
            messages.error(self.request,"You do not have an active order")
            return redirect("core:order-summary")
        
        


class PaymentView(View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user , ordered=False)
            context={
                'object':order
            }
            return render(self.request,"payment.html",context)
        except ObjectDoesNotExist :
            messages.error(self.request,"You do not have an active order")

            return redirect("/")
        

    def post(self,*args,**kwargs):
        order=Order.objects.get(user=self.request.user,ordered=False)
        amount=order.get_total()*100,

        

def product(request):
    return render(request,"product.html")


class HomeView(ListView):
    model=Items
    paginate_by=5
    template_name="home.html"


class OrderSummaryView(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user , ordered=False)
            context={
                'object':order
            }
            return render(self.request,'order_summary.html',context)
        except ObjectDoesNotExist :
            messages.error(self.request,"You do not have an active order")

            return redirect("/")


class ItemDetailView(DetailView):
    model=Items
    template_name="product.html"


@login_required
def add_to_cart(request,slug):
    item=get_object_or_404(Items,slug=slug)
    order_item , created = OrderItems.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,"Your item has been updated")
            return redirect("core:order-summary")
        else:
            messages.info(request,"Your item has been added to cart")
            order.items.add(order_item)    
            return redirect("core:order-summary")
    else:
        order_date=timezone.now()
        order=Order.objects.create(user=request.user,order_date=order_date)
        order.items.add(order_item)
        messages.info(request,"Your item has been added to cart")
        return redirect("core:order-summary") 

@login_required
def remove_from_cart(request,slug):
    item=get_object_or_404(Items,slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItems.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request,"Your item has been removed from your cart")
            return redirect("core:order-summary")
        else:
            messages.info(request,"Your item was not present in your cart")
            return redirect("core:product",slug=slug)

    else:
        messages.info(request,"Your item has no active order")
        return redirect("core:product",slug=slug) 


@login_required
def remove_single_item_from_cart(request,slug):
    item=get_object_or_404(Items,slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItems.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request,"Item quantity was updated")
            return redirect("core:order-summary")
        else:
            messages.info(request,"Your item was not present in your cart")
            return redirect("core:product",slug=slug)

    else:
        messages.info(request,"Your item has no active order")
        return redirect("core:product",slug=slug)        