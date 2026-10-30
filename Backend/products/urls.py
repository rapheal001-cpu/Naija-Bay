from django.urls import path
from .views import (
    products_list_view,
    categories_list_view,
    products_detail_view,
    create_product_view,
    create_product_images_view,
    featured_products_view,
    my_products_view,
    favorite_products_view,
    recently_viewed_products_view,
    report_product_view,
    update_product_images_view,
    delete_product_image_view,
)


urlpatterns = [
    path('', products_list_view, name='products-list'),  # products list
    path('categories/', categories_list_view, name='categories-list'),  # products categories list
    path('create/', create_product_view, name='create-product'),  # create product
    path('create/images/', create_product_images_view, name='create-product-images'),  # create product images
    path('update/images/<int:product_id>/', update_product_images_view, name='update-product-images'),  # replace product images
    path('image/delete/<int:image_id>/', delete_product_image_view, name='delete-product-image'),  # delete one image
    path('featured/', featured_products_view, name='featured-products'),  # featured products
    path('my-listings/', my_products_view, name='my-listings'),  # current user's listings
    path('favorites/', favorite_products_view, name='favorite-products'),  # current user's favorites
    path('recently-viewed/', recently_viewed_products_view, name='recently-viewed-products'),  # view history
    path('report/<slug:product_slug>/', report_product_view, name='report-product'),  # report abuse
    path('detail/<slug:product_slug>/', products_detail_view, name='product-detail'),  # product detail
]
