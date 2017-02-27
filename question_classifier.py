import re
import nltk
import random
import pickle

def question_features(post) :
	features = {}
	for word in nltk.word_tokenize(post) :
		features['contains(%s)' % word.lower()] = True
	return features

def question_features2(post) :
        return {'first_word': post.split(' ')[0],'second_word': post.split(' ')[1],'third_word': post.split(' ')[2]}

def get_class(post,d) :
	return d.get(post)

def read_qs_from_file() :
        words = open("training_set5.txt").read().split("\n")
        new_list = []
        for word in words :
                if word.find("ABBR") != 0 :
                        new_list.append(word)
        words = new_list
        return words

def extract_wordtags(words):
        wordtags = []
        for word in words :
                wordtags.append(word.split(' ')[0])
        return wordtags

def remove_subclasses(wordtags) :
        for i in range(0,len(wordtags)) :
                wordtags[i] = re.sub('[a-z:]+','',wordtags[i])
        return wordtags

def remove_tags(words) :
        for i in range (0,len(words)):
                words[i] = ' '.join(map(str,words[i].split(' ')[1:]))
        return words

def make_dictionary(words, wordtags) :
        keys = words
        values = wordtags
        d = {keys[n]:values[n] for n in range(len(keys)) }
        return d

def prepare_pickle_file(classifier):
        f = open('my_classifier.pickle','wb')
        pickle.dump(classifier, f)
        f.close()

def prepare_words_and_wordtags():
        words = read_qs_from_file()
        wordtags = extract_wordtags(words)
        wordtags = remove_subclasses(wordtags)
        words = remove_tags(words)
        d = make_dictionary(words, wordtags)
        return d, words

def train_classifier(d, words) :
        featuresets = [(question_features(word),get_class(word,d)) for word in words]
        size = int(len(featuresets)*0.2)
        train_set, test_set = featuresets[size:],featuresets[:size]
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        print 'Accuracy is:\t',nltk.classify.accuracy(classifier,test_set)
        return classifier

#Changes the question type told by the NaiveBayes QC to the answer type which
#will be found by the NER
def find_answer_type2(question_type, question) :
    if question_type == "DESC" :
        return "DESC"
    if question_type == "ENTY" :
        return "ENTY"
    if question_type == "HUM" :
        return "PERSON"
    if question_type == "ABBR" :
        return "ABBR"
    if question_type == "LOC" :
        return "LOCATION"
    if question_type == "NUM" :
        if question.find("when") != -1 :
            return "DATE"
        else :
            return "NUM"

def find_answer_type(question):
        abbs = ['full form','stands for','stand for','acronym']
        for abb in abbs :
                if question.find(abb) != -1 :
                        return "ABBR"
        first_word = question.split()[0].lower()
        if first_word == "who" :
                return "PERSON"
        if first_word == "where" :
                return "LOCATION"
        if first_word == "when" :
                return "DATE"

def ret_answer_type2(question) :
        #Making dictionary out of word and wordtags
        d, words = prepare_words_and_wordtags()
        #Training classifier
        classifier = train_classifier(d, words)
        question_type = classifier.classify(question_features(question))
        answer_type = find_answer_type2(question_type, question)
        return answer_type

def ret_answer_type(question) :
        answer_type = find_answer_type(question)
        return answer_type




#Preparing pickle file so that classifier can be opened from another file
#prepare_pickle_file(classifier)
#question = raw_input()
#print classifier.classify(question_features(question))
