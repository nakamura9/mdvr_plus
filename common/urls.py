from django.urls import path
from common import views



urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('config/<int:pk>', views.ConfigFormView.as_view(), name='config'),
    path('empty-page', views.EmptyPage.as_view(), name='empty-page'),
    path('daily/', views.daily, name='daily'),
]