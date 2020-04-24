import codecs
import re

from dataentry.models import Article
from dataentry.models import UserArticles
from dataentry.models import Entity
from dataentry.models import EntityResolution
from dataentry.models import EntityType
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class HtmlResolution:
    """Resolution data to be rendered on the html page."""
    def __init__(self, name, paragraph, content, sentence, rid, resolution_index):
        self.name = name
        self.paragraph = paragraph
        self.content = content
        self.sentence = sentence
        self.rid = rid
        self.resolution_index = resolution_index

def index(request):
    next_article = Article.objects.all()[0]
    resolutions = EntityResolution.objects.filter(article=next_article.id)
    outarr = [next_article.content, str(next_article.id)]
    outarr.extend([f'{x.resolution_id}:{x.id}' for x in resolutions])
    text = '<br>'.join(outarr)
    return HttpResponse(text)

def detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    resolutions = EntityResolution.objects.filter(article=article.id)
    return render(request, 'dataentry/detail.html', {'article': article, 'resolutions': resolutions})

@login_required(login_url='/accounts/login')
def next(request):
    processed = UserArticles.objects.values_list('article_id', flat=True)
    next_article = Article.objects.exclude(article_id__in=processed)[0]
    resolutions = EntityResolution.objects.filter(article=next_article.id)
    types = EntityType.objects.all()
    print("Types found are: ", types)
    content = codecs.decode(next_article.content, 'unicode_escape')
    content = content.split("\n")
    html_resolutions = []
    for r in resolutions:
        resolution = HtmlResolution(r.name, r.paragraph, content[r.paragraph - 1], r.sentence, r.id, r.resolution_id)
        html_resolutions.append(resolution)
    return render(request, 'dataentry/next.html',
                  {'user': request.user,
                   'article': next_article,
                   'resolutions': html_resolutions,
                   'types': types,
                   'content': content})

def getEntity(entity_map, name, type_id):
    log = []
    if (name, type_id) in entity_map:
        return entity_map[(name, type_id)]
    log.append(f'Processed entity map with name {name} and type {type_id}')
    # manager = Entity.mymanager
    # manager.myfilter(name, type_id)
    log.append(f'Got entity manager with name {name} and type {type_id}')
    all_entities = Entity.objects.all().filter(name=name, type_id=type_id)
    log.append('Manager.all executed')
    if all_entities and len(all_entities) > 0:
        log.append(f'Got all entities: {len(all_entities)}')
        entity = all_entities[0]
    else:
        log.append(f'Got no entity')
        entity = None
    if entity is not None:
        entity_map[(name, type_id)] = entity
    return entity

@login_required(login_url='/accounts/login')
@transaction.atomic
def update(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    user = request.user
    validation = UserArticles.objects.create(article=article, user=user)
    validation.save()
    rmap = request.POST
    resolutions = {}
    entities = {}
    log = ['<br>',]
    for key, value in rmap.items():
        if key.startswith('type'):
            _, resolution_id, rindex = key.split(':')
            type_id = int(value)
            x = (resolution_id, rindex)
            if x not in resolutions:
                resolutions[x] = {}
            resolutions[x]['type'] = type_id
            log.append(f'Got type of {type_id} for {resolution_id}, {rindex}')
        elif key.startswith('text'):
            _, resolution_id, rindex = key.split(':')
            x = (resolution_id, rindex)
            if x not in resolutions:
                resolutions[x] = {}
            resolutions[x]['name'] = value
            log.append(f'Got name as {value} for {resolution_id}, {rindex}')
    entity_map = {}
    log.append('Processing resolutions items')
    for key, value in resolutions.items():
        log.append(f'Processing resolution with key {key}')
        name = value['name']
        type_id = value['type']
        resolution_id = key[0]
        log.append(f'Processing with name {name} type {type_id} resolution {resolution_id}')
        entity = getEntity(entity_map, name, type_id)
        if entity is not None:
            log.append('Got entity with {name} and type {type_id}')
        else:
            log.append('Got null entity with {name} and type {type_id}')
        resolution = get_object_or_404(EntityResolution, pk=resolution_id)
        if entity is not None:
            resolution.entity = entity
            log.append(f'Got entity for {entity.id}')
        else:
            entity_type = EntityType.objects.all().filter(id=type_id)[0]
            entity = Entity.objects.create(type=entity_type, name=name)
            log.append(f'Created new entity with id {entity.id}')
            entity.save()
            resolution.entity = entity
        resolution.save()
    log.append(f'Successfully updated resolutions for {article_id}')
    return HttpResponse('<br>'.join(log))

# Create your views here.
