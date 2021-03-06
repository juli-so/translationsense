import train_word as train
import ref_definitions2 as ref
import json

with open('chinese_sents.json', 'rb') as fp:
      chinese_sents = json.load(fp)
def get_c_words():
    with open('train_data.json', 'rb') as fp:
        train_dict = json.load(fp)
        train_dict = dict([(k.encode('utf-8'),v) for k,v in train_dict.items()])
    return train_dict
def get_test_words():
    with open('train_data.json', 'rb') as fp:
        train_dict = json.load(fp)
        train_dict = dict([(k.encode('utf-8'),v) for k,v in train_dict.items()])
    with open('test_ref_dict.json', 'rb') as fp:
        ref_dict = json.load(fp)
        ref_dict = dict([(k.encode('utf-8'),v) for k,v in ref_dict.items()])

    words_train = train_dict.keys()
    words_ref = ref_dict.keys()
    can_eval_words = list(set(words_train) & set(words_ref))
    
    test_words = {}
    for word in can_eval_words:
        info = ref_dict[word]
        test_words[word] = [] 
        for data in info:
            test_words[word].append(data[0])
    return test_words 
def build_sentence_vector(sentences):
       word_set = set()
       word_list = []
       for s in sentences:
              words = s.split(' ')
              for word in words:
                     if word not in word_set and word != '':
                            word_set.add(word)
                            word_list.append(word)
       return word_list
def build_observation_vector(words_vec,sentence):
       vector = []
       for word in words_vec:
              if word in sentence:
                     vector.append(1)
              else:
                     vector.append(0)
       return vector
def classify_test_words(n,ign):
    count_all_zero_features = 0
    count_features = 0

    classifiers = train.get_classifiers(n)
    test_words = get_test_words()
    classified_words = {}

    most_common = most_common_classifier()

    for word in classifiers.keys():
        #print "WORD", word
        sentences = []
        for sent_i in test_words[word]:
            sentences.append(chinese_sents[sent_i])
        sent_vec = build_sentence_vector(sentences)

        for sent_i in test_words[word]:
            classifier = classifiers[word][0]
            feature_vec = classifiers[word][1]
            test_feature_vec = build_observation_vector(feature_vec,sent_vec)
            # print "feature_vec", feature_vec
            # print "sent_vec", sent_vec
            count_features += 1

            count_zero = test_feature_vec.count(0)
            if(count_zero >= (len(test_feature_vec)-ign)):
                pred = most_common[word]
                count_all_zero_features += 1
            else:
                pred = classifier.pred(test_feature_vec)
                
            if(word in classified_words):
                classified_words[word].append([sent_i,pred])
            else:
                classified_words[word] = [[sent_i,pred]]
    #print "classified words", classified_words
    return classified_words,count_all_zero_features,count_features
def most_common_classifier():
    with open('train_data.json', 'rb') as fp:
        train_dict = json.load(fp)
        train_dict = dict([(k.encode('utf-8'),v) for k,v in train_dict.items()])
    #classifiable_words = train_dict.keys()
    most_common_classifier = {}
    for word in train_dict:
        classes = {}
        classifications = train_dict[word]
        for c in classifications:
            if c[1] in classes:
                classes[c[1]] += 1
            else:
                classes[c[1]] = 1
        most_common = max(classes, key=classes.get)
        most_common_classifier[word] = most_common
    return most_common_classifier

def evaluate_most_common(n,ign):
    #ref_dict is build_chinese_word_sent_dict(3500,5000,{})
    with open('test_ref_dict.json', 'rb') as fp:
        ref_dict = json.load(fp)
        ref_dict = dict([(k.encode('utf-8'),v) for k,v in ref_dict.items()])
    correct_pred_count = 0
    pred_count = 0
    results = classify_test_words(n,ign)
    classified_words = results[0]
    print 'started training most_common_classifier'
    most_common = most_common_classifier()
    print 'most_common_classifier has been trained'
    for word in classified_words:
        for test_pred in classified_words[word]:
            sent_i = test_pred[0]
            prediction = most_common[word]
            if (word in ref_dict):
                ref_meanings = ref_dict[word]
                for meaning in ref_meanings:
                    if meaning[0] == sent_i:
                        if meaning[1] == prediction:
                            correct_pred_count += 1
                        pred_count += 1
    print "total # of correct predictions: %s" % correct_pred_count
    print "total # of prediction attempts: %s" % pred_count
    return correct_pred_count,pred_count
def evaluate_presense_feature(n,ign):
    #ref_dict is build_chinese_word_sent_dict(3500,5000,{})
    with open('test_ref_dict.json', 'rb') as fp:
        ref_dict = json.load(fp)
        ref_dict = dict([(k.encode('utf-8'),v) for k,v in ref_dict.items()])
    correct_pred_count = 0
    pred_count = 0
    results = classify_test_words(n,ign)
    classified_words = results[0]
    
    for word in classified_words:
        for test_pred in classified_words[word]:
            sent_i = test_pred[0]
            prediction = test_pred[1]
            if (word in ref_dict):
                ref_meanings = ref_dict[word]
                for meaning in ref_meanings:
                    if meaning[0] == sent_i:
                        if meaning[1] == prediction:
                            correct_pred_count += 1
                        pred_count += 1
    print "total # of all 0 observation vecs: %s" % results[1]
    print "total # of observation vecs: %s" % results[2]
    print "total # of correct predictions: %s" % correct_pred_count
    print "total # of prediction attempts: %s" % pred_count
    return correct_pred_count,pred_count
def run_test():
    n_list = [0.3,0.5,0.8,1.0]
    for n in n_list:
        print "N:",n
        #print "Ign:", i
        #print "common:"
        #print evaluate_most_common(n,0)
        #print "presense:"
        print evaluate_presense_feature(n,0)
