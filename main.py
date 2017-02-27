import nltk
import pickle
import time
import question_classifier
from question_classifier import ret_answer_type
import IR
from IR import get_all_links
import formulate_query
from formulate_query import ret_query
import score_paras
from score_paras import score_paras
import score_sentences
from score_sentences import score_sentences
import answer_processing
from answer_processing import answer_processing

#for question in where_questions :
#start = time.time()
    #TAKING INPUT
    #print question
question = raw_input()
question = question.lower()

    #MODULE 1 - QUESTION CLASSIFIER
answer_type = ret_answer_type(question)
    #print 'Answer type :\t', answer_type

    #MODULE 2 - INFORMATION RETRIEVAL
if answer_type != "ABBR" :
        #print 'Fetching information from web'
    get_all_links(question)

    #MODULE 3 - FORMULATE QUERY WORDS
if answer_type != "ABBR" :
        #print 'Formulating query'
    query = ret_query(question)
        #print query

    #MODULE 4 - SCORING PARAS AND SENTENCES
if answer_type != "ABBR" :
        #print 'Scoring paras'
    score_paras(query)
        #print 'Scoring sentences'
    final, imp_sentences, maxi, var = score_sentences(query, answer_type)

    #MODULE 5 - ANSWER PROCESSING
    #print 'Scoring answers'
if maxi != 0 and var !=1:
    answer = answer_processing(answer_type, question, final, imp_sentences)
    #print 'Answer is:\t', answer
    print answer
else:
    sentences = open('C:\Python27\BTP\imp_info.txt').read()
    print 'relevant information is : \n', sentences

#end = time.time()
#print 'The time taken by the code is', end - start


    #MODULE 6 - STORE QUESTIONS AND ANSWERS
    #records = open('C:/Python27/BTP/records.txt','a')
    #records.write('Question:\t'+str(question)+"Answer:\t"+str(answer)+'\n'+"Time:\t"+str(end-start)+'\n\n')
    #records.close()


    #DELETING THE TEMPORARY FILES
import os
directory = 'C:\Python27\BTP'
os.chdir(directory)
os.unlink('para.txt')
os.unlink('imp_info.txt')
os.unlink('imp_sentences.txt')


