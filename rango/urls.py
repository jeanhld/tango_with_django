from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name='about'),
	url(r'^add_profile/$', views.add_profile, name='add_profile'),
	url(r'^goto/(?P<page_id>[\w\-]+)/$', views.goto, name='goto'),
	url(r'^like_category/(?P<category_id>[\w\-]+)/$', views.like_category, name='like_category'),
    	url(r'^add_category/$', views.add_category, name='add_category'),
    	url(r'^register/$', views.register, name='register'),
	url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
	url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^profile/$', views.profile, name='profile'),
	url(r'^restricted/', views.restricted, name='restricted'),
	url(r'^suggest_category/$', views.suggest_category, name='suggest_category'),)
