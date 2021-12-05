"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from backend.views.clientView import ClientListView, ClientView
from backend.views.routeView import RoutingView, RouteView
from backend.views.locationView import LocationView, LocationListView
from backend.views.driverView import DriverView, DriverListView
from backend.views.managerView import ManagerView, ManagerListView
from backend.views.bulkClientView import BulkClientView
from backend.views.bulkDriverView import BulkDriverView
from backend.views.routeListView import RouteListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/locations/', LocationListView.as_view()),
    path('api/locations/<int:pk>/', LocationView.as_view()),
    path('api/clients/', ClientListView.as_view()),
    path('api/clients/<int:pk>/', ClientView.as_view()),
    path('api/routes/', RoutingView.as_view()),
    path('api/routes/<int:pk>/', RouteView.as_view()),
    path('api/routeList/<int:pk>/', RouteListView.as_view()),
    path('api/drivers/', DriverListView.as_view()),
    path('api/drivers/<int:pk>/', DriverView.as_view()),
    path('api/managers/', ManagerListView.as_view()),
    path('api/managers/<int:pk>/', ManagerView.as_view()),
    path('api/clients/bulk/', BulkClientView.as_view()),
    path('api/drivers/bulk/', BulkDriverView.as_view())
]
