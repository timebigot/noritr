import os
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from buysell.models import Category, Item, ItemImage, Area, City, State, Zipcode, Customer, PostView
from buysell.helper import url_coder, image_process
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def index(request):
    if request.user.is_authenticated():
        zipcode = request.user.customer.zipcode.number
        area = Zipcode.objects.get(number=zipcode).city.state.area.slug
        states = Area.objects.get(slug=area).states.all()
        cities = City.objects.filter(state__in=states)
    else:
        cities = City.objects.all()

    items_new = Item.objects.filter(city__in=cities).order_by('-pub_date')[:12]
    items_rand = Item.objects.filter(city__in=cities).order_by('?')[:6]

    return render(request, 'index.html', {'items_new': items_new, 'items_rand': items_rand})

def join(request):
    if request.user.is_authenticated():
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

        if 'image' in request.FILES:
            images = request.FILES.getlist('image')
            number  = len(images)
            
            # image count limit is 8
            if number <= 8:
                for image in images:
                    img_filename = image.name
                    img_type = image.content_type
                    img_size = len(image)

                    # image types are jpg, png, gif
                    if img_type == 'image/jpeg' or img_type == 'image/png' or img_type == 'image/gif':
                        # image size limited to 5MB or 50M bytes
                        if img_size <= 50000000:
                            img_name = url_coder(size=11)
                            img_ext = os.path.splitext(img_filename)[1].lower()
                            img_filename = img_name + img_ext
                            img_filepath = os.path.join(settings.MEDIA_ROOT, img_filename)
                            default_storage.save(img_filepath, ContentFile(image.read()))

                            img_db = ItemImage(name = img_filename, location = img_filename, item=item)
                            img_db.save()

                            thumb = Image.open(img_filepath)
                            W = thumb.size[0] / 2
                            H = thumb.size[1] / 2

                            filepath = os.path.join(settings.MEDIA_ROOT + '/thumbs/' + img_filename)

                            if W > H:
                                thumb = thumb.crop((W-H, H-H, W+H, H+H))
                                thumb = thumb.resize((244,244))
                            elif W < H:
                                thumb = thumb.crop((W-W, H-W, W+W, H+W))
                                thumb = thumb.resize((244,244))

                            thumb.save(filepath)

                        else:
                            return HttpResponse('The image is too big')
                    else:
                        return HttpResponse('Appropriate filetypes are jpg, png, and gif')

                return HttpResponseRedirect('/post/' + url_code)
            else:
                return HttpResponse('You may only upload up to 8 images')
        else:
            return HttpResponse('You need to add at least one image')

    else:
        # not a POST method
        return HttpResponseRedirect('/')

def post(request, url_code):
    item = Item.objects.get(url_code=url_code)
    images = ItemImage.objects.filter(item=item)
    user = request.user

    if request.user.is_authenticated():
        try:
            PostView.objects.get(item=item, user=user)
        except PostView.DoesNotExist:
            view = PostView(item=item, user=user)
            view.save()

    return render(request, 'post.html', {'item': item, 'images': images})

def list(request, category=None, page=1):
    print(page)
    if request.user.is_authenticated():
        zipcode = request.user.customer.zipcode.number
        area = Zipcode.objects.get(number=zipcode).city.state.area.slug
        states = Area.objects.get(slug=area).states.all()
        cities = City.objects.filter(state__in=states)
    else:
        cities = City.objects.all()

    cat = 'all'
    if not category:
        return HttpResponseRedirect('/list/all')
    elif category == 'all':
        item_list = Item.objects.filter(city__in=cities).order_by('-pub_date')
    else:
        try:
            category = Category.objects.get(slug=category)
            cat = category.slug
            item_list = Item.objects.filter(category=category, city__in=cities).order_by('-pub_date')
        except Category.DoesNotExist:
            return HttpResponseRedirect('/')

    paginator = Paginator(item_list, 24)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        return HttpResponseRedirect('/')
    except EmptyPage:
        return HttpResponseRedirect('/')

    return render(request, 'list.html', {'items': items, 'category': category})

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

def search(request):
    items = ''
    if request.method == 'GET':
        query = request.GET.get('q')
        items = Item.objects.filter(Q(title__icontains=query) | Q(details__icontains=query) | Q(category__eng_name__icontains=query) | Q(category__kor_name__icontains=query) | Q(user__username__icontains=query) | Q(city__name__icontains=query)).order_by('-pub_date')

    return render(request, 'list.html', {'items': items})
