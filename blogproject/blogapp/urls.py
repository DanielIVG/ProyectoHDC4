from django.urls import path
from .views import BlogListView, BlogDetailView, ReviewCreateView, CommentCreateView, BlogCreateView, register_view, login_view, logout_view, ChangePasswordView    
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordChangeDoneView

app_name = 'blogapp'


urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('blog/add/', BlogCreateView.as_view(), name='add_blog'),
    path('blog/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:pk>/review/', ReviewCreateView.as_view(), name='add_review'),
    path('blog/<int:blog_pk>/review/<int:review_pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cambiar_password/', ChangePasswordView.as_view(), name ='cambiar_password'),
    path('password_success/', PasswordChangeDoneView.as_view(template_name='blogapp/password_success.html'), name='password_success'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)