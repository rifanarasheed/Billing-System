from django.urls import path
from bill.views import OrderCreateView,OrderLineView,OrderDelete,OrderUpdate,BillGenerate,OrderBillnoSearch,OrderNameSearch,OrderDateSearch

urlpatterns = [
    path("createorder",OrderCreateView.as_view(),name="createorder"),
    path("orderline/<str:bill_num>",OrderLineView.as_view(),name="orderline"),
    path("orderupdate/<int:pk><str:bill_num>",OrderUpdate.as_view(),name="orderupdate"),
    path("classdelete/<int:pk><str:bill_num>",OrderDelete.as_view(),name="orderdelete"),
    path("billgenerate/<str:bill_num>",BillGenerate.as_view(),name="completeorder"),
    path("billnumbersearch",OrderBillnoSearch.as_view(),name="OrderBillnoSearch"),
    path("billnamesearch",OrderNameSearch.as_view(),name="ordernameSearch"),
    path("billdatesearch",OrderDateSearch.as_view(),name="orderdateSearch")

]
