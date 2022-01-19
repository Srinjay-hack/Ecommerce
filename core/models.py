from django.db import models
from django.conf import settings
from django.shortcuts import reverse
# Create your models here.


CATEGRIES_CHOICES=[
    ('S','Shirt'),
    ('SW','Sports Wear'),
    ('OW','Outwear')
]

LABEL_CHOICES=[
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
]

class Items(models.Model):
    title=models.CharField(max_length=100);
    price=models.FloatField();
    discount_price=models.FloatField(blank=True,null=True);
    category=models.CharField(choices=CATEGRIES_CHOICES,max_length=2);
    label=models.CharField(choices=LABEL_CHOICES,max_length=1);
    slug=models.SlugField();
    description=models.TextField(default="Latest new tecnology");
    

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("core:product",kwargs={
            'slug':self.slug
        })
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart",kwargs={
            'slug':self.slug
        })  

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart",kwargs={
            'slug':self.slug
        })         

class OrderItems(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    item=models.ForeignKey(Items,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    ordered=models.BooleanField(default=False)
    
    def __str__(self):
        return  f"{self.quantity} of {self.item.title}"
    
    def get_total_amount_price(self):
        return self.quantity * self.item.price
    
    def get_total_discounted_price(self):
        return self.quantity * self.item.discount_price

    def saved_price(self):
        return self.get_total_amount_price() - self.get_total_discounted_price()

    def get_final_price(self):
        if(self.item.discount_price):
            return self.get_total_discounted_price()
        else: 
          return self.get_total_amount_price()



class Order(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    items=models.ManyToManyField(OrderItems)
    start_date=models.DateTimeField(auto_now_add=True)
    order_date=models.DateTimeField()
    ordered=models.BooleanField(default=False)
    def __str__(self):
        return self.user.username

    def get_total(self):
        total=0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total



