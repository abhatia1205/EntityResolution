from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UnprocessedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(validated=False)


class EntityManager(models.Manager):
    def myfilter(self, name, type_id):
        self.name = name
        self.type_id = type_id

    def get_queryset(self):
        return super().get_queryset().filter(name=self.name, type_id=self.type_id)


class Article(models.Model):
    content = models.TextField()
    article_id = models.IntegerField(default=0)
    title = models.TextField(default="")
    subtitle = models.TextField(default="")
    publish_date = models.DateField(default="2000-01-01")
    article_url = models.TextField(default="")
    article_type = models.TextField(default="news_article")
    media_id = models.IntegerField(default=0)


class EntityType(models.Model):
    type = models.CharField(max_length=100)


class Entity(models.Model):
    type = models.ForeignKey(EntityType, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    # mymanager = EntityManager()
        

class EntityResolution(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    name = models.TextField()
    original_type = models.TextField(default='')
    resolution_id = models.IntegerField(default=0)
    paragraph = models.IntegerField(default=0)
    sentence = models.IntegerField(default=0)
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

class UserArticles(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

