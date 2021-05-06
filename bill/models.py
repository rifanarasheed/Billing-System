from django.db import models

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=120,unique=True)
    def __str__(self):
        return self.product_name

class Purchase(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)
    purchase_price = models.FloatField(null=False)
    selling_price = models.FloatField(null=False)
    purchase_date = models.DateField(auto_now=True)    # to get purchase date of product

class Order(models.Model):
    bill_number = models.CharField(max_length=60,unique=True)
    bill_date = models.DateField(auto_now=True)
    customer_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=120)
    bill_total = models.IntegerField(default=0,null=True)
    def __str__(self):
        return str(self.bill_number)

class OrderLines(models.Model):
    bill_number = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    product_quantity = models.FloatField()
    amount = models.FloatField()





