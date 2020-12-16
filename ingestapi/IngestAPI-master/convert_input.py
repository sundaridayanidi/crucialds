import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""                                                                                                                                                                                               
In this script we convert the inclusion/exclusion criteria from natural language to 
queries that can be passed to construct_query.py which are then converted to mongo queries   
"""

import urllib2
from bs4 import BeautifulSoup
import codecs
import nltk
import os
from urllib import urlopen
import re
from subprocess import check_output
import subprocess
import pickle
import string
from pymongo import MongoClient
import datetime
import json



#does pos tagging and replaces the plurals in the string with their singular counterparts
def replacePlurals(input):
    orig = input
    input = input.lower()
    input = input.strip()
    text = nltk.word_tokenize(input)
    pos_stuff = nltk.pos_tag(text)

    for term in pos_stuff:
        word = term[0]
        pos = term[1]

        if pos == "NNS" or pos == "NNPS":
            if word[-3:-1] == "ies":
                new_word = word[:-3]
                new_word = new_word + "y"

                input = input.replace(word, new_word)


            elif word[-1] == "s":
                new_word = word[:-1]

                if word == "diabetes":
                    new_word = "diabetes"

                input = input.replace(word, new_word)

        if word[-3:] == "ing":
            #print word
            new_word = word[:-3]

            input = input.replace(word, new_word)


    return input


#replaces strings that are semantically similar (plurals, etc) with the preferred string                                                                                                
def CleanString(db, input, stopwords):
    cleaned_input = input
    input = input.strip()
    input = input.split()
    exclude = set(string.punctuation)

    for word in input:
        #he maps to helium                                                                                                                                                                    
        if word.lower() != "he":

            if word[-1] in exclude: #we get rid of punctuation at the end of the sentence from the word                                                                                         
                word = word[-1]

            res = db.lower_lragr.find({"TERM":word}, {"PT":"1"})
            pt = word

            for document in res:
                #print document                                                                                                                                                               
                pt = document['PT']

            cleaned_input = cleaned_input.replace(word, pt)

    return cleaned_input #return if cleaned version exists above. Otherwise return original word


#we see if the term can be matched to an ICD 10 code
def getICD10(term, stopwords, icd_dict):
    type = "ICD10"

    term = term.strip()
    term = term.lower()
    orig_term = term
    term_list = term.split()

    for w in term_list:
        if w in stopwords:
            term = term.replace(w, "")

    term_list = set(term.split())

    with open("icd_file") as f:
        for line in f:
            line = line.strip()
            orig_line = line
            line = line.split()
    
            code = line[0]
            code_term = orig_line.replace(code, "")
            orig_code_term = code_term.strip()
            code_term = code_term.lower()

            code_term_list = code_term.split()

            for w in code_term_list:
                if w in stopwords:
                    code_term = code_term.replace(w, "")

            code_term_list = set(code_term.split())

            if len(code_term_list.intersection(term_list)) > 0:
                icd = code + "-" + orig_code_term

                if orig_term in icd_dict:
                    res = icd_dict[orig_term]
                    res = res + "," + icd
                    icd_dict[orig_term] = res
                else:
                    icd_dict[orig_term] = icd


#we look up the type corresponding to the term by first looking up CUI in mrconso and then finding type in mrsty                                                                        
def getType(db, term, type_dict, stopwords):
    type = ""
    cui = ""

    term = term.strip()
    term = term.lower()

    #print term

    #exits if any numbers or stopwords in the term
    term_list = term.split()
    for w in term_list:
        if w.isdigit() == True or w in stopwords:
            return ""

    res = db.lower_mrconso.find({"TERM":term})
    for document in res:
        #print document                                                                                                                                                                         
        cui = document["CUI"]
        #print cui
        break

    res = db.lower_mrsty.find({"CUI":cui})
    for document in res:
        t = document["TYPE"]
        #print t
        type = type + "\t" + t

        if t in type_dict:
            res = type_dict[t]
            
            #dont want to cause repeats
            if term not in res:
                res = res + "," + term
            type_dict[t] = res
        else:
            type_dict[t] = term
    

    type = type[1:]
    #print "Type: ", type
    return type



#checks to see if the term is in MRCONSO
def checkType(db, term, stopwords, line):
    orig_term = term
    term = term.strip()
    term = term.lower()
    line = line.strip()
    line = line.lower()

    #exits if any numbers or stopwords is a word in the phrase 
    term_list = term.split()

    for w in term_list:
        #if w.isdigit() == True or w in stopwords:
        if w in stopwords:
            return False


    #We implement checking for negative phrases here (to prevent picking up on negative conditions
    if term in line and (("no evidence of " + term) in line or ("did not show evidence for " + term) in line or ("no " + term) in line or ("negative for " + term) in line or (term + " r/o") in line or ("low probability for " + term) in line or ("hard to interpret as a sign for " + term) in line or "? no" in line or "father" in line or "mother" in line or "family history" in line):
        return False

    #print term
    res = db.lower_mrconso.find({"TERM":term})
    if len(list(res)) == 0:
        return False
    else:
        return True



def convertInput(db, line, stopwords, type_dict, icd_dict):
    line = line.strip()
             
    #take out punctuation
    line = line.replace(".", "")
    line = line.replace("?", "")
    line = line.replace("!", "")
    line = line.replace(":", "")
    line = line.replace("," , " ")
    line = line.replace("-", " ")
    line = line.replace("(", "")
    line = line.replace(")", "")

    #replace synonyms
    line = line.replace("nodules", "nodule")
    line = line.replace("obese", "obesity")
    line = line.replace("cataract", "cataracts")
    line = line.replace("tablets", "tablet")
    line = line.replace("medications", "medication")
    line = line.replace("vitamins", "vitamin")
    line = line.replace("cataractss", "cataracts")


    line = replacePlurals(line)
    line = CleanString(db, line, stopwords)

    orig_line = line
    line = line.split()
    i = 0
    if len(line) >= 5:
        while i < len(line) -4:
            term = line[i] + " " + line[i+1] + " " + line[i+2] + " " + line[i+3] + " " + line[i+4]

            if checkType(db, term, stopwords, orig_line) == False:
                term = line[i] + " " + line[i+1] + " " + line[i+2] + " " + " " + line[i+3]

                if checkType(db, term, stopwords, orig_line) == False:
                    term = line[i] + " " + line[i+1] + " " + line[i+2]

                    if checkType(db, term, stopwords, orig_line) == False:
                        term = line[i] + " " + line[i+1] 

                        if checkType(db, term, stopwords, orig_line) == False:
                            term = line[i]
                                 
                            if checkType(db, term, stopwords, orig_line) == True:
                                getType(db, term, type_dict, stopwords)
                                #getICD10(term, stopwords, icd_dict)

                            i=i+1 #move the index by one even if the term isnt in the MRCONSO

                        else:
                            getType(db, term, type_dict, stopwords)
                            #getICD10(term, stopwords, icd_dict)
                            i = i+2
                    else:
                        getType(db, term, type_dict, stopwords)
                        #getICD10(term, stopwords, icd_dict)
                        i = i+3
                else:
                    getType(db, term, type_dict, stopwords)
                    #getICD10(term, stopwords, icd_dict)
                    i = i+4
            else:
                getType(db, term, type_dict, stopwords)
                #getICD10(term, stopwords, icd_dict)
                i = i+5


    #check the end of the sentence
    if  len(line) >= 4 and i <= len(line)-4:
        term = line[i] + " " + line[i+1] + " " + line[i+2] + " " + line[i+3]
             
        if checkType(db, term, stopwords, orig_line) == False:
            term = line[i]+ " " + line[i+1] + " " + line[i+2]
            
            if checkType(db, term, stopwords, orig_line) == False:
                term = line[i]+ " " + line[i+1] 

                if checkType(db, term, stopwords, orig_line) == False:
                    term = line[i]

                    if checkType(db, term, stopwords, orig_line) == True:
                        getType(db, line[i], type_dict, stopwords)
                        #getICD10(line[i],  stopwords, icd_dict)
                    i = i+1
                else:
                    getType(db, term, type_dict, stopwords)
                    #getICD10(term, stopwords, icd_dict)
                    i = i+2
            else:
                getType(db, term, type_dict, stopwords)
                #getICD10(term, stopwords, icd_dict)
                i = i+3
        else:
            getType(db, term, type_dict, stopwords)
            #getICD10(term, stopwords, icd_dict)
            i = i+4
    

    
    #check the end of the sentence                                                                                                                                                                    
    if  len(line) >= 3 and i <= len(line)-3:
        term = line[i]+ " " + line[i+1] + " " + line[i+2]

        if checkType(db, term, stopwords, orig_line) == False:
            term = line[i]+ " " + line[i+1]

            if checkType(db, term, stopwords, orig_line) == False:
                term = line[i]

                if checkType(db, term, stopwords, orig_line) == True:
                    getType(db, line[i], type_dict, stopwords)
                    #getICD10(line[i], stopwords, icd_dict)
                i = i+1
            else:
                getType(db, term, type_dict, stopwords)
                #getICD10(term, stopwords, icd_dict)
                i = i+2
        else:
            getType(db, term, type_dict, stopwords)
            #getICD10(term, stopwords, icd_dict)
            i = i+3


    #check the end of the sentence                                                                                                                                                                    
    if  len(line) >= 2 and i <= len(line)-2:
        term = line[i]+ " " + line[i+1]

        if checkType(db, term, stopwords, orig_line) == False:
            term = line[i]

            if checkType(db, term, stopwords, orig_line) == True:
                getType(db, line[i], type_dict, stopwords)
                #getICD10(line[i], stopwords, icd_dict)
            i = i+1
        else:
            getType(db, term, type_dict, stopwords)
            #getICD10(term, stopwords, icd_dict)
            i = i+2



    if len(line) >=1 and i <= len(line)-1:
        if checkType(db, line[i], stopwords, orig_line) == True:
            getType(db, line[i], type_dict, stopwords)
            #getICD10(line[i], stopwords, icd_dict)



if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Run as python convert_input.py [inclusion/exclusion]"
        sys.exit(-1)

    criteria = sys.argv[1]
    type_dict = dict()
    icd_dict = dict() #term is the key and the value is the list of ICD codes. We want this so we can OR values corresponding to the same term (ICD and UMLS values)

    client = MongoClient()
    db = client.umls

    #get stopwords                                                                                                                                                                              
    with open("/Users/gangopad/Company/CysticFibrosis/CFSocialMedia/Dictionary/stopwords.pickle", "rb") as f:
        stopwords = pickle.load(f)

    criteria = criteria.replace("_", " ")

    convertInput(db, criteria, stopwords, type_dict, icd_dict)
    out = ""

    for t in type_dict:
        val = type_dict[t].split(",") 
        for v in val:
            if v in icd_dict:
                icds = icd_dict[v]
                icds = icds.split(",")

                if len(icds) > 0:
                    out = out + "("

                    for icd in icds:
                        out = out + "ICD10: " +  icd + " OR "

                    out = out[:-4]
                    out = out + ") OR "
                

            out = out +  t + ": " + v + " AND "

    out = out[:-5]

    print out
    

