"""
URL configuration for agro_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


def home(request):
    return render(request, "home.html")   # 👈 uses base.html as layout

urlpatterns = [
    path("", home, name="home"),   # now root URL works
    path("admin/", admin.site.urls),
    path("products/", include("products.urls")),
    path("customers/", include("customers.urls")),
    path("banks/", include("banks.urls")),
    path("sales/", include("sales.urls")), 
    path("expenses/", include("expenses.urls")),
    path("logs/", include("logs_reports.urls")),
     path("ledger/", include("ledger.urls")),
     path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


