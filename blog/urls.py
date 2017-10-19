from django.conf.urls import url
from . import views

app_name = 'blog'
urlpatterns = [
	url(r'^$',views.IndexView.as_view(),name='index'),
	url(r'^post/(?P<post_id>[0-9]+)/$',views.detail,name='detail'),
	url(r'^categories/$',views.categories,name='categories'),
	url(r'archives/$',views.archives,name='archives'),
	url(r'^category/(?P<category_id>[0-9]+)/$',views.category,name='category'),
	url(r'^tags/$',views.tags,name='tags'),
	url(r'^tag/(?P<tag_id>[0-9]+)/$',views.tag,name='tag'),
	url(r'^about/$',views.about,name='about'),
	#url(r'^search/$',views.search,name='search'),
]