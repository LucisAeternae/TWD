from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context_dict)
    return response

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits_cookie = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                           '%Y-%m-%d %H:%M:%S')
    visits = visits_cookie
    if (datetime.now() - last_visit_time).seconds > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits

def category_visitor_handler(request, category_name_slug):
    visits_cookie = int(get_server_side_cookie(request, str(category_name_slug), '0'))
    visits_cookie += 1
    request.session[category_name_slug] = visits_cookie

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None
    category_visitor_handler(request, category_name_slug)
    context_dict['category_name_slug'] = request.session[category_name_slug]
    return render(request, 'rango/category.html', context_dict)

def about(request):
    context_dict = {'boldmessage': "Rango says: Here is about page"}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    return render(request, 'rango/about.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    visitor_cookie_handler(request)
    return render(request, 'rango/add_category.html', {'form': form})

def search(request, category_name_slug):
    context_dict = {}
    if request.method == 'POST':
        query = request.POST.get('query')
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category,
                                        title__contains=query)
        context_dict['search_result'] = pages
    return render(request,
                  'rango/search_result.html',
                  context=context_dict)

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
                return redirect(url)
            except:
                pass
    return HttpResponseRedirect(reverse('index'))

@login_required
def like_category(request):
    category_id = None
    url = '/rango/'
    if request.method == 'GET':
        category_id = request.GET['category_id']
    likes = 0
    if category_id:
        category = Category.objects.get(id=int(category_id))
        user_liked = category.get_users_liked()
        if request.user.id not in user_liked:
            print(category)
            if category:
                likes = category.likes + 1
                category.likes = likes
                user_liked.append(request.user.id)
                category.set_users_liked(user_liked)
                category.save()
    return HttpResponse(likes)

def get_category_list(max_results=0, query=''):
    cats_list = []
    if query:
        cats_list = Category.objects.filter(name__istartswith=query)
    if max_results > 0:
        if len(cats_list) > max_results:
            cats_list = list(category[:max_results])
    return cats_list

def sidebar_category_update(request):
    cats = []
    start_with = ''
    if request.method == 'GET':
        start_with = request.GET['suggestion']
    cats = get_category_list(8, start_with)
    return render(request, 'rango/cats.html', {'cats': cats})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    visitor_cookie_handler(request)
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    if request.user.is_authenticated:
        return HttpResponse('You already logged in. <br> <a href="/">Index</a>')
    else:
        registered = False
        if request.method == 'POST':
            user_form = UserForm(data=request.POST)
            profile_form = UserProfileForm(data=request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                user.set_password(user.password)
                user.save()
                profile = profile_form.save(commit=False)
                profile.user = UserForm
                if 'picture' in request.FILES:
                    profile.picture = request.FILES['picture']
                profile.save()
                registered = True
            else:
                print(user_form.errors, profile_form.errors)
        else:
            user_form = UserForm()
            profile_form = UserProfileForm()
        visitor_cookie_handler(request)
        return render(request,
                      'rango/register.html',
                      {'user_form': user_form,
                       'profile_form': profile_form,
                       'registered': registered})

def user_login(request):
    if request.user.is_authenticated:
        return HttpResponse('You already logged in. <br> <a href="/">Index</a>')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return HttpResponse('Your Rango account is disabled')
            else:
                print('Invalid {0}, {1}'.format(username, password))
                return HttpResponse('Invalid login details supplied')
        else:
            visitor_cookie_handler(request)
            return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
