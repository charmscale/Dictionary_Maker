import nltk
from nltk import word_tokenize
from nltk import sent_tokenize
import re
from urllib import request
from bs4 import BeautifulSoup
import pickle

def getWord(elem):
    return elem[0]

def syllable_counter(word):#counts syllables in word
    vowels=['a','e','i','o','u','y'];
    syllables=0
    pot_minus=''
    pot_dip=[]
    word=word.lower()
    vowel=False
    for i in range(len(word)):
        for j in vowels:
            if word[i] == j:
                syllables += 1
                pot_minus += word[i]
                vowel=True
            if len(pot_minus) == 2:
                pot_dip += [pot_minus]
                pot_minus=pot_minus[1]
        if not vowel:
            pot_minus=''
        vowel=False
    if len(word)>2:
        if word[-1] == 'e' and word[-2] != 'l':
            syllables-=1
    if len(word)>4:
        if word[-1]=='n' and word[-2]=='o' and word[-3]=='i' and word[-4]=='t':
            syllables-=1
        if word[-1]=='s' and word[-2]=='u'and word[-3]=='o' and word[-4]=='i':
            syllables-=1
    if word[0] == 'y':
        syllables-=1
    dip=['ae','ai','au','ay','ea','ee','ei','eu','ey','ie','iu','iy','oa','oe','oi','oo','ou','oy','ua','ui','uy']
    for i in pot_dip:
        for j in dip:
            if i==j:
                syllables-=1
    return syllables;

def analyze_text(pairs, pair_count, word_list, word_count, url):
    f=request.urlopen(url)
    raw = f.read().decode('latin-1', 'backslashreplace')  
    soup=BeautifulSoup(raw, features="lxml")
    paragraphs=soup.find_all('p')
    count=1
    for p in paragraphs:
        text=p.text
        sentences = sent_tokenize(text)
        previous_s=[]
        print(str(count) + '/' + str(len(paragraphs)))
        for s in sentences:
            if '"' in s: 
                continue
            s=re.sub(r'[\W\d]',' ', s.lower())#remove all numbers and punctuation
            words=word_tokenize(s)#break sentence into words
            words=nltk.pos_tag(words)#tag word with part of speech
            for i in range(len(words)):
                ps=[]
                if words[i][1][0]=='J' or words[i][1][0:1]=='NN' or words[i][1][0:2]=='NNS' or words[i][1][0:1]=='RB' or words[i][1][0]=='V':#if verb, noun, adjective, or adverb
                    #determine relatedness count of pairs
                    ps.append(words[i])
                    if words[i] not in word_list:
                        word_list.append(words[i])
                        word_count.append(0)
                    word_count[word_list.index(words[i])]+=1
                    for j in range(i+1,len(words)):
                        if words[j]!=words[i] and (words[j][1][0]=='J' or words[j][1][0]=='N' or words[j][1][0:1]=='RB'  or words[j][1][0]=='V'):
                            pair=[words[i], words[j]]         
                            pair.sort(key=getWord)
                            if pair in pairs:
                                pair_count[pairs.index(pair)]+=3
                            else:
                                pairs.append(pair)
                                pair_count.append(3)
                    for w in previous_s:
                        if w!=words[i]:
                            pair=[words[i], w]
                            pair.sort(key=getWord)
                            if pair in pairs:
                                pair_count[pairs.index(pair)]+=1
                            else:
                                pairs.append(pair)
                                pair_count.append(1)
                if words[i][1][0]=='D' or words[i][1][0:1]=='IN' or words[i][1][0:1]=='PR':
                    if words[i] not in word_list:
                        word_list.append(words[i])
                        word_count.append(0)
                    word_count[word_list.index(words[i])]+=1
                previous_s=ps
        count+=1

def pair_relationship(pairs, pair_count, word_list, word_count):
    for i in range(len(pairs)): #calculate relationship between how often words are seen and how often they're seen together
        denominator=0
        if word_count[word_list.index(pairs[i][0])]>word_count[word_list.index(pairs[i][1])]:
            denominator=word_count[word_list.index(pairs[i][1])]
        else:
            denominator=word_count[word_list.index(pairs[i][0])]
        pair_count[i]=pair_count[i]/denominator

def pair_gap(pair_count):
    pair_gap=pair_count
    pair_gap.sort()
    gap=0
    upper=0
    for i in range(len(pair_gap)-1):
        if (pair_gap[i+1]-pair_gap[i])>gap:
            gap=pair_gap[i+1]-pair_gap[i]
            upper=pair_gap[i+1]
    return upper

def build_dict(pairs, pair_count, word_list, word_count, upper, word_dict):
    largest=word_count#find the largest word count
    largest.sort()
    largest=largest[-1]
           
    for i in range(len(word_list)):
        related_list=[]
        for j in range(len(pairs)): 
            pair=pairs[j]
            if len(pair)>1 and word_list[i] in pair:
                if pair_count[j]>=upper:
                    print(pair)
                    pair.remove(word_list[i])
                    related_list.append(pair[0])
        word_dict[word_list[i]]=[word_count[i]/largest, syllable_counter(word_list[i][0]), related_list]

pairs=[]
pair_count=[]
word_list=[]
word_count=[]
'''for i in range(97,122):
    f=request.urlopen('https://www.gutenberg.org/browse/authors/'+ chr(i))
    raw = f.read().decode('utf8')
    soup=BeautifulSoup(raw, features="lxml")
    links=soup.find_all('a')
    count=1
    for l in links:
        print(chr(i) + ' '+ str(count) + "/" + str(len(links)))
        url=l.get('href')
        if url!=None and 'ebooks' in url:
            f=request.urlopen('https://www.gutenberg.org'+ url)
            raw = f.read().decode('utf8')
            soup=BeautifulSoup(raw, features="lxml")
            other_links=soup.find_all('a')
            for o in other_links:
                if o.text=='Read this book online: HTML':
                    analyze_text(pairs, pair_count, word_list, word_count, 'https://www.gutenberg.org' + o.get('href'))
        count+=1'''
analyze_text(pairs, pair_count, word_list, word_count, 'https://www.gutenberg.org/files/29666/29666-h/29666-h.htm')
pair_relationship(pairs, pair_count, word_list, word_count)
upper=pair_gap(pair_count)
word_dict={}
build_dict(pairs, pair_count, word_list, word_count, upper, word_dict)
f = open("word_dict.pkl","wb")
pickle.dump(word_dict,f)
f.close()

