from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
#    path('accounts/login/', auth_views.LoginView.as_view()),
    path('<int:article_id>/', views.detail, name='detail'),
    path('next/', views.next, name='next'),
    path('findentity/', views.findentity, name='findentity'),
    path('createresolution/', views.createresolution, name='createresolution'),
    path('udpate/<int:article_id>', views.update, name='update'),
    path('', views.index, name='index'),
]