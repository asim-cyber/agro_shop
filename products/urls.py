from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("add-category/", views.add_category, name="add_category"),
    path("add-product/", views.add_product, name="add_product"),
    path("list/", views.list_products, name="list_products"),
    path("update/<int:pk>/", views.update_product, name="update_product"),
    

    # Stock In (list + add)
    path("stock-in/<int:product_id>/", views.stock_in_list, name="stock_in_list"),
    path("stock-in/<int:product_id>/add/", views.add_stock_in, name="add_stock_in"),

   
    # Stock Out URLs
    path("stock-out-list/<int:product_id>/", views.stock_out_list, name="stock_out_list"),
    path("add-stock-out/<int:product_id>/", views.add_stock_out, name="add_stock_out"),

]
