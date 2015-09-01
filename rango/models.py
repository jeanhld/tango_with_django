from django.db import models
from django.utils.text import *
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

class Category(models.Model):
	name = models.CharField(max_length=128, unique=True)
	view = models.IntegerField(default=0)
	likes = models.IntegerField(default=0)
	slug = models.SlugField(unique=True)

	def save(self, *args, **kwargs):
		if self.view < 0:
			self.view = 0
		self.slug = slugify(self.name)
		super(Category, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.name

class Page(models.Model):
	category = models.ForeignKey(Category)
	title = models.CharField(max_length=128)
	url = models.URLField()
	views = models.IntegerField(default=0)

	def __unicode__(self):
		return self.title

class UserProfile(models.Model):
	user = models.OneToOneField(User)

	website = models.URLField()
	picture = models.ImageField(blank=True)

	def __unicode__(self):
		return self.user.username