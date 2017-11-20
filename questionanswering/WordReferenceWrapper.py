import requests
from bs4 import BeautifulSoup
import re
from questionanswering.funaux import *

def get_synoms(word):
    
    url = "http://www.wordreference.com/sinonimos/{0}".format(word)
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    if soup.find(id="noEntryFound"):
        return []
    ul = soup.find(id="article").ul
    syms = []
    for li in ul.findAll('li'):
        if "Ant" in li.get_text():
            continue
        syms += li.get_text().split(',')
    syms = [ delete_tildes(x.strip()) for x in syms]
    return syms

def es_to_en(word):
    
    url = "http://www.wordreference.com/es/en/translation.asp?spen={0}".format(word)
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    if soup.find(id="noEntryFound"):
            return []

    lista = soup.find(id="articleWRD").table.findAll("td",class_="ToWrd")

    es_word = ""
    en_words = []
    for t in lista:
        tag_st = t.string
        if tag_st == "English":
            continue
        if not t.em == None:
            t.em.extract()
        if not t.a == None:
            t.a.extract()
        en_w = t.string.split(',')
        en_w = [ x.strip() for x in en_w]
        en_words += en_w

    return en_words

def en_to_es(word):
    
    url = "http://www.wordreference.com/es/translation.asp?tranword={0}".format(word)
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    if soup.find(id="noEntryFound"):
            return []

    lista = soup.find(id="articleWRD").table.findAll("td",class_="ToWrd")
    es_word = ""
    en_words = []
    for t in lista:
        tag_st = t.string
        if tag_st == "Español":
            continue
        if not t.em == None:
            t.em.extract()
        if not t.a == None:
            t.a.extract()
        if t.string == None:
            continue
        en_w = t.string.split(',')
        en_w = [ x.strip() for x in en_w]
        en_words += en_w

    return en_words