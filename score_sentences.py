import operator
import answer_processing
from answer_processing import NER_string

def add_to_index(index,keyword):
     if keyword in index:
         index[keyword] += 1
     else:
         index[keyword] = 1
         

def cal_score(diction):
    score = 0
    lis = diction.values()
    for l in lis :
        score += 1
    return score

def extract_text(nertext):
	s1 = nertext.find('</FORM>')
	s2 = nertext.find('</div>',s1+1)
	s3 = nertext.find('</div>',s2+1)
	s4 = nertext.find('</div>',s3+1)
	s5 = nertext.find('\n',s4)
	s6 = nertext.find('<div id',s5+1)
	return nertext[s5+1:s6]

def read_file(query, answer_type) :
    var = 0
    #print 'answer type-------', answer_type
    score =[]
    nertext = NER_string(open('C:\Python27\BTP\imp_info.txt').read())
    
    final = extract_text(nertext)
    #print 'final-----', final
    final = final.split('.')
    #print 'final senetences-----', final
    l = [] # List for scoring bool values to include that sentence in imp_sentences file or not
    for f in final :
         if f.find(answer_type) != -1 :
              l.append(1)
         else :
              l.append(0)
    #print 'list-----', l
    k = 0 #For printing the sentence number
    j = 0 #For incrementing list pointer
    sentences = open('C:\Python27\BTP\imp_info.txt').read().split('.')
    for s in sentences :
        #print 'sentence------\n', s
        s = s.lower()
        if l[j] == 0 :
             score.append(0)
        else :
             k +=1
             word = s.split()
             diction = {}
             for w in word :
                 for q in query :
                     if w == q :
                         add_to_index(diction, q)
                         break
             score.append(cal_score(diction))
             #print 'diction-----', diction
        j += 1
    if k==1 :
         var = 1
    #print 'score-----------------\n', score
    sid = []
    for i in range(0,len(sentences)):
        sid.append(i)
    keys = sid
    values = score
    d = {keys[n]:values[n] for n in range(0,len(keys)) }
    return d, final, var

def sort_sentences(score) :
    sorted_score = sorted(score.iteritems(),key=operator.itemgetter(1),reverse=True)
    return sorted_score

def ret_maxscore_sentence(newscore) :
    maxi = newscore[0][1]
    for i in range(0,len(newscore)):
        if newscore[i][1] != maxi :
            break
    return i, maxi

def write_imp_sentences(newscore) :
    #imp_sentences contains the list(index number) of the sentences which have
    #the maximum score
    imp_sentences = []
    index, maxi = ret_maxscore_sentence(newscore)
    for i in range(0,index) :
        imp_sentences.append(newscore[i][0])
    #print imp_sentences
    sentences = open('C:\Python27\BTP\imp_info.txt').read().split('.')
    #for s in sentences :
        #print s
    for i in range(0,index) :
        outfile = open('C:\Python27\BTP\imp_sentences.txt','a')
        outfile.write(sentences[imp_sentences[i]]+'.')
    outfile.close()
    return imp_sentences, maxi

def score_sentences(query, answer_type) :
     score, final, var  = read_file(query, answer_type)
     newscore = sort_sentences(score)
     imp_sentences, maxi = write_imp_sentences(newscore)
     return final, imp_sentences, maxi, var
