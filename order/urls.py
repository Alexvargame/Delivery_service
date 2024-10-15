
from django.urls import path
from .views import *

urlpatterns = [
    path('',main_menu,name='main_url'),
    path('admin/',main_admin_menu,name='main_admin_url'),
    path('check/',OrderCheckOnWork.as_view(),name='update_orders_on_work_url'),
    path('orders/create/', OrderCreateView.as_view(),name='create_order_url'),
    path('orders/create/<str:delivery_point_name>/<str:delivery_point_city>/<str:delivery_point_street>/<str:delivery_point_building>/<str:delivery_point_office>/<str:cost>/', OrderCheckCreateView.as_view(),name='check_create_order_url'),
    path('orders/search/orders/', SearchOrderView.as_view(),name='search_order_url'),
    path('orders/search/deliveres/', SearchDeliveryView.as_view(),name='search_deliveres_url'),
    path('orders/<int:pk>/', OrderDetailView.as_view(),name='detail_order_url'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(),name='update_order_url'),
    path('delivers/<int:pk>/', DeliveryDetailView.as_view(),name='detail_delivery_url'),
    path('delivers/<int:pk>/update/', DeliveryUpdateView.as_view(),name='update_delivery_url'),
    path('orders/', OrderListView.as_view(),name='list_orders_url'),
    path('orders/clients/', ClientsListView.as_view(),name='list_clients_url'),
    path('orders/couriers/', CouriersListView.as_view(),name='list_couriers_url'),
    path('orders/offices/', OfficesListView.as_view(),name='list_offices_url'),
    path('orders/offices/create/', OfficeCreateView.as_view(),name='create_office_url'),
    path('orders/offices/<int:pk>/', OfficeDetailView.as_view(),name='detail_office_url'),
    path('orders/offices/search/',SearchOfficeView.as_view(),name='search_office_url'),
    path('orders/delivery_points/',DeliveryPointListView.as_view(),name='list_delivery_points_url'),
    path('orders/delivery_points/create/',DeliveryPointCreateView.as_view(),name='create_delivery_point_url'),
    path('orders/delivery_points/<int:pk>/',DeliveryPointDetailView.as_view(),name='detail_delivery_point_url'),
    path('orders/delivery_poinits/search/',SearchDeliveryPointView.as_view(),name='search_delivery_point_url'),
    path('orders/search/<str:group_name>/', UsersSearchView.as_view(),name='search_users_url'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(),name='delete_order_url'),
    path('orders/done/<str:number>/', OrderDoneView.as_view(),name='done_order_url'),
    path('orders/check_cost/', DeliveryCostChekcView.as_view(),name='check_cost_url'),
    path('orders/deliveres/',DeliveryListView.as_view(),name='list_deliveres_url'),
    path('orders/reports/offices/',ReportOfficeView.as_view(),name='report_offices_url'),
    path('orders/reports/delivery_points/',ReportDeliveryPointsView.as_view(),name='report_delivery_points_url'),
    path('orders/reports/deliveres/',ReportDeliverView.as_view(),name='report_deliveres_url'),
    path('orders/reports/all_orders/',ReportAllOrdersView.as_view(),name='report_all_orders_url'),
    path('orders/reports/orderers/',ReportOrderersView.as_view(),name='report_orderers_url')
]
