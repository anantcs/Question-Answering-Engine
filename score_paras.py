import operator

def add_to_index(index,keyword):
     if keyword in index:
         index[keyword] += 1
     else:
         index[keyword] = 1
         

def cal_score(dict):
    score = 0
    list = dict.values()
    for l in list :
        score+=l
    return score

def read_file(query):
    score = []
    para = open('c:/Python27/BTP/para.txt').read().split('\n\n')
    for p in para:
        p = p.lower()
        dict = {}
        word = p.split()
        for w in word:
            for q in query:
                if w == q:
                    add_to_index(dict, q)
                    break
        score.append(cal_score(dict))
    paraid = []
    for i in range(0,len(para)) :
        paraid.append(i)
    keys = paraid
    values = score
    d = {keys[n]:values[n] for n in range(0,len(keys)) }
    return d

def sort_paras(score) :
    sorted_score = sorted(score.iteritems(),key=operator.itemgetter(1),reverse=True)
    return sorted_score

def write_imp_para(newscore) :
    imp_info = []
    for i in range(0,4) :
        imp_info.append(newscore[i][0])
    para = open('c:/Python27/BTP/para.txt').read().split('\n\n')
    for i in range(0,4) :
        outfile = open('C:\Python27\BTP\imp_info.txt','a')
        outfile.write(para[imp_info[i]])
    outfile.close()

def score_paras(query) :
     score = read_file(query)
     newscore = sort_paras(score)
     write_imp_para(newscore)


