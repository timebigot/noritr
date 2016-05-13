from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from buysell.models import Category, Item, City, State
from buysell.helper import url_coder

def index(request):
    items = Item.objects.all()
    return render(request, 'index.html', {'items': items})

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

def create_post(request):
    categories = Category.objects.order_by('kor_name')
    state = State.objects.get(abbrev='va')
    cities = City.objects.filter(state=state).order_by('name')
    return render(request, 'create_post.html', {'categories': categories, 'cities': cities, 'state' : state.abbrev})

def process_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        details = request.POST.get('details')
        price = request.POST.get('price')
        url_code = url_coder()
        user = request.POST.get('user')
        user = User.objects.get(username=user)
        category = request.POST.get('category')
        category = Category.objects.get(eng_name=category)
        state = request.POST.get('state')
        state = State.objects.get(abbrev=state)
        location = request.POST.get('city')
        location = City.objects.get(name=location, state=state)
        pub_date = timezone.now()

        item = Item(title=title, details=details, price=price, url_code=url_code, user=user, category=category, location=location, pub_date=pub_date)
        item.save()
        # TODO redirect to post page
        #return HttpResponseRedirect('/post/' + post_code)
        return HttpResponseRedirect('/')
    else:
        # not a POST method
        return HttpResponseRedirect('/')
