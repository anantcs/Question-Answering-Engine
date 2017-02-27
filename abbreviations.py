import re

text = open('abbrtemp.txt','r').read().split('\n')

def ret_full_form(abbr) :
    abbr = abbr.upper()
    for f in text :
        if f.find(abbr) != -1 :
            return f[f.find('\x97')+1:]

def find_word(question) :
    q = re.sub(r' ','',question)
    if q.find('of') != -1 :
        return q[q.find('of')+2:q.find('?')]
    if q.find('does') != -1 :
        return q2[q2.find('does')+5:q2.find('stand')-1]

def answer_abbreviations(question) :
    abbr = find_word(question)
    print 'Abbreviation', abbr
    return ret_full_form(abbr)
