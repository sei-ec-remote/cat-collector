from django.db import models
from django.urls import reverse

# A tuple of 2-tuples
MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
)
# Create your models here.

class Cat(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()

    # dunder str method return cat name
    def __str__(self):
        return self.name
    
    # this is used to direct to the detail view for a resource
    def get_absolute_url(self):
        return reverse('detail', kwargs={'cat_id': self.id })

# Add new Feeding model below Cat model
class Feeding(models.Model):
    date = models.DateField('feeding date')
    meal = models.CharField(
        max_length=1,
        # add the choices field
        choices = MEALS,
        # set a default value for the meal to be 'B'
        default = MEALS[0][0]
    )
    # add cat foreign key reference
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        # this method is coming from django
        # produced like this: get_<name_of_field>_display()
        return f"{self.get_meal_display()} on {self.date}"