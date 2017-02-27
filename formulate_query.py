import re
import nltk
import string
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

#nltk.download('wordnet')
#nltk.download('stopwords')

#syns = wn.synsets('country')
#syns

stopwords = stopwords.words('english')
len(stopwords)

#Stemming
def ret_stemmed_query(query) :
    stemmer = nltk.stem.porter.PorterStemmer()
    qstem = []
    for q in nltk.word_tokenize(query) :
        qstem.append(stemmer.stem_word(q))

def remove_stopwords(question) :
    query = []
    for q in nltk.word_tokenize(question):
        if q not in stopwords :
            query.append(q)
    return query

table = string.maketrans('','')
def clean(question) :
    return question.translate(table,string.punctuation)

def ret_query(question):
    question = question.lower()
    question = clean(question)
    query = remove_stopwords(question)
    return query

