from django.shortcuts import render,get_object_or_404
from comments.forms import CommentForm
from .models import Post,Category,Tag
import markdown
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from django.db.models.aggregates import Count
from django.db.models import Q
# Create your views here.
'''
def index(request):
	post_list = Post.objects.all().order_by('-created_time')
	paginator = Paginator(post_list,2)
	page = request.GET.get('page')
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		# 如果用户请求的页码号不是整数，显示第一页
		contacts = paginator.page(1)
	except EmptyPage:
		# 如果用户请求的页码号超过了最大页码号，显示最后一页
		contacts = paginator.page(paginator.num_pages)

	context = {'contacts':contacts}
	return render(request,'blog/index.html',context)
'''

class IndexView(ListView):
	model = Post
	template_name = 'blog/index.html'
	context_object_name = 'post_list'
	paginate_by = 5

	def get_context_data(self,**kwargs):
		context = super(IndexView,self).get_context_data(**kwargs)
		allpost_count = Post.objects.all().count()
		category_count = Category.objects.all().count()
		tags_count = Tag.objects.all().count()
		context.update({
			'allpost_count':allpost_count,
			'category_count':category_count,
			'tags_count':tags_count
			})
		return context


def detail(request,post_id):
	post = get_object_or_404(Post,pk=post_id)
	allpost_count = Post.objects.all().count()
	category_count = Category.objects.all().count()
	tags_count = Tag.objects.all().count()
	post.increase_views()
	md = markdown.Markdown(extensions=[
		'markdown.extensions.extra',
		'markdown.extensions.codehilite',
		'markdown.extensions.toc',
		])
	post.body = md.convert(post.body)
	post.toc = md.toc
	form = CommentForm()
	comment_list = post.comment_set.all()
	context = {'post':post,'allpost_count':allpost_count,'category_count':category_count,'tags_count':tags_count,'comment_list':comment_list}
	return render(request,'blog/detail.html',context)

# 获取所有分类
def categories(request):
	#category_list = Category.objects.all()
	category_list = Category.objects.annotate(num_posts=Count('post'))
	allpost_count = Post.objects.all().count()
	category_count = Category.objects.all().count()
	tags_count = Tag.objects.all().count()
	context = {'category_list':category_list,'category_count':category_count,'allpost_count':allpost_count,'tags_count':tags_count}
	return render(request,'blog/categories.html',context)

# 获取每个分类下的所有文章
def category(request,category_id):
	cate = get_object_or_404(Category,pk=category_id)
	post_list = Post.objects.filter(category=cate).order_by('-created_time') # 这里的category是Post的属性,model里定义的
	post_count = Post.objects.filter(category=cate).count()
	allpost_count = Post.objects.all().count()
	category_count = Category.objects.all().count()
	tags_count = Tag.objects.all().count()
	context = {'cate':cate,'post_list':post_list,'post_count':post_count,'allpost_count':allpost_count,'category_count':category_count,'tags_count':tags_count}
	return render(request,'blog/category.html',context)

def archives(request):
	date_list = Post.objects.dates('created_time','month',order='DESC')
	post_list = Post.objects.all().order_by('-created_time')
	allpost_count = Post.objects.all().count()
	category_count = Category.objects.all().count()
	tags_count = Tag.objects.all().count()
	context = {'date_list':date_list,'post_list':post_list,'allpost_count':allpost_count,'category_count':category_count,'tags_count':tags_count}
	return render(request,'blog/archives.html',context)

# 获取所有标签 
def tags(request):
	tags_list = Tag.objects.all()
	allpost_count = Post.objects.all().count()
	category_count = Category.objects.all().count()
	tags_count = Tag.objects.all().count()
	context = {'tags_list':tags_list,'tags_count':tags_count,'allpost_count':allpost_count,'category_count':category_count}
	return render(request,'blog/tags.html',context)

# 获取标签下所有文章
def tag(request,tag_id):
	tag = get_object_or_404(Tag,pk=tag_id)
	post_list = Post.objects.filter(tags=tag).order_by('created_time')
	post_count = Post.objects.filter(tags=tag).count()
	allpost_count = Post.objects.all().count()
	category_count = Category.objects.all().count()
	tags_count = Tag.objects.all().count()
	context = {'tag':tag,'post_list':post_list,'allpost_count':allpost_count,'category_count':category_count,'tags_count':tags_count,'post_count':post_count}
	return render(request,'blog/tag.html',context)

def search(request):
	q = request.GET.get('q')
	error_msg = ''

	if not q:
		error_msg = '请输入关键词'
		return render(request,'blog/index.html',{'error_msg':error_msg})

	post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
	return render(request,'blog/index.html',{'error_msg':error_msg,'post_list':post_list})

def about(request):
	allpost_count = Post.objects.all().count()
	category_count = Category.objects.all().count()
	tags_count = Tag.objects.all().count()
	context = {'allpost_count':allpost_count,'category_count':category_count,'tags_count':tags_count}
	return render(request,'blog/about.html',context)