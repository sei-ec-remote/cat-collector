from django.shortcuts import render
from .models import Cat

# temporary cats for building templates
# cats = [
#     {'name': 'Lolo', 'breed': 'tabby', 'description': 'furry little demon', 'age': 3},
#     {'name': 'Sachi', 'breed': 'calico', 'description': 'gentle and loving', 'age': 2},
#     {'name': 'Tubs', 'breed': 'ragdoll', 'description': 'chunky lil guy', 'age': 0},
# ]

# Create your views here.
# view functions match urls to code (like controllers in Express)
# define our home view function
def home(request):
    return render(request, 'home.html')

# about route
def about(request):
    return render(request, 'about.html')

# index route for cats
def cats_index(request):
    # just like we passed data to our templates in express
    # we pass data to our templates through our view functions
    # we can gather relations from SQL using our model methods
    cats = Cat.objects.all()
    return render(request, 'cats/index.html', { 'cats': cats })