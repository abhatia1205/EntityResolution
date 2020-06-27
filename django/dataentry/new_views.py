"""Comment"""

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

"""The class Token holds information on how to split by resolution. A token is just a piece of text that can either be a resolution
or not. It also"""
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

""" Input: A list of paragraphs that make up an article. Resolutions is a list of the resolutions found in thay article
Returned is the"""
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