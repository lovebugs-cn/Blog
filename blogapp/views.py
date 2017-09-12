# -*- coding=UTF-8 -*-
import markdown
from django.shortcuts import render,get_object_or_404
from .models import Post, Category, Tag
from comments.forms import CommentForm
from django.views.generic import ListView,DetailView
from django.db.models import Q
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
# Create your views here.

class IndexView(ListView):                  # ListView 是从数据库中获取某个模型列表数据的，所以 IndexView 继承 ListView
	model = Post                          # 将 model 指定为 Post，告诉 Django 要获取的模型是 Post
	template_name = 'blogapp/index.html'  # 指定这个视图渲染的模板
	context_object_name = 'post_list'     # 指定获取的模型列表数据保存的变量名。这个变量会被传递给模板

	paginate_by = 5                       # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章

	# 分页效果扩展

	def get_context_data(self, **kwargs):
		"""
		在视图函数中将模板变量传递给模板是通过给 render 函数的 context 参数传递一个字典实现的，
		例如 render(request, 'blog/index.html', context={'post_list': post_list})，
		这里传递了一个 {'post_list': post_list} 字典给模板。
		在类视图中，这个需要传递的模板变量字典是通过 get_context_data 获得的，
		所以复写该方法，以便能够自己再插入一些我们自定义的模板变量进去。
		"""

		# 首先获得父类生成的传递给模板的字典。
		context = super().get_context_data(**kwargs)

		# 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
		# paginator 是 Paginator 的一个实例，
		# page_obj 是 Page 的一个实例，
		# is_paginated 是一个布尔变量，用于指示是否已分页。
		# 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
		# 关于什么是 Paginator，Page 类在 Django Pagination 简单分页：http://zmrenwu.com/post/34/ 中已有详细说明。
		# 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
		paginator = context.get('paginator')
		page = context.get('page_obj')
		is_paginated = context.get('is_paginated')

		# 调用自己写的 pagination_data 方法获得显示分页导航条需要的数据，见下方。
		pagination_data = self.pagination_data(paginator, page, is_paginated)

		# 将分页导航条的模板变量更新到 context 中，注意 pagination_data 方法返回的也是一个字典。
		context.update(pagination_data)

		# 将更新后的 context 返回，以便 ListView 使用这个字典中的模板变量去渲染模板。
		# 注意此时 context 字典中已有了显示分页导航条所需的数据。
		return context

	def pagination_data(self, paginator, page, is_paginated):
		if not is_paginated:
			# 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
			return {}

		# 当前页左边连续的页码号，初始值为空
		left = []

		# 当前页右边连续的页码号，初始值为空
		right = []

		# 标示第 1 页页码后是否需要显示省略号
		left_has_more = False

		# 标示最后一页页码前是否需要显示省略号
		right_has_more = False

		# 标示是否需要显示第 1 页的页码号。
		# 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
		# 其它情况下第一页的页码是始终需要显示的。
		# 初始值为 False
		first = False

		# 标示是否需要显示最后一页的页码号。
		# 需要此指示变量的理由和上面相同。
		last = False

		# 获得用户当前请求的页码号
		page_number = page.number

		# 获得分页后的总页数
		total_pages = paginator.num_pages

		# 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
		page_range = paginator.page_range

		if page_number == 1:
			# 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
			# 此时只要获取当前页右边的连续页码号，
			# 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
			# 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
			right = page_range[page_number:page_number + 2]

			# 如果最右边的页码号比最后一页的页码号减去 1 还要小，
			# 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
			if right[-1] < total_pages - 1:
				right_has_more = True

			# 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
			# 所以需要显示最后一页的页码号，通过 last 来指示
			if right[-1] < total_pages:
				last = True

		elif page_number == total_pages:
			# 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
			# 此时只要获取当前页左边的连续页码号。
			# 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
			# 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
			left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

			# 如果最左边的页码号比第 2 页页码号还大，
			# 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
			if left[0] > 2:
				left_has_more = True

			# 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
			# 所以需要显示第一页的页码号，通过 first 来指示
			if left[0] > 1:
				first = True
		else:
			# 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
			# 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
			left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
			right = page_range[page_number:page_number + 2]

			# 是否需要显示最后一页和最后一页前的省略号
			if right[-1] < total_pages - 1:
				right_has_more = True
			if right[-1] < total_pages:
				last = True

			# 是否需要显示第 1 页和第 1 页后的省略号
			if left[0] > 2:
				left_has_more = True
			if left[0] > 1:
				first = True

		data = {
			'left': left,
			'right': right,
			'left_has_more': left_has_more,
			'right_has_more': right_has_more,
			'first': first,
			'last': last,
		}

		return data
'''
def detail(request,pk):
	post = get_object_or_404(Post,pk=pk)

	# 阅读量+1
	post.increase_views()

	post.body = markdown.markdown(post.body,extensions=[
												'markdown.extensions.extra',
												'markdown.extensions.codehilite',
												'markdown.extensions.toc',
											])
	form = CommentForm()
	# 获取这篇 post 下的全部评论
	comment_list = post.comment_set.all()
	# 将文章、表单、以及文章下的评论列表作为模板变量传给 detail.html 模板，以便渲染相应数据。
	context = {'post':post, 'form':form, 'comment_list':comment_list}
	return render(request,'blogapp/detail.html',context=context)

详情页的视图函数：根据从 URL 捕获的文章 id（也就是 pk，这里 pk 和 id 是等价的）获取数据库中文章 id 为该值的记录，
然后传递给模板。注意这里用到了从 django.shortcuts 模块导入的 get_object_or_404 方法，
其作用就是当传入的 pk 对应的 Post 在数据库存在时，就返回对应的 post，如果不存在，就给用户返回一个 404 错误，表明用户请求的文章不存在。

'''

# 详情页用类视图来写

class PostDetailView(DetailView):
	model = Post
	template_name = 'blogapp/detail.html'
	context_object_name = 'post'

	def get(self,request,*args,**kwargs):
		# 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
		# get 方法返回的是一个 HttpResponse 实例
		# 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
		response = super(PostDetailView,self).get(request,*args,**kwargs)

		# 将文章阅读量 +1,注意 self.object 的值就是被访问的文章 post
		self.object.increase_views()

		# 视图必须返回一个 HttpResponse 对象
		return response

	def get_object(self,queryset=None):
		# 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
		post = super(PostDetailView,self).get_object(queryset=None)
		md = markdown.Markdown(extensions=['markdown.extensions.extra',
															'markdown.extensions.codehilite',
															TocExtension(slugify=slugify),
														])
		post.body = md.convert(post.body)
		post.toc = md.toc
		return post

	def get_context_data(self,**kwargs):
		# 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），还要把评论表单、post 下的评论列表传递给模板。
		context = super(PostDetailView,self).get_context_data(**kwargs)
		form = CommentForm()
		comment_list = self.object.comment_set.all()
		context.update({'form':form,'comment_list':comment_list})
		return context

# 归档
class ArchivesView(IndexView):
	def get_queryset(self):
		year = self.kwargs.get('year')
		month = self.kwargs.get('month')
		return super(ArchivesView,self).get_queryset().filter(created_time__year=year,created_time__month=month)

# 分类
class CategoryView(IndexView):  # 继承自上面的IndexView
	# model = Post
	# template_name = 'blogapp/index.html'
	# context_object_name = 'post_list'

	def get_queryset(self):
		cate = get_object_or_404(Category,pk=self.kwargs.get('pk'))
		return super(CategoryView,self).get_queryset().filter(category=cate)

	paginate_by = 2
# 覆写了父类的 get_queryset 方法。
# 该方法默认获取指定模型的全部列表数据。
# 为了获取指定分类下的文章列表数据，覆写该方法，改变它的默认行为。

'''
首先是需要根据从 URL 中捕获的分类 id（也就是 pk）获取分类，
需要注意一点的是，在类视图中，从 URL 捕获的命名组参数值保存在实例的 kwargs 属性（是一个字典）里，
非命名组参数值保存在实例的 args 属性（是一个列表）里。
所以这里使用了 self.kwargs.get('pk') 来获取从 URL 捕获的分类 id 值。
然后调用父类的 get_queryset 方法获得全部文章列表，
紧接着就对返回的结果调用了 filter 方法来筛选该分类下的全部文章并返回。
'''

# 标签视图函数
class TagView(IndexView):
	def get_queryset(self):
		tag = get_object_or_404(Tag,pk=self.kwargs.get('pk'))
		return super(TagView,self).get_queryset().filter(tags=tag)


# 搜索功能
def search(request):
	q = request.GET.get('q')
	error_msg = ''

	if not q:
		error_msg = '请输入关键词'
		return render(request,'blogapp/index.html',{'error_msg':error_msg})

	post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
	return render(request,'blogapp/index.html',{'error_msg':error_msg,'post_list':post_list})
'''
首先使用 request.GET.get('q') 获取到用户提交的搜索关键词。
用户通过表单 get 方法提交的数据 Django 保存在 request.GET 里，这是一个类似于 Python 字典的对象，
所以要使用 get 方法从字典里取出键 q 对应的值，即用户的搜索关键词。
这里字典的键之所以叫 q 是因为表单中搜索框 input 的 name 属性的值是 q，
如果修改了 name 属性的值，那么这个键的名称也要相应修改。
这里的过滤条件是 title__icontains=q，即 title 中包含（contains）关键字 q，前缀 i 表示不区分大小写。
这里 icontains 是查询表达式（Field lookups），在之前也使用过其他类似的查询表达式，其用法是在模型需要筛选的属性后面跟上两个下划线。
'''

class fullwidthView(IndexView):
	template_name = 'blogapp/full-width.html'
