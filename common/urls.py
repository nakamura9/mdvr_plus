from django.urls import path
from common import views

app_name = 'app'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('config/<int:pk>', views.ConfigFormView.as_view(), name='config'),
    path('empty-page', views.EmptyPage.as_view(), name='empty-page'),
    path('error-page', views.ErrorPage.as_view(), name='error-page'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('api/config/<int:pk>', views.ConfigAPIView.as_view(), name='config-api'),
]