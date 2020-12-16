# -*- coding: utf-8 -*-


import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""
In this script we take an input EMR and structure and store into patients.rest (rest2 for testing)
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
                elif word == "arthritis":
                    new_word = "arthritis"
                input = input.replace(word, new_word)

    """
    if "lis" in input:
        print "Found lisinopril"
        print "New: ", input
        print "Old: ", orig
    """

    return input




#replaces strings that are semantically similar (plurals, etc) with the preferred string                                                                                                
def CleanString(db, input, stopwords):
    cleaned_input = input
    input = input.strip()
    input = input.split()
    exclude = set(string.punctuation)

    for word in input:

        #he maps to helium                                                                                                                                                                    
        if word.lower() != "he" and word not in stopwords:

            if word[-1] in exclude: #we get rid of punctuation at the end of the sentence from the word                                                                                         
                word = word[:-1]

            res = db.lower_lragr.find({"TERM":word}, {"PT":"1"})
            pt = word

            for document in res:
                #print document                                                                                                                                                               
                pt = document['PT']

            cleaned_input = cleaned_input.replace(word, pt)


    return cleaned_input #return if cleaned version exists above. Otherwise return original word




#we look up the type corresponding to the term by first looking up CUI in mrconso and then finding type in mrsty                                                                        
def getType(db, term, type_dict, stopwords, linkback, line):
    cuis = []

    term = term.strip()
    term = term.lower()

    #print term

    #exits if any numbers or stopwords in the term
    term_list = term.split()
    for w in term_list:
        if w in stopwords and w != "back" and w != "left":
            return ""

    res = db.lower_mrconso.find({"TERM":term})
    for document in res:                                                                                                                                                                        
        cuis.append(document["CUI"])
        

    for cui in cuis:
        res = db.lower_mrsty.find({"CUI":cui})
        for document in res:    
            t = document["TYPE"]

            if t in type_dict:
                res = type_dict[t]
                res_list = res.split(",")
            
                #dont want to cause repeats
                if term not in res_list:
                    res = res + "," + term
                    linkback[t + ":" + term] = line

                type_dict[t] = res
            else:
                type_dict[t] = term
                linkback[t + ":" + term] = line


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
        if w in stopwords and w != "back" and w != "left":
            return False


    #We implement checking for negative phrases here (to prevent picking up on negative conditions
    if term in line and (("no evidence of " + term) in line or ("did not show evidence for " + term) in line or ("no " + term) in line or ("negative for " + term) in line or (term + " r/o") in line or ("low probability for " + term) in line or ("hard to interpret as a sign for " + term) in line or "? no" in line or ":no" in line or ": no" in line or "father" in line or "mother" in line or "family history" in line):
        return False



    #print term
    res = db.lower_mrconso.find({"TERM":term})

    if len(list(res)) == 0:
        return False
    else:
        return True
        


#extract the types and other fields for the database
def ExtractTypes(type_dict, db, emr, stopwords, linkback):

    emr = emr.split("\n")
    for line in emr:
        orig = line
        line = line.strip()
             
        #take out punctuation
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")
        line = line.replace(".", "")
        line = line.replace("?", "")
        line = line.replace("!", "")
        line = line.replace(":", "")
        line = line.replace("," , " ")
        line = line.replace("-", " ")
        line = line.replace("(", "")
        line = line.replace(")", "")
        line = line.replace('"', '')

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
                    term = line[i] + " " + line[i+1] + " " + line[i+2] + " "  + line[i+3]

                    if checkType(db, term, stopwords, orig_line) == False:
                        term = line[i] + " " + line[i+1] + " " + line[i+2]

                        if checkType(db, term, stopwords, orig_line) == False:
                            term = line[i] + " " + line[i+1] 

                            if checkType(db, term, stopwords, orig_line) == False:
                                term = line[i]
                                 
                                if checkType(db, term, stopwords, orig_line) == True:
                                    getType(db, term, type_dict, stopwords, linkback, orig)

                                i=i+1 #move the index by one even if the term isnt in the MRCONSO

                            else:
                                getType(db, term, type_dict, stopwords, linkback, orig)
                                #getICD10(term, stopwords, icd_dict)

                                i = i+2
                        else:
                            getType(db, term, type_dict, stopwords, linkback, orig)
                            #getICD10(term, stopwords, icd_dict)
                            i = i+3
                    else:
                        getType(db, term, type_dict, stopwords, linkback, orig)
                        #getICD10(term, stopwords, icd_dict)
                        i = i+4
                else:
                    getType(db, term, type_dict, stopwords, linkback, orig)
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
                            getType(db, line[i], type_dict, stopwords, linkback, orig)
                        i = i+1
                    else:
                        getType(db, term, type_dict, stopwords, linkback, orig)
                        i = i+2
                else:
                    getType(db, term, type_dict, stopwords, linkback, orig)
                    i = i+3
            else:
                getType(db, term, type_dict, stopwords, linkback, orig)
                i = i+4
    

    
        #check the end of the sentence                                                                                                                                                                
        if  len(line) >= 3 and i <= len(line)-3:
            term = line[i]+ " " + line[i+1] + " " + line[i+2]

            if checkType(db, term, stopwords, orig_line) == False:
                term = line[i]+ " " + line[i+1]

                if checkType(db, term, stopwords, orig_line) == False:
                    term = line[i]

                    if checkType(db, term, stopwords, orig_line) == True:
                        getType(db, line[i], type_dict, stopwords, linkback, orig)
                    i = i+1
                else:
                    getType(db, term, type_dict, stopwords, linkback, orig)
                    i = i+2
            else:
                getType(db, term, type_dict, stopwords, linkback, orig)
                i = i+3


        #check the end of the sentence                                                                                                                                                                
        if  len(line) >= 2 and i <= len(line)-2:
            term = line[i]+ " " + line[i+1]

            if checkType(db, term, stopwords, orig_line) == False:
                term = line[i]

                if checkType(db, term, stopwords, orig_line) == True:
                    getType(db, line[i], type_dict, stopwords, linkback, orig)
                i = i+1
            else:
                getType(db, term, type_dict, stopwords, linkback, orig)
                i = i+2



        if len(line) >=1 and i <= len(line)-1:
            if checkType(db, line[i], stopwords, orig_line) == True:
                getType(db, line[i], type_dict, stopwords, linkback, orig)


#we pull the date and return 
def getDate(emr, type):

    dates = []
    dob = ""

    if type == "text" or type == "xml":
        emr = emr.split("\n")
    else:
        emr = emr.split(",")

    for line in emr:
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")
        match = re.search(r'\d{4}-\d{2}-\d{2}', line)
        match2 = re.search(r'\d{2}/\d{2}/\d{4}', line)
        match3 = re.search(r'\d{2}-\d{2}-\d{4}', line)
        match4 = re.search(r'\d{2}-\d{2}-\d{2}', line)
        match5 = re.search(r'\d{2}/\d{2}/\d{2}', line)

        line = line.strip()

        if match is not None:
            try:
                date = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
                #dates.append(str(date))

                if date.year < 1999:
                    dob = str(datetime.datetime(date.year, date.month, date.day))
                else:
                    dates.append(datetime.datetime(date.year, date.month, date.day))
            except ValueError:
                continue #If you are doing this in a loop (looping over the lines) so that it moves onto next iteration
        
        elif match2 is not None:
            try:
                date = datetime.datetime.strptime(match2.group(), '%m/%d/%Y').date()
                #dates.append(str(date))

                if date.year < 1999:
                    dob = str(datetime.datetime(date.year, date.month, date.day))

                else:
                    dates.append(datetime.datetime(date.year, date.month, date.day))

            except ValueError:
                continue

        elif match3 is not None:
            try:
                date = datetime.datetime.strptime(match3.group(), '%m-%d-%Y').date()
                #dates.append(str(date))

                if date.year < 1999:
                    dob = str(datetime.datetime(date.year, date.month, date.day))

                else:
                    dates.append(datetime.datetime(date.year, date.month, date.day))

            except ValueError:
                continue

        elif match4 is not None:
            try:
                date = datetime.datetime.strptime(match4.group(), '%m-%d-%y').date()
                #dates.append(str(date))

                if date.year < 1999:
                    dob = str(datetime.datetime(date.year, date.month, date.day))

                else:
                    dates.append(datetime.datetime(date.year, date.month, date.day))

            except ValueError:
                continue

        elif match5 is not None:
            try:
                date = datetime.datetime.strptime(match5.group(), '%m/%d/%y').date()
                #dates.append(str(date))

                if date.year < 1999:
                    dob = str(datetime.datetime(date.year, date.month, date.day))

                else:
                    dates.append(datetime.datetime(date.year, date.month, date.day))

            except ValueError:
                continue


    return dob, dates


#we pull the physician name
def getPhysician(emr):
    physician = ""
    emr = emr.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")


    if "M.D." in emr:
        emr = emr.split()
        for e in emr:
            if "M.D." in e:
                p_index = emr.index(e) 

        physician = emr[p_index -2] + " " + emr[p_index-1] + " " + emr[p_index]

    elif "MD" in emr:
        emr = emr.split()
        for e in emr:
            if "MD" in e:
                p_index = emr.index(e)

        physician = emr[p_index -2] + " " + emr[p_index-1] + " " + emr[p_index]

    else:
        physician = "N/A"

    return physician


#returns information on clinic/hospital
def getHospital(emr, type):
    if type == "text" or type == "xml":
        emr = emr.split("\n")
    else:
        emr = emr.split(",")


    for line in emr:
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")

        lower_line = line.lower()
        if "clinic" in lower_line or "associates" in lower_line or "dept" in lower_line or "center" in lower_line:
            line = re.split('; |, |\*|\n|.',line) #split on comma for xml, json
            for l in line:
                lower_line = l.lower()
                if "clinic" in lower_line or "associates" in lower_line or "dept" in lower_line or "center" in lower_line:
                    return l

    return "Unknown"



#pulls hba1c levels
def gethba1c(emr):
    hba1c = -1

    """
    if type == "text" or type == "xml":
        emr = emr.split("\n")
    else:
        emr = emr.split(",")
    """
    emr = emr.split("\n")


    for line in emr:
        line = line.strip()
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")

        line = line.split()

        for word in line:
            i = line.index(word)
            if (i+2) < len(line):
                if "a1c" in word.lower() and (len(word) == 3 or len(word) == 5):
                    if "of" in line[i+1] and line[i+2].replace('.','',1).isdigit() == True:
                        hba1c = float(line[i+2])
                        #print line

                    if line[i+1].replace('/','',1).isdigit() == True and line[i+2].replace('.','',1).isdigit() == True:
                        hba1c = float(line[i+2])
                        #print line

            if (i+1) < len(line):
                if "a1c" in word.lower() and (len(word) == 3 or len(word) == 5):
                    if line[i+1].replace('.','',1).isdigit() == True:
                        hba1c = float(line[i+1])
                        #print line

    #print "Hba1c: ", hba1c
    return hba1c



#figures out if the patient is a smoker (checks regular expressions to make sure there are no negations)
def isSmoker(emr, type):

    if type == "text" or type == "xml":
        emr = emr.split("\n")
    else:
        emr = emr.split(",")

    is_smoker = "N/A"
    smoking_terms = ["smoker", "smoking", "cigarette", "smoke"]

    for line in emr:
        line = line.strip()
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")

        for term in smoking_terms:
            if term in line and ("not" in line or "non" in line or "False"):
                is_smoker = "False"
            elif term in line:
                is_smoker = "True"

    return is_smoker



#returns the doses in dictionary format which allows for storage in mongodb with medication as key and dosage as value
def getDosesDict(emr, pharmacologic_substances):
    emr = emr.split("\n")
    doses = dict()

    for line in emr:
        orig = line
        line = line.strip()
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")
        line = line.replace("?", "")
        line = line.replace("!", "")
        line = line.replace(":", "")
        line = line.replace("," , " ")
        line = line.replace("-", " ")
        line = line.replace("(", "")
        line = line.replace(")", "")

        line = line.split()
        num_meds = 0 #number of medicines found in line
        main_med = "" #this is used to store the med if there is just one for line (used for pulling dates in next line)

        for word in line:
            original = word
            word = word.lower()
            if word in pharmacologic_substances:
                #print word
                num_meds = num_meds + 1
                main_med = word

                i = line.index(original)

                #accounts for mg of
                if (i-3) > -1:
                    if "mg" in line[i-2].lower():
                        dosage = line[i-3]

                        if dosage.replace('.','',1).isdigit() == True:
                            doses[word + "(mg)"] = float(dosage)

                if (i+3) < len(line):
                    if "mg" in line[i+3].lower():
                        dosage = line[i+2]

                        if dosage.replace('.','',1).isdigit() == True:
                            doses[word + "(mg)"] = float(dosage)

                #print line[i] + " " + line[i+1] + " " + line[i+2]
                if (i+2) < len(line):
                    if "mg" in line[i+2].lower():
                        dosage = line[i+1]
                            
                        if dosage.replace('.','',1).isdigit() == True:
                            doses[word + "(mg)"] = float(dosage)


                if (i+1) < len(line):
                    if "mg" in line[i+1].lower():
                        dosage = line[i+1]
                        num_dosage = ''
                        for ch in dosage:
                            if ch.isdigit() == True:
                                num_dosage = num_dosage + ch
                            
                        if num_dosage.replace('.','',1).isdigit() == True:
                            #print num_dosage
                            doses[word + "(mg)"] = float(num_dosage)

                if "tablet" in orig.lower():
                    doses[word + "(route)"] = "tablet"
                elif "inhale" in orig.lower():
                    doses[word + "(route)"] = "inhalant"
                elif "intravenous" in orig.lower() or "iv" in orig.lower() or "injection" in orig.lower():
                    doses[word + "(route)"] = "injection"
                else:
                    doses[word + "(route)"] = "tablet"


                if "prn" in orig or "as necessary" in orig.lower():
                    doses[word + "(frequency)"] = "prn"
                elif "pa" in orig.lower():
                    doses[word + "(frequency)"] = "pa"
                elif "qid" in orig.lower():
                    doses[word + "(frequency)"] = "qid"
                elif "tid" in orig.lower():
                    doses[word + "(frequency)"] = "tid"
                elif "qm" in orig.lower():
                    doses[word + "(frequency)"] = "qm"
                elif "qod" in orig.lower():
                    doses[word + "(frequency)"] = "qod"

                #pull start and end dates
                (start_date, end_date) = extractDateFromLine(orig)
                doses[word + "(end_date)"] = end_date
                doses[word + "(start_date)"] = start_date


        #check if next line is a date if this line has just one pharmacologic substance
        if num_meds == 1 and len(emr) > emr.index(orig) + 1:
            next_line = emr[emr.index(orig) + 1] 
            (start_date, end_date) = extractDateFromLine(next_line)

            if doses[main_med + "(end_date)"] == "":
                doses[main_med + "(end_date)"] = end_date

            if doses[main_med + "(start_date)"] == "":
                doses[main_med + "(start_date)"] = start_date
            

    return doses


#extracts date from given line and returns
def extractDateFromLine(orig):
    #pull start and end dates
    start_date  = ""
    end_date = ""

    orig = orig.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")



    match = re.search(r'\d{4}-\d{2}-\d{2}', orig)
    match2 = re.search(r'\d{2}/\d{2}/\d{4}', orig)
    match3 = re.search(r'\d{2}-\d{2}-\d{4}', orig)
    match4 = re.search(r'\d{2}-\d{2}-\d{2}', orig)
    match5 = re.search(r'\d{2}/\d{2}/\d{2}', orig)

    orig_line = orig.strip()

    if match is not None:
        try:
            date = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
            date = datetime.datetime(date.year, date.month, date.day)
            date = date.strftime("%a") + " " + date.strftime("%b") + " " + date.strftime("%m") + " " + date.strftime("%Y")
 
            #dates.append(str(date))
            if "end" in orig_line:
                end_date = date
            else:
                start_date = date

        except ValueError:
            pass
        
    elif match2 is not None:
        try:
            date = datetime.datetime.strptime(match2.group(), '%m/%d/%Y').date()
            date = datetime.datetime(date.year, date.month, date.day)
            date = date.strftime("%a") + " " + date.strftime("%b") + " " + date.strftime("%m") + " " + date.strftime("%Y")

            #dates.append(str(date))
            if "end" in orig_line:
                end_date = date
            else:
                start_date = date

        except ValueError:
            pass

    elif match3 is not None:
        try:
            date = datetime.datetime.strptime(match3.group(), '%m-%d-%Y').date()
            date = datetime.datetime(date.year, date.month, date.day)
            date = date.strftime("%a") + " " + date.strftime("%b") + " " + date.strftime("%m") + " " + date.strftime("%Y")


            #dates.append(str(date))
            if "end" in orig_line:
                end_date = date
            else:
                start_date = date

        except ValueError:
            pass

    elif match4 is not None:
        try:
            date = datetime.datetime.strptime(match4.group(), '%m-%d-%y').date()
            date = datetime.datetime(date.year, date.month, date.day)
            date = date.strftime("%A") + " " + date.strftime("%b") + " " + date.strftime("%m") + " " + date.strftime("%Y")


            #dates.append(str(date))
            if "end" in orig_line:
                end_date = date
            else:
                start_date = date

        except ValueError:
            pass

    elif match5 is not None:
        try:
            date = datetime.datetime.strptime(match5.group(), '%m/%d/%y').date()
            date = datetime.datetime(date.year, date.month, date.day)
            date = date.strftime("%A") + " " + date.strftime("%b") + " " + date.strftime("%d") + " " + date.strftime("%Y")


            #dates.append(str(date))
            if "end" in orig_line:
                end_date = date
            else:
                start_date = date

        except ValueError:
            pass

    return start_date, end_date



#pulls the AEs 
def extractAdverseEvents(type_dict, emr, type, dob):
    adverse_events = []
    collect = 0
    disease_keys = ["Disease or Syndrome", "Neoplastic Process", "Diagnostic Procedure", "Therapeutic or Preventive Procedure", "Finding", "Sign or Symptom"]

    if type == "text" or type == "xml":
        emr = emr.split("\n")
    else:
        emr = emr.split(",")

    for line in emr:
        orig = line

        #take out punctuation
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")                                                                                                                                                         
        line = line.replace(".", "")
        line = line.replace("?", "")
        line = line.replace("!", "")
        line = line.replace(":", "")
        line = line.replace("," , " ")
        line = line.replace("-", " ")

        line = line.lower()

        #accounts for case where medical history is listed one per line -- collect mode is on
        if collect == 1:
            if len(line.strip()) == 0:
                collect = 0
            else:
                for typeKey in type_dict:
                    val = type_dict[typeKey]
                    val = val.strip()
                    val = val.split(",")
                    
                    #currently pulls the last line from the EMR that matches the pattern
                    for term in val:
                        if term in line and typeKey in disease_keys:
                            ae = {}
                            (start_date, end_date) = extractDateFromLine(orig)
                            ae["adverse event"] = term
                            ae["linkback"] = orig
                            ae["start date"] = start_date
                            ae["end date"] = end_date

                            res = db.ae.find({"Adverse Event": term.lower().capitalize()})
                            category = "Unknown"
                            for document in res:
                                category = document["Category"]

                            ae["category"]  = category
                            adverse_events.append(ae)


        #accounts for case where medical history is listed one per line
        if ("ae" in line.split() or "adverse event" in line) and len(line.strip().split()) < 4:
            collect = 1


        for typeKey in type_dict:
            val = type_dict[typeKey]
            val = val.strip()
            val = val.split(",")

            #currently pulls the last line from the EMR that matches the pattern
            for term in val:
                if term in line and ("adverse event" in line or "ae" in line.split()) and typeKey in disease_keys:
                    ae = {}
                    (start_date, end_date) = extractDateFromLine(orig)
                    ae["adverse event"] = term
                    ae["linkback"] = orig
                    ae["start date"] = start_date
                    ae["end date"] = end_date

                    res = db.ae.find({"Adverse Event":term})
                    category = "Unknown"
                    for document in res:
                        category = document["Category"]

                    ae["category"]  = category
                    adverse_events.append(ae)


    print adverse_events
    return list(adverse_events)



#strips non ascii
def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)



#extracts the vital signs for a specific patient
def extractVitals(emr):
    d = {'height': 'NULL', 'weight': 'NULL', 'sys_bp': -1, 'dia_bp': -1, 'resp_rate': -1, 'heart_rate': -1, 'temperature': -1, 'temp_method':'oral', 'bp_method': 'NULL', 'bp_location': 'NULL', 'bp_position': 'NULL'}
    emr = emr.split("\n")

    for line in emr:
        line = line.lower()
        line = line.strip()
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'").replace(u'\xe2', u"'")
        line = line.replace("?", "")
        line = line.replace("!", "")
        line = line.replace(":", "")
        line = line.replace("," , " ")
        line = line.replace(':', '')
        line = line.replace('-', ' ')
        orig = line

        line = line.split()

        for word in line:
            ind = line.index(word)
            stripped_word = strip_non_ascii(word)


            #height
            if word.replace(".", "", 1).isdigit() == True and (ind+1) < len(line) and ("in" in line[ind +1] or "inches" in line[ind +1]):
                d['height'] = word + " (in)"
            elif word.replace(".", "", 1).isdigit() == True and (ind+1) < len(line) and ("cm" in line[ind +1] or "centimeter" in line[ind + 1]):
                d['height'] = word + " (cm)"
            elif ("'" in stripped_word or "'" in word) and stripped_word.replace("'", "").replace(".", "").isdigit() == True:
                d['height'] = word
            elif "ft" in line and "in" in line:
                d['height'] = line[line.index("ft") - 1] + "'" + line[line.index("in") - 1]

            #weight
            if word.replace(".", "", 1).isdigit() == True and (ind+1) < len(line) and ("lb" in line[ind +1] or "pound" in line[ind + 1]) and "/" not in line[ind + 1]:
                if ((ind + 2) < len(line) and "/" not in line[ind + 2]) or (ind + 2) >= len(line): 
                    d['weight'] = word + " (lbs)"
            elif word.replace(".", "", 1).isdigit() == True and (ind+1) < len(line) and ("kg" in line[ind +1] or "kilo" in line[ind + 1]) and "/" not in line[ind + 1]:
                if ((ind + 2) < len(line) and "/" not in line[ind + 2]) or (ind + 2) >= len(line): 
                    d['weight'] = word + "(kg)"
            elif "lbs" in word and word.replace(".", "", 1).replace("lbs", "").isdigit() == True and "/" not in word:
                d['weight'] = word.replace("lbs", "") + " (lbs)"
            elif "kg" in word and word.replace(".", "", 1).replace("kg", "").isdigit() == True and "/" not in word:
                d['weight'] = word.replace("kg", "") + " (kg)"


            #temperature
            if word.replace(".", "", 1).isdigit() == True and (ind+1) < len(line) and (("f" in line[ind + 1] and len(line[ind +1].replace(".", "")) < 2) or ("fahrenheit" in line[ind +1].lower()) or ("degrees" in line[ind +1].lower())):
                temp = float(word)

                if temp > 90 and temp < 120:
                    d['temperature'] = float(word)

            elif word.replace(".", "", 1).isdigit() == True and (ind+1) < len(line) and (("c" in line[ind + 1] and len(line[ind +1].replace(".", "")) < 2) or ("celsius" in line[ind +1].lower()) or ("degrees" in line[ind +1].lower())):
                temp = float(word)

                if temp > 32 and temp < 45:
                    d['temperature'] = float(word)

            elif word.replace(".", "").replace("f", "").isdigit() == True and word.count(".") == 1 and "f" in word:
                temp = float(word.replace("f", ""))

                if temp > 90 and temp < 120:
                    d['temperature'] = temp
                

            elif word.replace(".", "").replace("c", "").isdigit() == True and word.count(".") == 1 and "c" in word:
                temp = float(word.replace("c", ""))

                if temp > 32 and temp < 45:
                    d['temperature'] = temp
                


        #bp
        if "mmhg" in line:
            ind = line.index("mmhg")

            if ind > 0 and "/" in line[ind -1] and line[ind -1].replace("/").isdigit() == True:
                bp = line[ind -1]
                bp = bp.split("/")
                d['sys_bp'] = float(bp[0])
                d['dia_bp'] = float(bp[1])
                d['bp_method'] = "N/A"
                d['bp_location'] = "N/A"
                d['bp_position'] = "N/A"

                if "right arm" in orig:
                    d['bp_location'] = "right arm"
                elif "left arm" in orig:
                    d['bp_location'] = "left arm"

                if "sitting" in orig:
                    d['bp_position'] = "sitting"

        elif "bp" in line:
            ind = line.index("bp")

            if ind + 1 < len(line) and "/" in line[ind +1] and line[ind -1].replace("/").isdigit() == True:
                bp = line[ind +1]
                bp = bp.split("/")
                d['sys_bp'] = float(bp[0])
                d['dia_bp'] = float(bp[1])
                d['bp_method'] = "N/A"
                d['bp_location'] = "N/A"
                d['bp_position'] = "N/A"

                if "right arm" in orig:
                    d['bp_location'] = "right arm"
                elif "left arm" in orig:
                    d['bp_location'] = "left arm"

                if "sitting" in orig:
                    d['bp_position'] = "sitting"



        #heart rate, resp rate
        if "bpm" in line:
            ind = line.index("bpm")

            if ind > 0 and line[ind -1].isdigit() == True:
                num = line[ind -1].strip()

                if int(num) < 20:
                    d['resp_rate'] = num
                else:
                    d['heart_rate'] = num

        elif "rpm" in line:
            ind = line.index("rpm")

            if ind > 0 and line[ind -1].isdigit() == True:
                num = line[ind -1].strip()

                if int(num) < 20:
                    d['resp_rate'] = num
                else:
                    d['heart_rate'] = num

        elif "reg" in line:
            ind = line.index("reg")

            if ind > 0 and line[ind -1].isdigit() == True:
                num = line[ind -1].strip()

                if int(num) < 20:
                    d['resp_rate'] = num
                else:
                    d['heart_rate'] = num

        elif "pulse" in line:
            ind = line.index("pulse")

            if ind + 1 < len(line) and line[ind +1].isdigit() == True:
                num = line[ind +1].strip()
                d['heart_rate'] = num

        elif "rate" in line:
            ind = line.index("rate")

            if ind + 1 < len(line) and line[ind +1].isdigit() == True:
                num = line[ind +1].strip()


                if int(num) < 20:
                    d['resp_rate'] = num
                else:
                    d['heart_rate'] = num


    return d


#extracts and stores demographic information for a specific patient
def extractDemographic(emr):
    findage = True
    findgender = True
    findethnicity = True
    emr = emr.split("\n")

    d = {'age':-1, 'gender':'NULL', 'ethnicity':'NULL'}

    for line in emr:
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")
        line = line.replace(".", "")
        line = line.replace("?", "")
        line = line.replace("!", "")
        line = line.replace(":", "")
        line = line.replace("," , " ")
        line = line.replace('.', '')
        line = line.replace('-', ' ')
        orig = line
        line = line.strip()
        #check for demographics
        line = line.split()
        for word in line:
            ind = line.index(word)

            if word.isdigit() == True and (ind+1) < len(line) and (("year" in line[ind+1] and "old" in orig) or "yo" in line[ind+1] or "yr" in line[ind+1]) and findage == True:
                age = word
                d['age'] = float(age)
                findage = False
                    
                """
                if int(age) < 10:
                print patient_id
                print age , line[ind+1]
                print line
                """

            if ('female' in word.lower()  or 'woman' == word.lower() or 'lady' == word.lower()) and findgender == True:
                gender = 'female'
                d['gender'] = gender
                findgender = False
            elif ('male' in word.lower()  or 'man' == word.lower() or "gentleman" == word.lower()) and findgender == True:
                gender = 'male'
                d['gender'] = gender
                findgender = False

                
            if "white" in word.lower() and ("male" in line or "female" in orig or "patient" in orig):
                d['ethnicity'] = "white"
                findethnicity = False
            elif ("black" in word.lower() or "african" in word.lower()) and ("male" in line or "female" in orig or "patient"in orig):
                d['ethnicity'] = "black"
                findethnicity = False
            elif "indian" in word.lower() and ("male" in line or "female" in orig or "patient"in orig):
                d['ethnicity'] = "indian"
                findethnicity = False
            elif "chinese" in word.lower() and ("male" in line or "female" in orig or "patient"in orig):
                d['ethnicity'] = "chinese"
                findethnicity = False
            elif "caribbean" in word.lower() and ("male" in line or "female" in orig or "patient"in orig):
                d['ethnicity'] = "caribbean"
                findethnicity = False
            elif "hispanic" in word.lower() and ("male" in line or "female" in orig or "patient"in orig):
                d['ethnicity'] = "hispanic"
                findethnicity = False

    return d

def getICDType(term, db, icd9, icd10):
    term = term.strip()
    term = term.lower()
    ret = False

    res = db.lower_mrconso.find({"TERM":term})
    for document in res:                                                                                                                                                                   
        source = document["F12"]
        code = document["F11"]
        
        if  "icd9" in source:
            icd9.append(str(code) + "-" + term)
            ret = True

        """
        if "icd10" in source:
            icd10.append(term + "-" + str(code))
            ret = True
        """

    #load the icd10 codes from the icd10cm_codes_2016.txt file here instead of using UMLS
    res = db.icd10.find({"TERM":term})
    for document in res:
        code = document["CODE"]
        icd10.append(str(code) + "-" + term)
        ret = True

    return ret

def ExtractICDCodes(db, emr):
    icd9 = []
    icd10 = []
    emr = emr.split("\n")
    
    for line in emr:
        line = line.strip()

        #take out punctuation   
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")                                                                                                                                                      
        line = line.replace(".", "")
        line = line.replace("?", "")
        line = line.replace("!", "")
        line = line.replace(":", "")
        line = line.replace("," , " ")
        line = line.replace("-", " ")
        line = CleanString(db, line, stopwords)

        line = line.split()
        i = 0

        if len(line) >= 5:
            while i < len(line) -4:
                term = line[i] + " " + line[i+1] + " " + line[i+2] + " " + line[i+3] + " " + line[i+4]

                if getICDType(term, db, icd9, icd10) == False:
                    term = line[i] + " " + line[i+1] + " " + line[i+2] + " " + " " + line[i+3]

                    if getICDType(term, db, icd9, icd10) == False:
                        term = line[i] + " " + line[i+1] + " " + line[i+2]

                        if getICDType(term, db, icd9, icd10) == False:
                            term = line[i] + " " + line[i+1] 

                            if getICDType(term, db, icd9, icd10) == False:
                                term = line[i]
                                 
                                getICDType(term, db, icd9, icd10)
                                i=i+1 #move the index by one even if the term isnt in the MRCONSO

                            else:
                                i = i+2
                        else:
                            i = i+3
                    else:
                        i = i+4
                else:
                    i = i+5


        #check the end of the sentence
        if  len(line) >= 4 and i <= len(line)-4:
            term = line[i] + " " + line[i+1] + " " + line[i+2] + " " + line[i+3]
             
            if getICDType(term, db, icd9, icd10) == False:
                term = line[i]+ " " + line[i+1] + " " + line[i+2]
            
                if getICDType(term, db, icd9, icd10) == False:
                    term = line[i]+ " " + line[i+1] 

                    if getICDType(term, db, icd9, icd10) == False:
                        term = line[i]

                        getICDType(term, db, icd9, icd10)
                        i = i+1

                    else:
                        i = i+2
                else:
                    i = i+3
            else:
                i = i+4
    

        if  len(line) >= 3 and i <= len(line)-3:
            term = line[i]+ " " + line[i+1] + " " + line[i+2]

            if getICDType(term, db, icd9, icd10) == False:
                term = line[i]+ " " + line[i+1]

                if getICDType(term, db, icd9, icd10) == False:
                    term = line[i]
                    getICDType(term, db, icd9, icd10)
                    i = i+1
                else:
                    i = i+2
            else:
                i = i+3

        if  len(line) >= 2 and i <= len(line)-2:
            term = line[i] + " " + line[i+1]

            if getICDType(term, db, icd9, icd10) == False:
                term = line[i]
                getICDType(term, db, icd9, icd10)
                i = i+1

            else:
                i = i+2

        if len(line) >=1 and i <= len(line)-1:
            getICDType(line[i], db, icd9, icd10)

        

    return icd9, icd10



#returns the hdl and ldl levels
def getCholesterol(emr):
    hdl = -1
    ldl = -1

    if type == "text" or type == "xml":
        emr = emr.split("\n")
    else:
        emr = emr.split(",")

    for line in emr:
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")
        line = line.strip()
        line = line.split()
            
        for word in line:
            i = line.index(word)
            if (i+2) < len(line):
                if "hdl" in word.lower() and len(word) == 3:
                    #print "IN HDL: ", filename
                    #print line
                    if "of" in line[i+1].lower() and line[i+2].replace(".", "").isdigit() == True:
                        hdl = float(line[i+2])


                    if "hdl" in word.lower() and (len(word) == 3):
                        if line[i+1].replace('.','',1).isdigit() == True and "mg" in line[i+2]:
                            hdl = float(line[i+1])

            if (i+2) < len(line):
                if "ldl" in word.lower() and len(word) == 3:
                    #print "IN LDL: ", filename
                    #print line
                    if "of" in line[i+1].lower() and line[i+2].replace(".", "").isdigit() == True:
                        ldl = float(line[i+2])

                    if "hdl" in word.lower() and (len(word) == 3):
                        if line[i+1].replace('.','',1).isdigit() == True and "mg" in line[i+2]:
                            hdl = float(line[i+1])

    #print "Hdl: ", hdl
    #print "Ldl: ", ldl

    return hdl, ldl


#this returns the EMR in HTML readable format
def getBody(emr):
    emr = emr.replace("&", "&amp;")
    emr = emr.replace("<", "&lt;")
    emr = emr.replace(">", "&gt;")
    emr = emr.replace('"', "&quot;")
    emr = "<p>" + emr + "</p>"
    emr = emr.replace("\n", "<br>")
    emr = emr.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")

    return emr



def getMedicalHistory(type_dict, emr, type, linkback):
    medical_history = set()
    collect = 0
    collect_list = 0
    pattern = ['\xc2\xb7', '\xe2\x80\xa2']
    pattern = "(" + ")|(".join(pattern) + ")"
    disease_keys = ["Disease or Syndrome", "Neoplastic Process", "Diagnostic Procedure", "Therapeutic or Preventive Procedure", "Finding", "Sign or Symptom"]
    start_line = "" #this marks the line that states "medical history", "pmh", etc
    emr_sentences = emr.split(".")

    if type == "text" or type == "xml":
        emr = emr.split("\n")
    else:
        emr = emr.split(",")

    for line in emr:
        orig = line
        line = line.strip()
        line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")

        line = line.replace("\t", " ")

        #take out punctuation                                                                                                                                                                 
        line = line.replace(".", "")
        line = line.replace("?", "")
        line = line.replace("!", "")
        line = line.replace("," , " ")

        line = line.lower()

        #accounts for case where medical history is listed one per line -- collect mode is on
        if collect == 1:
            if len(line.strip()) == 0 and emr[emr.index(line) -1] != start_line:
                collect = 0
            else:
                for typeKey in type_dict:
                    val = type_dict[typeKey]
                    val = val.strip()
                    val = val.split(",")
                    
                    #currently pulls the last line from the EMR that matches the pattern
                    for term in val:
                        if term in line and typeKey in disease_keys:
                            medical_history.add(term)
                            linkback[typeKey + ":" + term] = orig


        #accounts for case where medical history is listed one per line as a list -- collect mode is on
        if collect_list == 1:
            if len(line.strip()) > 0 and line.strip()[0] != "-" and line.strip()[0].isdigit() == False and bool(re.match(pattern, line)) == False and emr[emr.index(line) -1] != start_line:
                collect_list = 0
            else:
                for typeKey in type_dict:
                    val = type_dict[typeKey]
                    val = val.strip()
                    val = val.split(",")
                    
                    #currently pulls the last line from the EMR that matches the pattern
                    for term in val:
                        if term in line and typeKey in disease_keys:
                            medical_history.add(term)
                            linkback[typeKey + ":" + term] = orig


        #accounts for case where medical history is listed one per line
        if ("pmh" in line or "medical history" in line or "ongoing medical history" in line or "surgical history" in line or "major events" in line) and "family history" not in line and len(line.strip().split())  < 4:
            collect = 1
            start_line = line

        if ("pmh" in line or "medical history" in line or "ongoing medical history" in line or "surgical history" in line or "major events" in line) and "family history" not in line and line.strip()[-1] == ":":
            collect_list = 1
            start_line = line


        if "history" in line or "pmh" in line:
            for typeKey in type_dict:
                val = type_dict[typeKey]
                val = val.strip()
                val = val.split(",")

                #currently pulls the last line from the EMR that matches the pattern
                for term in val:
                    if term in line and ("history" in line or "pmh" in line) and typeKey in disease_keys and "family history" not in line and typeKey in disease_keys:
                        medical_history.add(term)
                        linkback[typeKey + ":" + term] = orig


    #Figure out how to split on sentences and redo the last if statement above 
    for line in emr_sentences:
        newlines =  line.count("\n")

        if newlines <=1:
            orig = line
            line = line.strip()
            line = line.decode('utf-8').replace('\xc2\xa0', u' ').replace(u'\xad', u'-').replace(u'\xe2', u"'")

            line = line.replace("\t", " ")

            #take out punctuation                                                                                                                                                                 
            line = line.replace("\n", "")
            line = line.replace("?", "")
            line = line.replace("!", "")
            line = line.replace("," , " ")
            line = line.lower()

            if "history" in line or "pmh" in line:
                for typeKey in type_dict:
                    val = type_dict[typeKey]
                    val = val.strip()
                    val = val.split(",")

                    #currently pulls the last line from the EMR that matches the pattern
                    for term in val:
                        if term in line and ("history" in line or "pmh" in line) and typeKey in disease_keys and "family history" not in line and typeKey in disease_keys:
                            medical_history.add(term)
                            linkback[typeKey + ":" + term] = orig

    #print medical_history
    return list(medical_history)
        


#returns all indices of substr in mainstr
def findAll(substr, mainstr):
    return [m.start() for m in re.finditer(substr, mainstr)]


#for each type: element pair we return the line in the document relevant to it (can alternatively embed this in ExtractType -- more efficient but less modular code)
def getLinkback(type_dict, emr, linkback, type, stopwords):
    emr = emr.decode('utf-8').replace('\xc2\xa0', ' ').replace(u'\xad', '-').replace(u'\xe2', "'")                                           

    if type == "text" or type == "xml":
        emr = emr.split("\n")
    else:
        emr = emr.split(",")

    acceptable_types = ["Disease or Syndrome", "Neoplastic Process", "Diagnostic Procedure", "Therapeutic or Preventive Procedure", "Finding", "Sign or Symptom", "Pharmacologic Substance", "Laboratory or Test Result"]

    for line in emr:
        tagged = False #this variable represents if the line contains a tagged term
        orig = line

        #take out punctuation     
        line = line.replace(".", "")
        line = line.replace("?", "")
        line = line.replace("!", "")
        line = line.replace(":", "")
        line = line.replace("," , " ")
        line = line.replace("-", " ")
        line = line.replace("(", "")
        line = line.replace(")", "")
        line = line.replace('"', '')

        #replace synonyms
        line = line.replace("nodules", "nodule")
        line = line.replace("obese", "obesity")
        line = line.replace("cataract", "cataracts")
        line = line.replace("tablets", "tablet")
        line = line.replace("medications", "medication")
        line = line.replace("vitamins", "vitamin")
        line = line.replace("cataractss", "cataracts")


        #line = replacePlurals(line)
        #line = CleanString(db, line, stopwords)


        line = line.lower()
        split_line = line.strip().split()

        for typeKey in type_dict:

            if typeKey in acceptable_types:
                val = type_dict[typeKey]
                val = val.strip()
                val = val.split(",")

                #currently pulls the last line from the EMR that matches the pattern
                for term in val:
                    if term in line and not((("no evidence of " + term) in line or ("did not show evidence for " + term) in line or ("no " + term) in line or ("negative for " + term) in line or (term + " r/o") in line or ("low probability for " + term) in line or ("hard to interpret as a sign for " + term) in line or "? no" in line or ":no" in line or ": no" in line or "father" in line or "mother" in line or "family history" in line)):
                        """
                        next_char_indexes = findAll(term, line)

                        for n in next_char_indexes:
                            next_char_index = n + len(term) #SEARCH THRU ALL INDICES NOT JUST FIRST ONE
                            prev_char_index = n - 1 if n-1 > 0 else 0

                            if (len(line) > next_char_index and line[next_char_index].isalpha() == False and line[prev_char_index].isalpha() == False) or (len(line) <= next_char_index and line[prev_char_index].isalpha() == False) or term == line.strip():
                                #linkback[typeKey + ":" + term] = orig
                                tagged = True
                        """

                        if len(term.strip().split()) > 1:
                            tagged = True
                        elif len(term.strip().split()) == 1 and term in split_line:
                            tagged = True


        if tagged == False and len(orig.strip()) > 0:
            linkback["Line " + str(emr.index(orig))] = orig
            #print "Line " + str(emr.index(orig)) + ": " + orig + "\n"



#populate database with claims data
def populateClaimsDatabase(db, store_db, emr, stopwords, patient_ID, event_ID, cost, physician_name, collectionName, recordType, language, languageDict):
    type_dict = dict()
    linkback = dict()
    emr = emr.replace(r'\r','') #get rid of windows carriage returns if they exist

    ExtractTypes(type_dict, db, emr, stopwords, linkback)
    getLinkback(type_dict, emr, linkback, type, stopwords)
    data = {}

    (dob, dates) = getDate(emr, type)
    hospital = getHospital(emr, type)
    smoker = isSmoker(emr, type)
    demographics = extractDemographic(emr)
    vitals = extractVitals(emr)
    hba1c = gethba1c(emr)
    (hdl, ldl) = getCholesterol(emr)
    body = getBody(emr)
    medical_history = getMedicalHistory(type_dict, emr, type, linkback)
    adverse_events = extractAdverseEvents(type_dict, emr, type, db)

    if 'Pharmacologic Substance' in type_dict:
        doses = getDosesDict(emr, type_dict['Pharmacologic Substance'])
    else:
        doses = dict()


    (icd9, icd10) = ExtractICDCodes(db, emr)

    #store the types
    for typeKey in type_dict:
        val = type_dict[typeKey]
        val = val.strip()
        val = val.split(",")
        data[typeKey] = val

    #store the dosage information
    for medication, med_type in doses.items():
        data[medication] = str(med_type)

    #store linkbacks
    for key in linkback:
        data[key] = linkback[key]

    
    data["date"] = dates
    data["physician"] = physician_name
    data["hospital"] = hospital
    data["dob"] = dob
    data["smoker"] = smoker
    data["age"] = demographics["age"]
    data["gender"] = demographics["gender"]
    data["ethnicity"] = demographics["ethnicity"]
    data["height"] = vitals["height"]
    data["weight"] = vitals["weight"]
    data["sys_bp"] = vitals["sys_bp"]
    data["dia_bp"] = vitals["dia_bp"]
    data["resp_rate"] = vitals["resp_rate"]
    data["heart_rate"] = vitals["heart_rate"]
    data["temperature"] = vitals["temperature"]
    data["temp_method"] = vitals["temp_method"]
    data["bp_method"] = vitals["bp_method"]
    data["bp_location"] = vitals["bp_location"]
    data["bp_position"] = vitals["bp_position"]
    data['icd9'] = icd9
    data['icd10'] = icd10
    data['hdl'] = float(hdl)
    data['ldl']  = float(ldl)
    data['hba1c'] = float(hba1c)
    data['patient_id'] = patient_ID
    data['event_id'] = event_ID
    data['cost'] = float(cost)
    data['medical history'] = medical_history
    data['adverse events'] = json.dumps(adverse_events)
    data['body'] = body
    data['recordType'] = recordType
    data['language'] = language
    data['languageDict'] = languageDict


    #store_db.rest2.insert(data) #collection is rest, db is called patients 
    store_db[collectionName].insert(data) #collection stores the collection name, db is called patients



#we populate our database with the inputted name, hospital, date, emr
def populateDatabase(db, store_db, emr, stopwords, patient_ID, event_ID, type, collectionName, recordType, language, languageDict):
    type_dict = dict()
    linkback = dict()
    emr = emr.replace(r'\r','') #get rid of windows carriage returns if they exist

    ExtractTypes(type_dict, db, emr, stopwords, linkback)
    getLinkback(type_dict, emr, linkback, type, stopwords)
    data = {}

    (dob, dates) = getDate(emr, type)
    physician = getPhysician(emr)
    hospital = getHospital(emr, type)
    smoker = isSmoker(emr, type)
    demographics = extractDemographic(emr)
    vitals = extractVitals(emr)
    hba1c = gethba1c(emr)
    (hdl, ldl) = getCholesterol(emr)
    body = getBody(emr)
    medical_history = getMedicalHistory(type_dict, emr, type, linkback)
    adverse_events = extractAdverseEvents(type_dict, emr, type, db)

    
    if 'Pharmacologic Substance' in type_dict:
        doses = getDosesDict(emr, type_dict['Pharmacologic Substance'])
    else:
        doses = dict()

    (icd9, icd10) = ExtractICDCodes(db, emr)

    #store the types
    for typeKey in type_dict:
        val = type_dict[typeKey]
        val = val.strip()
        val = val.split(",")
        data[typeKey] = val

        #store the date here so we can query date(Type: Element) > date
        for v in val:
            dateKey = "date(" + str(typeKey) + ":" + str(v) + ")"
            data[dateKey] = dates

    #store the dosage information
    for medication, med_type in doses.items():
        data[medication] = str(med_type)

    #store linkbacks
    for key in linkback:
        data[key] = linkback[key]


    data["date"] = dates
    data["physician"] = physician
    data["hospital"] = hospital
    data["dob"] = dob
    data["smoker"] = smoker
    data["age"] = demographics["age"]
    data["gender"] = demographics["gender"]
    data["ethnicity"] = demographics["ethnicity"]
    data["height"] = vitals["height"]
    data["weight"] = vitals["weight"]
    data["sys_bp"] = vitals["sys_bp"]
    data["dia_bp"] = vitals["dia_bp"]
    data["resp_rate"] = vitals["resp_rate"]
    data["heart_rate"] = vitals["heart_rate"]
    data["temperature"] = vitals["temperature"]
    data["temp_method"] = vitals["temp_method"]
    data["bp_method"] = vitals["bp_method"]
    data["bp_location"] = vitals["bp_location"]
    data["bp_position"] = vitals["bp_position"]
    data['icd9'] = icd9
    data['icd10'] = icd10
    data['hdl'] = float(hdl)
    data['ldl']  = float(ldl)
    data['hba1c'] = float(hba1c)
    data['patient_id'] = patient_ID
    data['event_id'] = event_ID
    data['medical history'] = medical_history
    data['adverse events'] = json.dumps(adverse_events)
    data['body'] = body
    data['recordType'] = recordType
    data['language'] = language
    data['languageDict'] = languageDict


    """
    print type_dict
    print "Date: ", dates #this is a datetime.datetime object
    print "Physician: ", physician
    print "Hospital: ", hospital
    print "Smoker: ", smoker
    print "Age: ", demographics["age"]
    print "Gender: ", demographics["gender"]
    print "Ethnicity: ", demographics["ethnicity"]
    print "Doses: ", doses
    print "ICD9: ", icd9
    print "ICD10: ", icd10
    print "Linkbacks: ", linkback
    print "Patient ID: ", patient_ID
    print "Event ID: ", event_ID

    if hba1c != -1:
        print "hba1c: ", hba1c

    if hdl != -1:
        print "hdl: ", hdl

    if ldl != -1:
        print "ldl: ", ldl
    """

    #store_db.rest2.insert(data) #collection is rest, db is called patients 
    store_db[collectionName].insert(data) #collection stores the collection name, db is called patients

#removes html tags                                                                                                                                                                               
def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)


#cleans the text and returns it                                                                                                                                                                  
def cleanText(body):
    body = remove_tags(body)
    body = unicode(body, 'utf-8')

    return body


if __name__ == '__main__':

    if len(sys.argv) < 10:
        print "Run as python insert.py [type] [patientID] [eventID] [emr] [delimiter] [collection] [record type] [language] [languageDict]"
        sys.exit(-1)


    type = sys.argv[1]
    patient_ID = sys.argv[2]
    event_ID = sys.argv[3]
    emr = sys.argv[4] 

    """
    #for inserting text files into the database
    emr_name = sys.argv[4]

    with open('/Users/gangopad/Company/EMR/Data/' + emr_name, 'r') as myfile:
        emr=myfile.read()
    """

    delimiter = sys.argv[5]
    collectionName = sys.argv[6]
    recordType = sys.argv[7]
    language = sys.argv[8]
    languageDict = sys.argv[9]

    client = MongoClient()
    db = client.umls
    store_db = client.patients
    num_events = len(event_ID.split(","))

    #get stopwords                                                                                                                                                                              
    with open("/Users/gangopad/Company/CysticFibrosis/CFSocialMedia/Dictionary/stopwords.pickle", "rb") as f:
        stopwords = pickle.load(f)


    if type == "text":

        """
        #TESTING
        with open ("/Users/gangopad/Company/RiskScores/Data/100-01.xml", "r") as myfile:
        #with open("/Users/gangopad/Company/REST/ApysAPI/TestData/json_example.json", "r") as myfile:
            emr=myfile.read()
        """


        #if the number of events is greater than 1 then split on appropriate delimiter
        if num_events == 1:
            #print emr + "\n\n\n"
            populateDatabase(db, store_db, emr, stopwords, patient_ID, event_ID, type, collectionName, recordType, language, languageDict)
        else:
            emr = emr.split(delimiter)
            patient_ID = patient_ID.split(",")
            event_ID = event_ID.split(",")
            index = 0

            for e in emr:
                #print e + "\n\n\n"
                populateDatabase(db, store_db, e, stopwords, patient_ID[index], event_ID[index], type, collectionName, recordType, language, languageDict)
                index = index + 1

    elif type == "json":

        """
        #TESTING
        with open("/Users/gangopad/Company/REST/ApysAPI/TestData/json_example2.json") as json_file:
            json_data = json.load(json_file)
        """ 

        #parse through json and get rid of the keys. Also replace all commas with a space

        #later change this to check if number of elements in json_data corresponds to number of records (may have to go a layer deeper if it doesnt ie if first layer is data: [
        #for emr in json_data:

        emr = json.loads(emr)

        if num_events == 1:
            emr =  json.dumps(emr, sort_keys = False)
            emr = json.dumps(emr, sort_keys = False)  
            emr = emr.replace ('"', '')
            emr = emr.replace('{', '')
            emr = emr.replace('}', '')
            emr = emr.replace('[', '')
            emr = emr.replace(']', '')
            emr = emr.replace('\\', '')
            #print emr + "\n\n\n"

            populateDatabase(db, store_db, emr, stopwords, patient_ID, event_ID, type, collectionName, recordType, language, languageDict)

        else:
            patient_ID = patient_ID.split(",")
            event_ID = event_ID.split(",")
            index = 0

            for e in emr:
                #if delimiter in e:
                if True:
                    emr = json.dumps(e, sort_keys = False)
                    emr = emr.replace ('"', '')
                    emr = emr.replace('{', '')
                    emr = emr.replace('}', '')
                    emr = emr.replace('[', '')
                    emr = emr.replace(']', '')
                    emr = emr.replace('\\', '')
                    #print emr + "\n\n\n"

                    populateDatabase(db, store_db, emr, stopwords, patient_ID[index], event_ID[index], type, collectionName, recordType, language, languageDict)
                    index = index + 1
    
    elif type == "xml":

        """
        #TESTING
        with open("/Users/gangopad/Company/REST/ApysAPI/TestData/xml_example.xml") as xml_file:
            emr = xml_file.read()
        """

         #if the number of events in the xml is greater than 1 then split on the appropriate tag 
        if num_events == 1:
            emr = cleanText(emr)
            #print emr + "\n\n\n"
            populateDatabase(db, store_db, emr, stopwords, patient_ID, event_ID, type, collectionName, recordType, language, languageDict)

        else:
            emr = emr.split(delimiter)
            patient_ID = patient_ID.split(",")
            event_ID = event_ID.split(",")
            index = 0

            for e in emr:
                e = cleanText(e)
                #print e + "\n\n\n"
                populateDatabase(db, store_db, e, stopwords, patient_ID[index], event_ID[index], type, collectionName, recordType, language, languageDict)
                index = index + 1


    elif type == "claims":
        #split emr by tab and assign manually to each entity (we dont do automatic integration of claims because we dont need to)
        emr = emr.split("\t")
        physician_name = emr[0]
        cost = emr[2]
        emr = emr[1]

        populateClaimsDatabase(db, store_db, emr, stopwords, patient_ID, event_ID, cost, physician_name, collectionName, recordType, language, languageDict)


    elif type == "table":
        
        if num_events == 1:
            populateDatabase(db, store_db, emr, stopwords, patient_ID, event_ID, type, collectionName, recordType, language, languageDict)
        else:
            emr = emr.split("\n")
            patient_ID = patient_ID.split(",")
            event_ID = event_ID.split(",")
            index = 0

            for e in emr:
                #print e + "\n\n\n"                                                                                                                                                                 
                populateDatabase(db, store_db, e, stopwords, patient_ID[index], event_ID[index], type, collectionName, recordType, language, languageDict)
                index = index + 1
