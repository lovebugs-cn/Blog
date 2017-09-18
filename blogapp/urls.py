# -*- coding=UTF-8 -*-
from django.conf.urls import url
from . import views

app_name = 'blogapp' # 告诉 Django 这个 urls.py 模块是属于 blogapp 应用的，这种技术叫做视图函数命名空间
urlpatterns = [
	url(r'^$',views.IndexView.as_view(),name='index'),  # 要将类视图转换成函数视图
	url(r'^post/(?P<pk>[0-9]+)/$',views.PostDetailView.as_view(),name='detail'),
	url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',views.ArchivesView.as_view(),name='archives'),
	url(r'^category/(?P<pk>[0-9]+)/$',views.CategoryView.as_view(),name='category'),
	url(r'^tag/(?P<pk>[0-9]+)/$',views.TagView.as_view(),name='tag'),
	url(r'^allpost/$',views.fullwidthView.as_view(),name='full-width'),
	url(r'about/$',views.about,name='about'),
	url(r'contact/$',views.contact,name='contact')
]