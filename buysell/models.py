from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    #picture = models.ImageField(upload_to='profile_images', blank=True)
    
    def __str__(self):
        return self.user.username

class Category(models.Model):
    eng_name = models.CharField(max_length=20)
    kor_name = models.CharField(max_length=20)
    days_til_expire = models.IntegerField(default=30)

    def __str__(self):
        return self.eng_name

class Area(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=20)
    abbrev = models.CharField(max_length=2)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return self.abbrev

class City(models.Model):
    name = models.CharField(max_length=20)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Item(models.Model):
    title = models.CharField(max_length=50)
    price = models.CharField(max_length=10)
    url_code = models.CharField(max_length=5)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    location = models.ForeignKey(City, on_delete=models.CASCADE)
    pub_date = models.DateField()
    mod_date = models.DateField()
    is_sold = models.BooleanField(default=0)
    is_expired = models.BooleanField(default=0)
    is_removed = models.BooleanField(default=0)

    def __str__(self):
        return self.url_code

class ItemImage(models.Model):
    #location = models.ImageField(upload_to='item_images', blank=True)
    is_primary = models.BooleanField(default=0)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.location
