# -*- coding=UTF-8 -*-
from django import template
from ..models import Post, Category, Tag
from django.db.models.aggregates import Count
register = template.Library() # 实例化了一个 template.Library 类

# 最新文章模板标签，这个函数的功能是获取数据库中前 num 篇文章，这里 num 默认为 5。
# 将函数 get_recent_posts 装饰为 register.simple_tag。这样就可以在模板中使用语法 {% get_recent_posts %} 调用这个函数了
@register.simple_tag
def get_recent_posts(num=5):
	return Post.objects.all().order_by('-created_time')[:num]

# 归档模板标签
@register.simple_tag
def archives():
	return Post.objects.dates('created_time','month',order='DESC')
# 这里 dates 方法会返回一个列表，列表中的元素为每一篇文章（Post）的创建时间，且是 Python 的 date 对象，精确到月份，降序排列

# 分类模板标签
@register.simple_tag
def get_categories():
	return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

# 标签云
@register.simple_tag
def get_tags():
	return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)