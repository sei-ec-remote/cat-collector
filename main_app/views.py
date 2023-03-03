from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
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

# detail route for cats
# cat_id is defined, expecting an integer, in our url
def cats_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id)

    return render(request, 'cats/detail.html', { 'cat': cat })

class CatCreate(CreateView):
    model = Cat
    # the fields attribute is required for a createview. These inform the form
    fields = '__all__'
    # we could also have written our fields like this:
    # fields = ['name', 'breed', 'description', 'age']
    # we need to add redirects when we make a success
    # success_url = '/cats/{cat_id}'
    # or, we could redirect to the index page if we want
    # success_url = '/cats'
    # what django recommends, is adding a get_absolute_url method to the model

class CatUpdate(UpdateView):
    model = Cat
    # let's use custom fields to disallow renaming a cat
    fields = ['breed', 'description', 'age']

class CatDelete(DeleteView):
    model = Cat
    success_url = '/cats/'