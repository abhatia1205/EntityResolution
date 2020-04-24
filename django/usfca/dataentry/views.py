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
from nltk.tokenize import sent_tokenize

class Token:
    def __init__(self, text, paragraph_id, sequence_id, is_entity):
        self.text = text
        self.paragraph_id = paragraph_id
        self.sequence_id = sequence_id
        self.is_entity = is_entity
        self.has_break = False

    def SplitForResolution(self, resolution):
        print('Splitting sentence ', self)
        update = []
        if resolution.paragraph != self.paragraph_id or resolution.sentence != self.sequence_id or self.is_entity:
            print('Skipping sentence ', self)
            return [self]
        regex = '(' + resolution.name + ')'
        split_tokens = re.split(regex, self.text)
        nr = re.split(resolution.name, self.text)
        print('Non entities', nr)
        mydict = {}
        for t in nr:
            mydict[t] = 1
        print('Split tokens: ', split_tokens)
        for st in split_tokens:
            print('tok: ', st)
            is_entity = self.is_entity
            if st not in mydict:
                is_entity = True
            update.append(Token(st, self.paragraph_id, self.sequence_id, is_entity))
        print('Returning tokens: ', update)
        return update

    def __str__(self):
        mystr = '{%s (P: %d S: %d E: %d)}' % (self.text, self.paragraph_id, self.sequence_id, self.is_entity)
        return mystr

    def __repr__(self):
        return self.__str__()


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

def process_para(content, resolutions):
    sentences= []
    for para, c in enumerate(content):
        tokens = sent_tokenize(c)
        for index, sentence in enumerate(tokens):
            sentences.append([Token(sentence, para+1, index+1, False)])
    print('At start sentences are:', sentences)
    for resolution in resolutions:
        print('Processing ', resolution.name, 'para ', resolution.paragraph, ' sen', resolution.sentence)
        print('Tokens are: ', sentences)
        for index, sentence in enumerate(sentences):
            print('Processing tokens of ', sentence, ' with ', resolution.name, resolution.paragraph, resolution.sentence)
            update = []
            for tix, token in enumerate(sentence):
                update.extend(token.SplitForResolution(resolution))
            sentences[index] = update
            print('Tokens are: ', sentences)
    return sentences

@login_required(login_url='/accounts/login')
def next(request):
    processed = UserArticles.objects.values_list('article_id', flat=True)
    next_article = Article.objects.exclude(article_id__in=processed)[0]
    resolutions = EntityResolution.objects.filter(article=next_article.id)
    types = EntityType.objects.all()
    print("Types found are: ", types)
    content = codecs.decode(next_article.content, 'unicode_escape')
    final_content = []
    content = content.split("\n")
    sentences = process_para(content, resolutions)
    last_para = 1
    for s in sentences:
        if s[0].paragraph_id != last_para:
            s[0].has_break = True
            last_para = s[0].paragraph_id
    final_content = [x for s in sentences for x in s]
    html_resolutions = []
    for r in resolutions:
        resolution = HtmlResolution(r.name, r.paragraph, content[r.paragraph - 1], r.sentence, r.id, r.resolution_id)
        html_resolutions.append(resolution)
    return render(request, 'dataentry/next.html',
                  {'user': request.user,
                   'article': next_article,
                   'resolutions': html_resolutions,
                   'types': types,
                   'content': final_content})

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
# Can use redirect('dataentry/next')

# Create your views here.