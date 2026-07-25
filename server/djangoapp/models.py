from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Any other fields you would like to include in car make model
    country = models.CharField(max_length=50, blank=True)

    # __str__ method to print a car make object
    def __str__(self):
        return self.name


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
class CarModel(models.Model):
    # Many-To-One relationship to Car Make model
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    
    # Dealer ID (refers to dealer in external database/Cloudant)
    dealer_id = models.IntegerField()
    
    # Name
    name = models.CharField(max_length=100)
    
    # Type (CharField with a choices argument to provide limited choices)
    SEDAN = 'SEDAN'
    SUV = 'SUV'
    WAGON = 'WAGON'
    TRUCK = 'TRUCK'
    COUPE = 'COUPE'
    
    CAR_TYPES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (TRUCK, 'Truck'),
        (COUPE, 'Coupe'),
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default=SEDAN)
    
    # Year (IntegerField) with min value 2015 and max value 2023
    year = models.IntegerField(
        default=2023,
        validators=[
            MaxValueValidator(2023),
            MinValueValidator(2015)
        ]
    )

    # __str__ method to print a car make and car model object
    def __str__(self):
        return f"{self.car_make.name} {self.name}"