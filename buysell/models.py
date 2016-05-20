from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class Category(models.Model):
    eng_name = models.CharField(max_length=20)
    kor_name = models.CharField(max_length=20)
    slug = models.SlugField()
    days_til_expire = models.IntegerField(default=30)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.eng_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.eng_name

class Area(models.Model):
    name = models.CharField(max_length=10)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Area, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=20)
    abbrev = models.CharField(max_length=2)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='states')

    def __str__(self):
        return self.abbrev

class City(models.Model):
    name = models.CharField(max_length=20)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    slug = models.SlugField(default='')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(City, self).save(*args, **kwargs)

    def __str__(self):
        return '%s, %s' % (self.name, self.state)

class Zipcode(models.Model):
    number = models.CharField(max_length=5)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='zipcodes')

    def __str__(self):
        return '%s - %s' % (self.number, self.city)

class Customer(models.Model):
    user = models.OneToOneField(User)
    zipcode = models.ForeignKey(Zipcode, on_delete=models.CASCADE)
    #picture = models.ImageField(upload_to='profile_images', blank=True)
    
    def __str__(self):
        return self.user.username

class Item(models.Model):
    title = models.CharField(max_length=50)
    price = models.CharField(max_length=10)
    details = models.CharField(max_length=250)
    url_code = models.CharField(max_length=7)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE, default='')
    pub_date = models.DateTimeField()
    mod_date = models.DateField(blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.title, self.url_code)

class ItemImage(models.Model):
    #location = models.ImageField(upload_to='item_images', blank=True)
    is_primary = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.location
