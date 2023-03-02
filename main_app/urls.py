from django.urls import path
from . import views

urlpatterns = [
    # using an empty string here makes this our root route
    # views.home refers to a view that renders a file
    # the name='home' kwarg gives the route a name
    # naming routes is optional, but best practices
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    # paths for cats
    path('cats/', views.cats_index, name='index'),
    path('cats/<int:cat_id>/', views.cats_detail, name='detail'),
]