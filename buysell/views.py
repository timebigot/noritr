from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from buysell.models import Category, Item, Area, City, State
from buysell.helper import url_coder

def index(request):
    items = Item.objects.all()
    return render(request, 'index.html', {'items': items})

def gatekeeper(request):
    return render(request, 'gatekeeper.html', {})

def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return HttpResponse('username taken')
        elif User.objects.filter(email=email).exists():
            return HttpResponse('email in use')
        else:
            user = User.objects.create_user(username, email, password)
            return HttpResponse('account created')
    else:
        return HttpResponseRedirect('/')

def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse('activate your account')
        else:
            return HttpResponse('wrong username/password')
    else:
        # not a POST method
        return HttpResponseRedirect('/')

def log_out(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def post_create(request):
    categories = Category.objects.order_by('kor_name')
    area = request.user.customer.area
    state = State.objects.filter(area=area)
    cities = City.objects.filter(state__in=state).order_by('name')
    return render(request, 'post_create.html', {'categories': categories, 'cities': cities})

def post_process(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        details = request.POST.get('details')
        price = request.POST.get('price')
        url_code = url_coder()
        user = request.POST.get('user')
        user = User.objects.get(username=user)
        category = request.POST.get('category')
        category = Category.objects.get(eng_name=category)
        location = request.POST.get('city')
        location = City.objects.get(name=location)
        pub_date = timezone.now()

        item = Item(title=title, details=details, price=price, url_code=url_code, user=user, category=category, location=location, pub_date=pub_date)
        item.save()
        return HttpResponseRedirect('/post/' + url_code)
    else:
        # not a POST method
        return HttpResponseRedirect('/')

def post(request, url_code):
    item = Item.objects.get(url_code=url_code)

    return render(request, 'post.html', {'item': item})

@login_required
def list(request, area=False, category=None, page=1):
    if not area:
        area = Area.objects.all()
    else:
        area = Area.objects.get(slug=area)
    state = State.objects.filter(area=area)
    location = City.objects.filter(state__in=state)

    if not category:
        items = Item.objects.filter(location__in=location)
        return render(request, 'index.html', {'items': items})
    else:
        try:
            category = Category.objects.get(slug=category)
            items = Item.objects.filter(category=category, location__in=location)
            return render(request, 'index.html', {'items': items})
        except Category.DoesNotExist:
            category=category
