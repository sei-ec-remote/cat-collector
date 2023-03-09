from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import Cat, Toy, Photo
from .forms import FeedingForm
import uuid #python package for creating unique identifiers
import boto3 #what we'll use to connect to s3
from django.conf import settings
# imports for signing up
# we want to automatically log in signed up users
from django.contrib.auth import login
# we want to use the builtin form for our custom view for sign up
from django.contrib.auth.forms import UserCreationForm
# Import the login_required decorator
from django.contrib.auth.decorators import login_required
# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin

AWS_ACCESS_KEY = settings.AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
S3_BUCKET = settings.S3_BUCKET
S3_BASE_URL = settings.S3_BASE_URL

# Create your views here.
# view functions match urls to code (like controllers in Express)
# define our home view function
def home(request):
    return render(request, 'home.html')

# about route
def about(request):
    return render(request, 'about.html')

# index route for cats
@login_required
def cats_index(request):
    # just like we passed data to our templates in express
    # we pass data to our templates through our view functions
    # we can gather relations from SQL using our model methods
    # cats = Cat.objects.all()
    cats = Cat.objects.filter(user=request.user)

    return render(request, 'cats/index.html', { 'cats': cats })

# detail route for cats
# cat_id is defined, expecting an integer, in our url
@login_required
def cats_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id)

    # first we'll get a list of ids of toys the cat owns
    id_list = cat.toys.all().values_list('id')
    # then we'll make a list of the toys the cat does not have
    toys_cat_doesnt_have = Toy.objects.exclude(id__in=id_list)
    # instantiate FeedingForm to be rendered in the template
    feeding_form = FeedingForm()
    return render(request, 'cats/detail.html', { 'cat': cat, 'feeding_form': feeding_form, 'toys': toys_cat_doesnt_have })

class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    # the fields attribute is required for a createview. These inform the form
    # fields = '__all__'
    # we could also have written our fields like this:
    fields = ['name', 'breed', 'description', 'age']
    # we need to add redirects when we make a success
    # success_url = '/cats/{cat_id}'
    # or, we could redirect to the index page if we want
    # success_url = '/cats'
    # what django recommends, is adding a get_absolute_url method to the model
    def form_valid(self, form):
        # we can assign the logged in user's data(id) to the cat's create form
        form.instance.user = self.request.user

        return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    # let's use custom fields to disallow renaming a cat
    fields = ['breed', 'description', 'age']

class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats/'

@login_required
def add_feeding(request, cat_id):
    # create a ModelForm instance from the data in request.POST
    form = FeedingForm(request.POST)

    # we need to validate the form, that means "does it match our data?"
    if form.is_valid():
        # we dont want to save the form to the db until is has the cat id
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()
    return redirect('detail', cat_id=cat_id)

@login_required
def assoc_toy(request, cat_id, toy_id):
    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('detail', cat_id=cat_id)

@login_required
def unassoc_toy(request, cat_id, toy_id):
    Cat.objects.get(id=cat_id).toys.remove(toy_id)
    return redirect('detail', cat_id=cat_id)

# ToyList
class ToyList(LoginRequiredMixin, ListView):
    model = Toy
    template_name = 'toys/index.html'

# ToyDetail
class ToyDetail(LoginRequiredMixin, DetailView):
    model = Toy
    template_name = 'toys/detail.html'

# ToyCreate
class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = ['name', 'color']

    # define what the inherited method is_valid does(we'll update this later)
    def form_valid(self, form):
        # we'll use this later, but implement right now
        # we'll need this when we add auth
        # super allows for the original inherited CreateView function to work as it was intended
        return super().form_valid(form)

# ToyUpdate
class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['name', 'color']

# ToyDelete
class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'

# view for adding photos
@login_required
def add_photo(request, cat_id):
    # photo-file will be the name attribute of our form input
    # input type will be file
    photo_file = request.FILES.get('photo-file', None)
    # use conditional logic to make sure a file is present
    if photo_file:
        # S3_BASE_URL
        # if present, we'll use this to create a reference to the boto3 client
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        # create a unique key for our photos
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # we're going to use try....except which is just like try...catch in js
        # to handle the situation if anything should go wrong
        try:
            # if success
            s3.upload_fileobj(photo_file, S3_BUCKET, key)
            # build the full url string to upload to s3
            url = f"{S3_BASE_URL}{S3_BUCKET}/{key}"
            # if our upload(that used boto3) was successful
            # we want to use that photo location to create a Photo model
            photo = Photo(url=url, cat_id=cat_id)
            # save the instance to the db
            photo.save()
        except Exception as error:
            # print an error message
            print('Error uploading photo', error)
            return redirect('detail', cat_id=cat_id)
    # upon success redirect to detail page 
    return redirect('detail', cat_id=cat_id)

# view for signup
def signup(request):
    # this view is going to be like our class based views
    # because this is going to be able to handle a GET and a POST request
    error_message = ''
    if request.method == 'POST':
        # this is how to create a user form object that includes data from the browser
        form = UserCreationForm(request.POST)
        # now we check validity of the form, and handle our success and error situations
        if form.is_valid():
            # we'll add the user to the database
            user = form.save()
            # then we'll log the user in
            login(request, user)
            # redirect to our index page
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    # a bad POST or GET request will render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)