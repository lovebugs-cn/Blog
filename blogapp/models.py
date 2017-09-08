from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import markdown
from django.utils.html import strip_tags
# Create your models here.
class Category(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name

class Tag(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name

class Post(models.Model):
	# 文章标题
	title = models.CharField(max_length=70)

	# 文章正文
	body = models.TextField()

	# 创建时间和最后修改时间
	created_time = models.DateTimeField()
	modified_time = models.DateTimeField()

	# 文章摘要，可以没有文章摘要，但默认情况下 CharField 要求我们必须存入数据，否则就会报错。
	# 指定 CharField 的 blank=True 参数值后就可以允许空值了。
	excerpt = models.CharField(max_length=200,blank=True)

	# 下面把把文章对应的数据库表和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同。
	# 一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以使用的是 ForeignKey，即一对多的关联关系。
	# 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以使用 ManyToManyField，表明这是多对多的关联关系。
	# 同时一篇文章可以没有标签，因此为标签 tags 指定了 blank=True。
	category = models.ForeignKey(Category)
	tags = models.ManyToManyField(Tag, blank=True)

	# 文章作者，这里 User 是从 django.contrib.auth.models 导入的。
	# django.contrib.auth 是 Django 内置的应用，专门用于处理网站用户的注册、登录等流程，User 是 Django 为我们已经写好的用户模型。
	# 这里通过 ForeignKey 把文章和 User 关联了起来。
	# 因为一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和 Category 类似。
	author = models.ForeignKey(User)

	# 记录阅读量
	views = models.PositiveIntegerField(default=0)

	def increase_views(self):
		self.views += 1
		self.save(update_fields=['views']) # 只更新数据库中 views 字段的值，以提高效率。

	def __str__(self):
		return self.title

	# 为了方便地生成文章详情页的URL,自定义 get_absolute_url 方法
	# 记得从 django.urls 中导入 reverse 函数
	def get_absolute_url(self):
		return reverse('blogapp:detail',kwargs={'pk':self.pk})

	# 在 Post 类的内部定义一个 Meta 类，并指定排序属性
	# ordering 属性用来指定文章排序方式，['-created_time'] 指定了依据哪个属性的值进行排序，这里指定为按照文章发布时间排序，且负号表示逆序排列
	class Meta:
		ordering = ['-created_time']

	'''
	注意到 URL 配置中的 url(r'^post/(?P<pk>[0-9]+)/$', views.detail, name='detail') ，
	前面设定的 name='detail' 在这里派上了用场。看到这个 reverse 函数，它的第一个参数的值是 'blogapp:detail'，
	意思是 blogapp 应用下的 name=detail 的函数，
	由于在上面通过 app_name = 'blog' 告诉了 Django 这个 URL 模块是属于 blog 应用的，
	因此 Django 能够顺利地找到 blog 应用下 name 为 detail 的视图函数，
	于是 reverse 函数会去解析这个视图函数对应的 URL，
	这里 detail 对应的规则就是 post/(?P<pk>[0-9]+)/ 这个正则表达式，
	而正则表达式部分会被后面传入的参数 pk 替换，
	所以，如果 Post 的 id（或者 pk，这里 pk 和 id 是等价的） 是 255 的话，
	那么 get_absolute_url 函数返回的就是 /post/255/ ，这样 Post 自己就生成了自己的 URL。
	'''
	# 实现自动获取摘要
	def save(self,*args,**kwargs):
		# 如果没有填写摘要
		if not self.excerpt:
			# 首先实例化一个markdown类，用于渲染body文本
			md = markdown.Markdown(extensions=[
					'markdown.extensions.extra',
					'markdown.extensions.codehilite',
				])
			# 先将Markdown文本渲染成HTML文本
			# strip_tags去掉HTML文本的全部HTML标签
			# 从文本摘取前54个字符赋给excerpt
			self.excerpt = strip_tags(md.convert(self.body))[:54]

			# 调用父类的save方法将数据保存到数据库中
			super(Post,self).save(*args,**kwargs)