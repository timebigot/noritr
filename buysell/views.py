import os
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings as base_set
from django.db.models import Q
from django.utils import timezone
from buysell.models import *
from buysell.helper import url_coder, image_process, paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from datetime import datetime, timedelta
from django.db.models import Count, Max
from parser import missy_parser
from django.contrib import messages

def index(request):
    if request.user.is_authenticated():
        zipcode = request.user.customer.zipcode.number
        area = Zipcode.objects.get(number=zipcode).city.state.area.slug
        states = Area.objects.get(slug=area).states.all()
        cities = City.objects.filter(state__in=states)
    else:
        cities = City.objects.all()

    one_day = datetime.now() - timedelta(hours=24)
    items_new = Item.objects.filter(city__in=cities, is_expired=False, is_removed=False).order_by('-pub_date')[:12]
    items_rand = Item.objects.filter(city__in=cities, pub_date__lte=one_day).order_by('?')[:6]
    items_saved = []
    if request.user.is_authenticated():
        faves = Favorite.objects.filter(user=request.user).values('item').order_by('-pk')[:6]
        for fave in faves:
            fave_item = Item.objects.get(pk=fave['item'])
            items_saved.append(fave_item)

    return render(request, 'index.html', {'items_new': items_new, 'items_rand': items_rand, 'items_saved': items_saved})

def join(request):
    if request.user.is_authenticated():
        return redirect('/')
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

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is taken')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email in use')

        try:
            zipcode = Zipcode.objects.get(number=zipcode)
        except:
            messages.error(request, 'Area not supported')
        else:
            user = User.objects.create_user(username, email, password)
            add = Customer(user=user, zipcode=zipcode)
            add.save()
            messages.success(request, 'Account created!')
        return render(request, 'join.html')
    else:
        return redirect('/')

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
                    return redirect('/')
                else:
                    return redirect(next)
            else:
                return HttpResponse('activate your account')
        else:
            messages.error(request, 'Wrong username/password')
            return redirect('/join')
    else:
        # not a POST method
        return redirect('/')

@login_required
def log_out(request):
    logout(request)
    return redirect('/')

@login_required
def settings(request):
    if request.method == 'POST':
        if request.POST.get('profile'):
            email = request.POST.get('email')
            number = request.POST.get('zipcode')

            try:
                zipcode = Zipcode.objects.get(number=number)
            except Zipcode.DoesNotExist:
                return HttpResponse('Your area is not supported')
            else:
                user = User.objects.get(username=request.user.username)
                user.email = email
                user.customer.zipcode = zipcode

                user.save()
                user.customer.save()

                messages.success(request, 'Successfully updated your profile!')
                return render(request, 'settings.html')
        elif request.POST.get('password'):
            pass_cur = request.POST.get('pass_cur')
            pass_new = request.POST.get('pass_new')
            pass_conf = request.POST.get('pass_conf')

            if pass_new == pass_conf:
                auth = authenticate(username=request.user.username, password=pass_cur)
                if auth is not None:
                    user = User.objects.get(username=request.user.username)
                    user.set_password(pass_new)
                    user.save()
                    return redirect('/join')
                else:
                    messages.error(request, 'Wrong password!')
                    return render(request, 'settings.html')
            else:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'settings.html')
        else:
            return redirect('/')
    else:
        return render(request, 'settings.html')

@login_required
def post_create(request):
    categories = Category.objects.order_by('kor_name')
    zipcode = request.user.customer.zipcode.number
    area = Zipcode.objects.get(number=zipcode).city.state.area.slug
    states = Area.objects.get(slug=area).states.all()
    cities = City.objects.filter(state__in=states).order_by('name')
    return render(request, 'post_create.html', {'categories': categories, 'cities': cities})

@login_required
def post_edit(request, url_code):
    if Item.objects.get(url_code=url_code).user == request.user:
        categories = Category.objects.order_by('kor_name')
        zipcode = request.user.customer.zipcode.number
        area = Zipcode.objects.get(number=zipcode).city.state.area.slug
        states = Area.objects.get(slug=area).states.all()
        cities = City.objects.filter(state__in=states).order_by('name')
        item = Item.objects.get(url_code=url_code)
        repost = False
        return render(request, 'post_create.html', {'categories': categories, 'cities': cities, 'item': item, 'repost': repost})
    else:
        return redirect('/')

@login_required
def post_repost(request, url_code):
    try:
        Item.objects.get(url_code=url_code, is_removed=True).user == request.user
    except Item.DoesNotExist:
        return redirect('/')
    else:
        categories = Category.objects.order_by('kor_name')
        zipcode = request.user.customer.zipcode.number
        area = Zipcode.objects.get(number=zipcode).city.state.area.slug
        states = Area.objects.get(slug=area).states.all()
        cities = City.objects.filter(state__in=states).order_by('name')
        item = Item.objects.get(url_code=url_code)
        repost = True
        return render(request, 'post_create.html', {'categories': categories, 'cities': cities, 'item': item, 'repost': repost})

@login_required
def post_remove(request):
    if request.method == 'POST':
        item_code = request.POST.get('item_code')
        item = Item.objects.get(url_code=item_code)
        item.is_removed=True
        item.save()

        return redirect('/store/manage')

@login_required
def post_process(request):
    if request.method == 'POST':

        if request.POST.get('edit'):
            title = request.POST.get('title')
            details = request.POST.get('details')
            url_code = request.POST.get('item_code')
            category = request.POST.get('category')
            category = Category.objects.get(eng_name=category)
            city = request.POST.get('city')
            city = City.objects.get(slug=city)

            item = Item.objects.get(url_code=url_code)
            item.title = title
            item.details = details
            item.category = category
            item.city = city
            if request.POST.get('repost'):
                exp_date = item.pub_date + timedelta(days=item.category.days_til_expire)
                if timezone.now() >= exp_date:
                    #price = request.POST.get('price')
                    #item.price = price
                    item.pub_date = timezone.now()
                item.is_removed = False

            item.save()

            messages.success(request, 'You have successfully edited the item')
            return redirect('/')

        elif request.POST.get('create'):
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
                            # image size limited to 5MB
                            if img_size <= 50000000:
                                img_name = url_coder(size=11)
                                img_ext = os.path.splitext(img_filename)[1].lower()
                                img_filename = img_name + img_ext
                                img_filepath = os.path.join(base_set.MEDIA_ROOT, img_filename)
                                default_storage.save(img_filepath, ContentFile(image.read()))

                                img_db = ItemImage(name = img_filename, location = img_filename, item=item)
                                img_db.save()

                                thumb = Image.open(img_filepath)
                                W = thumb.size[0] / 2
                                H = thumb.size[1] / 2

                                filepath = os.path.join(base_set.MEDIA_ROOT + '/thumbs/' + img_filename)

                                if W > H:
                                    thumb = thumb.crop((W-H, H-H, W+H, H+H))
                                    thumb = thumb.resize((350,350))
                                elif W < H:
                                    thumb = thumb.crop((W-W, H-W, W+W, H+W))
                                    thumb = thumb.resize((300,300))

                                thumb.save(filepath)

                            else:
                                messages.error(request, 'The image is too big')
                                return render(request, 'post_create.html')
                        else:
                            messages.error(request, 'Appropriate filetypes are jpg, png, and gif')
                            return render(request, 'post_create.html')

                    return redirect('/post/' + url_code)
                else:
                    messages.error(request, 'You may only upload up to 8 images')
                    return render(request, 'post_create.html')
            else:
                    messages.error(request, 'You need to add at least one image')
                    return render(request, 'post_create.html')
        else:
            # not a POST method
            return redirect('/')

def post(request, url_code):
    item = Item.objects.get(url_code=url_code)
    if not item.is_removed:
        images = ItemImage.objects.filter(item=item)
        user = request.user
        more = Item.objects.filter(user=item.user).all().count()
        if more > 6:
            more_items = Item.objects.filter(user=item.user).exclude(url_code=url_code).order_by('?')[:6]
        else:
            more_items = None

        if request.user.is_authenticated():
            try:
                find = PostView.objects.get(item=item, user=user)
            except PostView.DoesNotExist:
                view = PostView(item=item, user=user)
                view.save()
            else:
                view = PostView(item=item, user=user)
                view.save()
                find.delete()
        try:
            fave = Favorite.objects.get(item=item)
        except Favorite.DoesNotExist:
            favorited = False
        else:
            favorited = True

        return render(request, 'post.html', {'item': item, 'images': images, 'more_items': more_items, 'favorited': favorited})
    else:
        messages.error(request, 'This item has been removed')
        return redirect('/')

def list(request, category=None, page=1):
    if request.user.is_authenticated():
        zipcode = request.user.customer.zipcode.number
        area = Zipcode.objects.get(number=zipcode).city.state.area.slug
        states = Area.objects.get(slug=area).states.all()
        cities = City.objects.filter(state__in=states)
    else:
        cities = City.objects.all()

    cat = 'new'
    if not category:
        return redirect('/list/new')
    elif category == 'new':
        item_list = Item.objects.filter(city__in=cities, is_expired=False, is_removed=False).order_by('-pub_date').exclude(is_removed=True)
        img_title = 'new'
    elif category == 'free':
        item_list = Item.objects.filter(city__in=cities, price='0', is_expired=False, is_removed=False).order_by('-pub_date').exclude(is_removed=True)
        img_title = 'free'
    else:
        try:
            category = Category.objects.get(slug=category)
            cat = category.slug
            item_list = Item.objects.filter(category=category, city__in=cities, is_expired=False, is_removed=False).order_by('-pub_date').exclude(is_removed=True)
            img_title = category.slug
        except Category.DoesNotExist:
            return redirect('/')

    items = paginator(item_list, page)
    if not items:
        return redirect('/')
    else:
        return render(request, 'list.html', {'items': items, 'title': category, 'view': 'list', 'img_title': img_title})

@login_required
def change_zip(request):
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        try:
            zipcode = Zipcode.objects.get(number=zipcode)
        except:
            messages.error(request, 'That area is not yet supported')
            return redirect('/')
        else:
            if request.user.is_authenticated():
                user = User.objects.get(username=request.user.username)
                change = Customer.objects.get(user=user)
                change.zipcode = zipcode
                change.save()
                messages.success(request, 'You successfully changed your zipcode')
                return redirect('/')
            else:
                return redirect('/')
    else:
        return redirect('/')

def search(request, query='', page=1):
    items = ''
    if request.method == 'POST':
        query = request.POST.get('query')
        return redirect('/search/' + query)
    else:
        if not query:
            title = 'None'
            return HttpResponse('No results')
        else:
            title = query
            i = Item.objects
            item_list = i.filter(
                    Q(title__icontains=query) | 
                    Q(details__icontains=query) | 
                    Q(category__eng_name__icontains=query) | 
                    Q(category__kor_name__icontains=query) | 
                    Q(user__username__icontains=query) | 
                    Q(city__name__icontains=query)).order_by('-pub_date')
            item_list = item_list.exclude(is_removed=True)


            items = paginator(item_list, page)
            return render(request, 'list.html', {'items': items, 'search': title, 'view': 'search', 'img_title': 'search'})

@login_required
def message(request):
    if request.method == 'POST':
        content = request.POST.get('message')
        sender = request.user
        sender = User.objects.get(username = sender)
        recipient = request.POST.get('recipient')
        recipient = User.objects.get(username = recipient)
        item_code = request.POST.get('item')
        item = Item.objects.get(url_code = item_code)
        url_code = request.POST.get('url_code')

        m= Message.objects

        if m.filter(item=item, sender=recipient):
            msg_code = url_code
        elif m.filter(item=item, recipient=recipient):
            msg_code = url_code
        else:
            msg_code = url_coder(size=9)

        msg = Message(sender = sender, recipient = recipient, content = content, item = item, url_code=msg_code)
        msg.save()

        if request.POST.get('url_code'):
            return redirect('/inbox/' + msg_code)
        else:
            messages.success(request, 'Message sent!')
            return redirect('/post/' + item_code)
    else:
        return redirect('/')

@login_required
def inbox(request, url_code=None):
    if request.user.is_authenticated:
        user = request.user
        if Message.objects.filter(url_code=url_code):
            msgs = Message.objects.filter(url_code=url_code)
            user = User.objects.get(username=request.user.username)
            if not msgs.exclude(sender=user).exclude(recipient=user):
                try:
                    recipient = Message.objects.filter(url_code=url_code, sender=user).first().recipient
                except:
                    recipient = Message.objects.filter(url_code=url_code, recipient=user).first().sender
                item_pk = msgs.values('item').distinct()[0]['item']
                item = Item.objects.get(pk=item_pk)

                unread = Message.objects.filter(url_code=url_code, recipient=request.user, is_read=False)
                for msg in unread:
                    msg.is_read = True
                    msg.save()
            else:
                return redirect('/')

            return render(request, 'thread.html', {'msgs':msgs, 'recipient':recipient, 'item':item, 'url_code':url_code})
        else:
            if url_code == None:
                msgs = Message.objects.values('url_code').annotate(date=Max('pub_date')).order_by('-date').filter(Q(sender=user)|Q(recipient=user))
                return render(request, 'inbox.html', {'msgs':msgs})
            elif url_code == 'unread':
                msgs = Message.objects.values('url_code').annotate(date=Max('pub_date')).order_by('-date').filter(recipient=user, is_read=False)
                return render(request, 'inbox.html', {'msgs':msgs})
            elif url_code == 'sent':
                msgs = Message.objects.values('url_code').annotate(date=Max('pub_date')).order_by('-date').filter(sender=user)
                return render(request, 'inbox.html', {'msgs':msgs})
            else:
                return redirect('/inbox')
    else:
        return redirect('/')

@login_required
def bot(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            url = request.POST.get('url')
            cat = request.POST.get('cat')
            city = request.POST.get('city')

            url_code = missy_parser(url, cat, city)

            return redirect('/post/' + url_code)
        else:
            categories = Category.objects.order_by('eng_name')
            zipcode = request.user.customer.zipcode.number
            area = Zipcode.objects.get(number=zipcode).city.state.area.slug
            states = Area.objects.get(slug=area).states.all()
            cities = City.objects.filter(state__in=states).order_by('name')
            return render(request, 'bot.html', {'categories': categories, 'cities': cities})
    else:
        return redirect('/')

@login_required
def store_manage(request):
    items = Item.objects.filter(user=request.user).order_by('-pub_date')
    return render(request, 'store_manage.html', {'items':items})

def store(request, seller, page=1):
    try:
        user = User.objects.get(username=seller)
    except User.DoesNotExist:
        return HttpResponse(user)
    else:
        item_list = Item.objects.filter(user=user).all().order_by('-pub_date').exclude(is_removed=True)
        title = user.username + "'s Store"

        items = paginator(item_list, page)
        if not items:
            return redirect('/')
        else:
            return render(request, 'list.html', {'items':items, 'title':title, 'seller':user.username, 'view':'store'})

@login_required
def history(request, page=1):
    if request.user.is_authenticated():
        title = 'history'
        views = PostView.objects.filter(user=request.user).values('item').order_by('-pk')
        item_list = []
        for view in views:
            view_item = Item.objects.get(pk=view['item'])
            item_list.append(view_item)
        items = paginator(item_list, page)
        if not items:
            return redirect('/')
        else:
            return render(request, 'list.html', {'items':items, 'title':title, 'img_title': 'history'})
    else:
        return redirect('/')

@login_required
def favorites(request, page=1):
    if request.user.is_authenticated():
        # process favorites
        if request.method == 'POST':
            item_code = request.POST.get('item_code')
            item = Item.objects.get(url_code=item_code)
            try:
                find = Favorite.objects.get(item=item)
            except Favorite.DoesNotExist:
                fave = Favorite(user=request.user, item=item, fav_date=timezone.now())
                fave.save()
                messages.success(request, 'Favorited ' + item.title)
            else:
                find.delete()
                messages.success(request, 'Unfavorited ' + item.title)

            return redirect('/post/' + item_code)
        # list favorites
        else:
            title = 'favorites'
            faves = Favorite.objects.filter(user=request.user).values('item').order_by('-pk')
            item_list = []
            for fave in faves:
                fave_item = Item.objects.get(pk=fave['item'])
                item_list.append(fave_item)
            items = paginator(item_list, page)
            if not items:
                return redirect('/')
            else:
                return render(request, 'list.html', {'items':items, 'title':title, 'img_title': 'favorites'})
    else:
        return redirect('/')
