from django.urls import path
from .views import (
    products_list_view, categories_list_view, products_detail_view, create_product_view,
    create_product_images_view, update_product_images_view, featured_products_view,
    delete_product_image_view,
)


urlpatterns = [
    path('', products_list_view, name='products-list'), # products list
    path('categories/', categories_list_view, name='categories-list'), # products categories list
    path('create/', create_product_view, name='create-product'), # create product
    path('create/images/', create_product_images_view, name='create-product-images'), # create product images
    path('featured/', featured_products_view, name='featured-products'), # featured products
    path('detail/<slug:product_slug>/', products_detail_view, name='product-detail'), # product detail
    path('update/images/<int:pk>/', update_product_images_view, name='update-product-images'), # update product images
    path('image/delete/<int:pk>/', delete_product_image_view, name='delete-product-image'), # delete one product image
]