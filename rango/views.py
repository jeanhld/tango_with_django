from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.models import User
from datetime import datetime

@login_required
def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		cat = None

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
			
				return category(request, category_name_slug)
		else:
			print form.errors
	else:
		form = PageForm()

	context_dict = {'form':form, 'category': cat}

	return render(request, 'rango/add_page.html', context_dict)

@login_required
def add_category(request):
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)

			return index(request)
		else:
			print form.errors
	else:
		form = CategoryForm()

	return render(request, 'rango/add_category.html', {'form': form})

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	visits = int(request.COOKIES.get('visits', '1'))
	context_dict = {'categories': category_list, 'pages': page_list, 'visits': visits}

	reset_last_visit_time = False
	response = render(request, 'rango/index.html', context_dict)
	
	if 'last_visit' in request.COOKIES:
		last_visit = request.COOKIES['last_visit']
	
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).days > 0:
			visits = visits + 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True
		context_dict['visits'] = visits
		response = render(request, 'rango/index.html', context_dict)

	if reset_last_visit_time:
		response.set_cookie('last_visit', datetime.now())
		response.set_cookie('visits', visits)

	return response

def about(request):
	if request.COOKIES.get('visits'):
		count = request.COOKIES.get('visits')
	else:
		count = 0
		
	context_dict = {
		'about_message': "See a picture of me:",
		'visits': count
	}

	return render(request, 'rango/about.html', context_dict)

def category(request, category_name_slug):
	context_dict = {}
	try:
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name
		if request.method == 'POST':
			search = request.POST.get('search')
			context_dict['search'] = True
			pages = Page.objects.filter(category=category, title__contains=search).order_by('-views')
		else:
			pages = Page.objects.filter(category=category).order_by('-views')[:5]
			category.view += 1
			category.save()

		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		pass

	return render(request, 'rango/category.html', context_dict)

def register(request):
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()

			registered = True

		else:
			print user_form.errors, profile_form.errors

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request,
		'rango/register.html',
		{'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )

def user_login(request):	
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse("Your Rango account is disabled.")
		else:
			return render(request, 'rango/login.html', {'error':'Invalid username or password'})
	else:
		return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
	logout(request)

	return HttpResponseRedirect('/rango/')

def goto(request, page_id):
	try:
		page = Page.objects.get(id=page_id)
	except:
		return HttpResponseRedirect('/rango/')

	page.views += 1
	page.save()
	url = page.url
	
	return redirect(url)

def add_profile(request):
	user = request.user
	if request.method == 'POST':
		form = UserProfileForm(request.POST)
		if form.is_valid():
			if user:
				user_profile = form.save(commit=False)
				user_profile.user = user
				user_profile.save()
			
				return index(request)
		else:
			print form.errors
	else:
		form = UserProfileForm()

	context_dict = {'form':form, 'user': user}

	return render(request, 'rango/profile_registration.html', context_dict)

def profile(request):
	current_user = request.user
	user_profile = UserProfile.objects.get(user=current_user)
	context_dict = {'user': current_user, 'user_profile': user_profile}
	return render(request, 'rango/profile.html', context_dict)

@login_required
def like_category(request, category_id):
	cat_id = None
	if request.method == 'GET':
		cat_id = category_id

	likes = 0
	if cat_id:
		cat = Category.objects.get(id=int(cat_id))
		if cat:
			likes = cat.likes + 1
			cat.likes =  likes
			cat.save()

	return HttpResponse(likes)

def suggest_category(request):

	cat_list = []
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.GET['suggestion']

	cat_list = get_category_list(8, starts_with)

	return render(request, 'rango/category_list.html', {'cat_list': cat_list })


def get_category_list(max_results=0, starts_with=''):
	cat_list = []
	if starts_with:
		cat_list = Category.objects.filter(name__contains=starts_with)

	if max_results > 0:
		if len(cat_list) > max_results:
			cat_list = cat_list[:max_results]

	return cat_list