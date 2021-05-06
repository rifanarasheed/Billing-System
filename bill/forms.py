from django.forms import ModelForm
from django import forms
from bill.models import Order,Purchase

class OrderCreateForm(ModelForm):
    class Meta:
        model = Order
        fields = ["bill_number","customer_name","phone_number"]

class OrderLineForm(forms.Form):
    bill_number = forms.CharField()
    # we need products in a drop down list, we that we can select our choice.
    # during ordering, we need to get only products from purchase model
    # we need to get product_name from purchase model - product ( we need only products which we have purchased only to order, not all the product list)
    # in purchase model, product is in the form of object but we need only name from that object  ,so orm query to get name only -->
    # productnames = Purchase.objects.all().values_list('product__product_name') -->
    # Purchase.objects.all() --> gives all fields of purchase model but we need only name of product, so, values_list('product__product_name') --> product__product_name shows that get product name(product model) from purchase parent model(product-> forign key)
    # __ indicates parent model refering
    # we put choices in the form tuple inside tuple format, so by value_list() --> we get product names in the form of list, so we need to convert it
    # ex: data = [("horlicks"),("boost"),("bournvita")]
    # we need to get in this format
    # (
    #   (horlicks,horlicks)
    #   (boost,boost)
    #   (bournvita,bournvita)
    # )
    #to get that,we can use list comprehension
    # result = [(item[0],item[0]) for item in data]
    # print(result)
    # so we get list of tuple
    products = Purchase.objects.all().values_list('product__product_name')  # purchase -> product and product ->product_name
    result = [(itemtuple[0],itemtuple[0]) for itemtuple in products]
    #choices = (
    #    ("horlicks","horlicks"),
    #    ("oreo","oreo")
    #)
    product_name = forms.ChoiceField(choices=result)
    product_quantity = forms.IntegerField()

class BillNumberSearchForm(forms.Form):
    bill_number = forms.CharField(max_length=30)

class BillNameSearchForm(forms.Form):
    customer_name = forms.CharField(max_length=40)

class BillDateSearchForm(forms.Form):
    bill_date = forms.DateField()