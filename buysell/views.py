from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from buysell.models import Category, Item, Area, City, State, Zipcode, Customer
from buysell.helper import url_coder

def index(request):
    if request.user.is_authenticated():
        zipcode = request.user.customer.zipcode.number
        area = Zipcode.objects.get(number=zipcode).city.state.area.slug
        states = Area.objects.get(slug=area).states.all()
        cities = City.objects.filter(state__in=states)
    else:
        cities = City.objects.all()

    items = Item.objects.filter(city__in=cities).order_by('-pub_date')

    return render(request, 'index.html', {'items': items})

def join(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'GET':
            next = request.GET.get('next')
        return render(request, 'join.html', {'next': next})

def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        zipcode = request.POST.get('zipcode')
        zipcode = Zipcode.objects.get(number=zipcode)

        if User.objects.filter(username=username).exists():
            return HttpResponse('username taken')
        elif User.objects.filter(email=email).exists():
            return HttpResponse('email in use')
        else:
            user = User.objects.create_user(username, email, password)
            add = Customer(user=user, zipcode=zipcode)
            add.save()
            return HttpResponse('account created')
    else:
        return HttpResponseRedirect('/')

def log_in(request):
    next = request.GET.get('next')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['zip'] = request.user.customer.zipcode.number
                if not next:
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponseRedirect(next)
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
    zipcode = request.user.customer.zipcode.number
    area = Zipcode.objects.get(number=zipcode).city.state.area.slug
    states = Area.objects.get(slug=area).states.all()
    cities = City.objects.filter(state__in=states).order_by('name')
    return render(request, 'post_create.html', {'categories': categories, 'cities': cities})

def post_process(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        details = request.POST.get('details')
        price = request.POST.get('price')
        url_code = url_coder()
        user = request.user
        category = request.POST.get('category')
        category = Category.objects.get(eng_name=category)
        city = request.POST.get('city')
        city = City.objects.get(slug=city)
        pub_date = timezone.now()

        item = Item(title=title, details=details, price=price, url_code=url_code, user=user, category=category, city=city, pub_date=pub_date)
        item.save()
        return HttpResponseRedirect('/post/' + url_code)
    else:
        # not a POST method
        return HttpResponseRedirect('/')

def post(request, url_code):
    item = Item.objects.get(url_code=url_code)

    return render(request, 'post.html', {'item': item})

def list(request, category=None, page=1):
    if request.user.is_authenticated():
        zipcode = request.user.customer.zipcode.number
        area = Zipcode.objects.get(number=zipcode).city.state.area.slug
        states = Area.objects.get(slug=area).states.all()
        cities = City.objects.filter(state__in=states)
    else:
        cities = City.objects.all()

    if not category:
        return HttpResponseRedirect('/list/all')
    elif category == 'all':
        items = Item.objects.filter(city__in=cities).order_by('-pub_date')
        return render(request, 'index.html', {'items': items})
    else:
        try:
            category = Category.objects.get(slug=category)
            items = Item.objects.filter(category=category, city__in=cities).order_by('-pub_date')
            return render(request, 'index.html', {'items': items})
        except Category.DoesNotExist:
            return HttpResponseRedirect('/')

def change_zip(request):
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        zipcode = Zipcode.objects.get(number=zipcode)

        if request.user.is_authenticated():
            user = User.objects.get(username=request.user.username)
            change = Customer.objects.get(user=user)
            change.zipcode = zipcode
            change.save()
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')
