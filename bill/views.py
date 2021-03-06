from django.shortcuts import render,redirect
from bill.forms import OrderCreateForm,OrderLineForm,BillNumberSearchForm,BillNameSearchForm,BillDateSearchForm,SearchbillForm

from bill.forms import UserRegister,UserLogin
from django.contrib.auth.models import User
from bill.authentication import EmailAuthBackend
from django.contrib.auth import login

from django.views.generic import TemplateView
from bill.models import Order,OrderLines,Purchase,Product
from django.db.models import Sum

from bill.filters import OrderFilter

from bill.decorators import admin_only
from django.utils.decorators import method_decorator



class UserRegisterView(TemplateView):
    model = User
    form_class = UserRegister
    template_name = "bill/userregistration.html"
    context = {}
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context["form"] = form
        return render(request,self.template_name,self.context)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

class UserLoginView(TemplateView):
    template_name = "bill/userlogin.html"
    form_class = UserLogin
    context = {}
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context["form"] = form
        return render(request,self.template_name,self.context)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            # creating an object of class EmailAuthBackend to access its method
            obj = EmailAuthBackend()
            user = obj.authenticate(request,username=email,password=password)
            if user:
                login(request,user)
                return redirect("createorder")
            else:
                return redirect("login")
        return render(request,"bill/userlogin.html")

@method_decorator(admin_only,name='dispatch')
class OrderCreateView(TemplateView):
    model = Order
    form_class = OrderCreateForm
    template_name = "bill/ordercreate.html"
    context = {}
    def get(self, request, *args, **kwargs):
        print(request.user)
        form = self.form_class()
        self.context["form"] = form
        # bill number should be autogenerated ,
        # so, if first insertion , billnumber="lulu-1000', then next bill should be increment of 1000
        # orm query to get last bill number
        order = self.model.objects.last()
        if order:
            last_billnum = order.bill_number              # "lulu-1000"
            last = int(last_billnum.split("-")[1]) + 1   # [lulu,1000]
            bill_number = "bill-" + str(last)
        else:
            bill_number = "bill-1000"
        form = self.form_class(initial={"bill_number":bill_number})
        self.context["form"] = form
        return render(request,self.template_name,self.context)
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # we need to bring bill number to next page, where button for selectitem and all
            bill_number = form.cleaned_data.get("bill_number")   # bill_number from forms.py
            form.save()
            # once customer details are entered, after clicking submit, we need to go to orderline page
            # we need bill_number to pass to orderline page in its gets part,
            return redirect("orderline",bill_num = bill_number)    # calling through url

@method_decorator(admin_only,name='dispatch')
class OrderLineView(TemplateView):
    model = OrderLines
    form_class = OrderLineForm
    template_name ="bill/orderline.html"
    context = {}
    def get(self, request, *args, **kwargs):
        # to get bill number and pass it in the form, we add initial
        bill_number = kwargs.get("bill_num")
        form = self.form_class(initial={"bill_number" : bill_number})   # forms.py bill_number of orderlineform, because in that field we need bill_number to display
        self.context["form"] = form
        # we need list all the added product of that particular bill
        queryset  = self.model.objects.filter(bill_number__bill_number = bill_number)
        # adding queryset into context
        self.context["items"] = queryset
        # to get total of the amount
        # first from django.db.models import Sum,then based on groupby the bill number's object and get the sum of the field we want total
        total = OrderLines.objects.filter(bill_number__bill_number = bill_number).aggregate(Sum("amount"))
        # we get the answer in dictionary format, so to get the value only of amount__sum ({'amount__sum':230.0})
        ctotal = total["amount__sum"]
        # add to context
        self.context["total"] = ctotal
        self.context["bill_number"] = bill_number
        return render(request,self.template_name,self.context)
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # cant save form directly beacuse this is not modelform
            # even we cant use model class also, we need to calculate amount on the basis of quanity taken of particular product
            # now we need save these into Orderlines model, but we cant save them direclty
            # coz in Orderline model, as bill_number and product is foreign key(Order table and Product table) which accept only object instance
            # and we are trying to pass product_name to product field and bill number to bill_number
            # so we need to set object of product_name
            # actually we should have given product as a foreign key to Purchase table not product table because we need only purchased product ,as we cant change now
            bill_number = form.cleaned_data.get("bill_number")  # forms.py fields
            bill = Order.objects.get(bill_number=bill_number)
            # to get products purchased by seller
            product_name = form.cleaned_data.get("product_name")
            prdt = Product.objects.get(product_name=product_name)
            # quantity
            quantity = form.cleaned_data.get("product_quantity")  # this can be accessed direclty from form
            # to get product selling price from purchase model
            product = Purchase.objects.get(product__product_name = product_name)   # to get product name, so we can get selling price
            amount = product.selling_price*quantity
            # storing the data into model
            orderline = self.model(bill_number = bill, product = prdt, product_quantity = quantity, amount = amount)
            orderline.save()
            print("saved")
            return redirect("orderline", bill_num=bill_number)

@method_decorator(admin_only,name='dispatch')
class OrderUpdate(TemplateView):
    model = OrderLines
    form_class = OrderLineForm
    template_name = "bill/orderedit.html"
    context = {}
    def get(self, request, *args, **kwargs):
        bill_number = kwargs.get("bill_num")
        order = self.model.objects.get(id=kwargs["pk"])
        form = self.form_class(initial={"bill_number": bill_number})  # forms.py bill_number of orderlineform, because in that field we need bill_number to display
        self.context["form"] = form
        self.context["order"] = order
        return render(request, self.template_name, self.context)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            bill_number = form.cleaned_data.get("bill_number")
            bill = Order.objects.get(bill_number=bill_number)
            product_name = form.cleaned_data.get("product_name")
            prdt = Product.objects.get(product_name=product_name)
            quantity = form.cleaned_data.get("product_quantity")
            # to get product name, so we can get selling price
            product = Purchase.objects.get(product__product_name=product_name)
            amount = product.selling_price * quantity
            # storing the data into model
            orderline = self.model(bill_number=bill, product=prdt, product_quantity=quantity, amount=amount)
            orderline.save()
            print("saved")
            return redirect("orderline", bill_num=bill_number)

@method_decorator(admin_only,name='dispatch')
class OrderDelete(TemplateView):
    # just get the book id of book that need to be deleted and delete it
    model = OrderLines
    def get(self, request, *args, **kwargs):
        bill_number = kwargs.get("bill_num")
        order = self.model.objects.get(id=kwargs["pk"])
        order.delete()
        return redirect("orderline", bill_num=bill_number)

@method_decorator(admin_only,name='dispatch')
class BillGenerate(TemplateView):
    def get(self, request, *args, **kwargs):
        bill_number = kwargs.get("bill_num")
        total = OrderLines.objects.filter(bill_number__bill_number = bill_number).aggregate(Sum("amount"))
        grandtotal = total["amount__sum"]
        order = Order.objects.get(bill_number=bill_number)   # to get details regarding bill number from order model
        order.bill_total = grandtotal  # model field -> bill_total
        cust_name = order.customer_name
        phone_number = order.phone_number
        date = order.bill_date
        order.save()
        queryset = OrderLines.objects.filter(bill_number__bill_number = bill_number)
        context = {}
        context["items"] = queryset
        context["Grand_Total"] = grandtotal
        context["customer_name"] = cust_name
        context["phone"] = phone_number
        context["date"] = date
        return render(request,"bill/customerbill.html",context)

class OrderBillnoSearch(TemplateView):
    template_name = "bill/searchbillnumber.html"
    form_class = BillNumberSearchForm
    context = {}
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context["form"] = form
        return render(request,self.template_name,self.context)
    def post(self,request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            bill_number = form.cleaned_data.get("bill_number")
            total = OrderLines.objects.filter(bill_number__bill_number=bill_number).aggregate(Sum("amount"))
            grandtotal = total["amount__sum"]
            order = Order.objects.get(bill_number=bill_number)  # to get details regarding bill number from order model
            order.bill_total = grandtotal  # model field -> bill_total
            cust_name = order.customer_name
            phone_number = order.phone_number
            date = order.bill_date
            order.save()
            queryset = OrderLines.objects.filter(bill_number__bill_number=bill_number)
            context = {}
            context["items"] = queryset
            context["Grand_Total"] = grandtotal
            context["bill_number"] = bill_number
            context["customer_name"] = cust_name
            context["phone"] = phone_number
            context["date"] = date
            return render(request, "bill/searchbillnumber.html", context)

class OrderNameSearch(TemplateView):
    template_name = "bill/searchbillname.html"
    form_class = BillNameSearchForm
    context = {}
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context["form"] = form
        return render(request,self.template_name,self.context)
    def post(self,request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            customer_name = form.cleaned_data.get("customer_name")
            total = OrderLines.objects.filter(bill_number__customer_name=customer_name).aggregate(Sum("amount"))
            grandtotal = total["amount__sum"]
            order = Order.objects.get(customer_name=customer_name)  # to get details regarding bill name from order model
            order.bill_total = grandtotal  # model field -> bill_total
            bill_num = order.bill_number
            phone_number = order.phone_number
            date = order.bill_date
            order.save()
            queryset = OrderLines.objects.filter(bill_number__customer_name=customer_name)
            context = {}
            context["items"] = queryset
            context["Grand_Total"] = grandtotal
            context["billnumber"] = bill_num
            context["customer_name"] = customer_name
            context["phone"] = phone_number
            context["date"] = date
            return render(request, "bill/searchbillname.html", context)

class OrderDateSearch(TemplateView):
    # month/day/year
    template_name = "bill/searchbilldate.html"
    form_class = BillDateSearchForm
    context = {}
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context["form"] = form
        return render(request,self.template_name,self.context)
    def post(self,request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            bill_date = form.cleaned_data.get("bill_date")
            order = Order.objects.get(bill_date=bill_date)
            bill_num = order.bill_number
            cust_name = order.customer_name
            phone_number = order.phone_number
            date = order.bill_date
            total = OrderLines.objects.filter(bill_number__bill_date=bill_date).aggregate(Sum("amount"))
            grandtotal = total["amount__sum"]
            order.bill_total = grandtotal  # model field -> bill_total
            order.save()
            queryset = OrderLines.objects.filter(bill_number__bill_date=bill_date)
            context = {}
            context["items"] = queryset
            context["Grand_Total"] = grandtotal
            context["billnumber"] = bill_num
            context["customer_name"] = cust_name
            context["phone"] = phone_number
            context["date"] = date
            return render(request, "bill/searchbilldate.html", context)

class Searchbill(TemplateView):
    template_name = "bill/searching.html"
    form_class = SearchbillForm
    context = {}
    def get(self, request, *args, **kwargs):
        orders = Order.objects.all()
        orderfilter = OrderFilter(request.GET,queryset=orders)
        self.context["filter"] = orderfilter
        return render(request,self.template_name,self.context)




















