import codecs
import re
import heapq
import nltk
from itertools import chain

from dataentry.models import Article
from dataentry.models import UserArticles
from dataentry.models import Entity
from dataentry.models import EntityResolution, TemporaryResolution
from dataentry.models import EntityType
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

color_code = {"person": "background-color:#FFFF00A0", "location": "background-color:#008000A0", "organization": "background-color:#008080A0", "Other": "background-color:#FFA500"}


"""class TempResolution:
    def __init__(self, name, entity_id):
        self.name = name
        self.entity_id = entity_id """

class Token:
    def __init__(self, text, paragraph_id, sequence_id, is_entity, color = None):
        self.text = text
        self.paragraph_id = paragraph_id
        self.sequence_id = sequence_id
        self.is_entity = is_entity
        self.color = color
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
            color = False
            if st not in mydict:
                is_entity = True
                try:
                    color = color_code[resolution.original_type.lower()]
                except:
                    color = color_code["Other"]
            update.append(Token(st, self.paragraph_id, self.sequence_id, is_entity, color = color))
        print('Returning tokens: ', update)
        return update

    def __str__(self):
        mystr = '{%s (P: %d S: %d E: %d)}' % (self.text, self.paragraph_id, self.sequence_id, self.is_entity)
        return mystr

    def __repr__(self):
        return self.__str__()


class HtmlResolution:
    """Resolution data to be rendered on the html page."""
    def __init__(self, name, paragraph, content, sentence, rid, resolution_index, article_id, entity_id):
        self.name = name
        self.paragraph = paragraph
        self.content = content
        self.sentence = sentence
        self.rid = rid
        self.resolution_index = resolution_index
        self.article_id = article_id
        self.entity_id = entity_id

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
        tokens = nltk.sent_tokenize(c)
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
    temp_resolutions = []
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
        resolution = HtmlResolution(r.name, r.paragraph, content[r.paragraph - 1], r.sentence, r.id, r.resolution_id, next_article.id, r.entity_id)
        html_resolutions.append(resolution)
    return render(request, 'dataentry/next.html',
                  {'user': request.user,
                   'article': next_article,
                   'resolutions': html_resolutions,
                   'types': types,
                   'content': final_content})

def getEntity(entity_map, entity_id):
    log = []
    if entity_id in entity_map:
        return entity_map[entity_id]
    log.append(f'Processed entity map with id {entity_id}')
    # manager = Entity.mymanager
    # manager.myfilter(name, type_id)
    log.append(f'Got entity manager with id {entity_id}')
    all_entities = Entity.objects.all().filter(entity_id = entity_id)
    log.append('Manager.all executed')
    if all_entities and len(all_entities) > 0:
        log.append(f'Got all entities: {len(all_entities)}')
        entity = all_entities[0]
    else:
        log.append(f'Got no entity')
        entity = None
    if entity is not None:
        entity_map[entity_id] = entity
    return entity

@login_required(login_url='/accounts/login')
@transaction.atomic
def update(request, article_id):
    TemporaryResolution.objects.all().delete()
    article = get_object_or_404(Article, pk=article_id)
    user = request.user
    validation = UserArticles.objects.create(article=article, user=user)
    validation.save()
    rmap = request.POST
    print("----------------------------------------------------------------------------------------------------------------------------------------------")
    print("RMAP is: ", rmap)
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
        elif key.startswith('id'):
            _, resolution_id, rindex = key.split(':')
            x = (resolution_id, rindex)
            if x not in resolutions:
                resolutions[x] = {}
            resolutions[x]['entity_id'] = value
            log.append(f'Got id as {value} for {resolution_id}, {rindex}')
    entity_map = {}
    log.append('Processing resolutions items')
    for key, value in resolutions.items():
        log.append(f'Processing resolution with key {key}')
        entity_id = int(value['entity_id'])
        type_id = value['type']
        resolution_id = key[0]
        log.append(f'Processing {entity_id} type {type_id} resolution {resolution_id}')
        entity = getEntity(entity_map, entity_id)
        if entity is not None:
            log.append('Got entity {}'.format(entity_id))
        else:
            log.append('Got null entity with id {}'.format(entity_id))
        resolution = get_object_or_404(EntityResolution, pk=resolution_id)
        if entity is not None:
            resolution.entity = entity
            log.append(f'Got entity for {entity.entity_id}')
        else:
            entity_type = EntityType.objects.all().filter(id=type_id)[0]
            entity = Entity.objects.create(type=entity_type, entity_id = entity_id)
            log.append(f'Created new entity with id {entity.entity_id}')
            entity.save()
            resolution.entity = entity
        resolution.save()
    log.append(f'Successfully updated resolutions for {article_id}')
    return HttpResponse('<br>'.join(log))


@login_required(login_url='/accounts/login')
@transaction.atomic
def findentity(request):
    print("HELLO")
    resolutions = list(chain(EntityResolution.objects.exclude(entity_id__isnull=True), TemporaryResolution.objects.exclude(entity_id__isnull=True)))
    user = request.user
    rmap = request.POST
    print("RMAP:", rmap)
    if rmap:
        log = ['<br>',]
        search_str = 'myvalue'
        for key, value in rmap.items():
            if key == 'search':
                search_str = value
                break
        rs = []
        best_matches = heapq.nsmallest(20, resolutions,
                                       key=lambda r: nltk.edit_distance(search_str, r.name))
        html_resolutions = []
        articleids = []
        for r in best_matches:
            if(not isinstance(r, TemporaryResolution)):
                articleids.append(r.article_id)        
        articles = Article.objects.filter(pk__in=articleids)
        article_dict = {}
        for a in articles:
            content = codecs.decode(a.content, 'unicode_escape').split("\n")
            article_dict[a.id] = (a, content)

        for r in best_matches:
            if(not isinstance(r, TemporaryResolution)):
                if r.article_id in article_dict:
                    content = article_dict[r.article_id][1]
                resolution = HtmlResolution(r.name, r.paragraph, content[r.paragraph-1], r.sentence, r.id, r.resolution_id, r.article_id, r.entity.entity_id)
                html_resolutions.append(resolution)
            else:
                resolution = HtmlResolution(r.name, 0, "NAN", 0, 0, 0, 0, r.entity_id)
                html_resolutions.append(resolution)
        search_bool = True
    else:
        search_str = ""
        html_resolutions = []
        search_bool = False

    return render(request, 'dataentry/findentity.html',
                  {'searchstr': search_str,
                   'resolutions': html_resolutions,
                   'search_bool': search_bool,
                   'new_entity_id': getNextId()})

# Can use redirect('dataentry/next')
@login_required(login_url='/accounts/login')
@transaction.atomic
def createresolution(request):
    rmap = request.POST
    x = getNextId()
    TemporaryResolution.objects.create(name = rmap["createres"], entity_id = x)
    return HttpResponse('Created new resolution {}. Enter the id {} into the form'.format(request.POST["createres"], x))

def getNextId():
    try:
        print(list(TemporaryResolution.objects.all()))
        return max(Entity.objects.all().order_by("-entity_id")[0].entity_id, TemporaryResolution.objects.all().order_by("-entity_id")[0].entity_id) + 1
    except:
        print("EXCEPTION OCCURED WITH GETTING NEXT ID")
        return Entity.objects.all().order_by("-entity_id")[0].entity_id + 1

# Create your views here.