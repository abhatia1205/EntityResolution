from django.contrib import admin
from .models import Article
from .models import EntityResolution
from .models import EntityType
from .models import Entity

admin.site.register(Article)
admin.site.register(EntityResolution)
admin.site.register(EntityType)
admin.site.register(Entity)
# Register your models here.
