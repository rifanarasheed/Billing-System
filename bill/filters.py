# import model that need to import for filtering

from bill.models import Order
import django_filters

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = ['bill_number','bill_date','customer_name']   # fields that we need to filter,same field name as given in order model
