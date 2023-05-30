from django.urls import path
from .views import home, create_post, detail_post, update_post, delete_post

app_name = 'blog'

urlpatterns = [
    path('', home, name='home'),
    path('create_post/', create_post, name='create_post'),
    path('<int:post_id>/', detail_post, name='detail_post'),
    path('<int:post_id>/update/', update_post, name='update_post'),
    path('<int:post_id>/delete/', delete_post, name='delete_post'),
]