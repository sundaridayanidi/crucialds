import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""                                                                                                                                                                                                   
In this script we take as input the inclusion and exclusion criteria for the REST APi and return the 
query for mongodb. To be used as the constructQuery method for routes.js
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
from collections import deque


#returns a dictionary of synonyms for the given term
def getSynonyms(term, umls_db):
    synonyms = dict() #the key is the term, the value is the type
    cuis = set()
    type = ""

    res = umls_db.lower_mrconso.find({"TERM":term}, {"CUI": 1})

    for document in res:
        cui = document["CUI"]
        cuis.add(cui)


    for cui in cuis:
        res = umls_db.lower_mrsty.find({"CUI": cui}, {"TYPE": 1})
        type = ""

        for document in res:
            #pull the last type from the list unless the type is Disease or Syndrome or Pharmacologic Substance. These types are preferred since they are indexed
            if "Disease or Syndrome" not in type and "Pharmacologic Substance" not in type:
                type = document["TYPE"]

        res = umls_db.lower_mrconso.find({"CUI":cui}, {"TERM": 1})

        for document in res:
            term = document["TERM"]
            synonyms[term] = type


    return synonyms


#constructs the query for mongodb
def constructQuery(fields, inclusion, query_type, umls_db):
    fields = fields.split('_')
    inclusion = inclusion.split('_')

    new_fields = ""
    new_inclusion = ""
    boolean_operator = ""
    query =  'collection.find({'
    orig_inclusion = ""

    for f in fields:
        if "id" in f:
            new_fields = new_fields + "_" + f
        else:
            new_fields = new_fields + " " + f

    for inc in inclusion:
        if "id" in inc:
            new_inclusion = new_inclusion + "_" + inc
        else:
            new_inclusion = new_inclusion + " " + inc

    fields = new_fields[1:]
    inclusion = new_inclusion[1:]

    fields = fields.strip()
    
    if len(fields) > 0:
        fields = fields.split(",")

    if inclusion != "all":
        orig_inclusion = inclusion.strip()
        
        if query_type == "inclusion":
            boolean_operator = '"$and": ['
        else:
            boolean_operator = '"$or": ['

        if len(inclusion) > 0:
            query = query + boolean_operator
        else:
            query = query + '"None": "None"'

        inclusion = orig_inclusion.split(",")

        for arg in inclusion:
            if ">" in arg:
                arg = arg.split(">")
                
                if "date" in arg[0]:
                    query = query + '{"' + arg[0] + '": {"$gt": new Date("' + arg[1] + '")}},'
                else:
                    query = query + '{"' + arg[0] + '": {"$gt": ' + arg[1] + '}},'
            
            elif "<" in arg:
                arg = arg.split("<")

                if "date" in arg[0]:
                    query = query + '{"' + arg[0] + '": {"$lt": new Date("' + arg[1] + '")}},'
                else:
                    query = query + '{"' + arg[0] + '": {"$lt": ' + arg[1] + '}},'

            #INCLUDE ANOTHER ELIF HERE THAT CHECKS IF arg[0] IS ICD9 OR ICD10. IF SO LOWERCASE THE ARG[0]
            elif ":" in arg:
                arg = arg.split(":")
                
                if "date" in arg[0]:
                    query = query + '{"' + arg[0] + '": new Date("' + arg[1] + '")},'
                else:

                    synonyms = getSynonyms(arg[1], umls_db)

                    if len(synonyms) > 0:
                        query = query + '{"$or": ['

                        for term in synonyms:
                            query = query + '{"' + synonyms[term] + '": "' + term + '"},'


                        query = query + '{"' + arg[0] + '": "' + arg[1] + '"}'
                        query = query + ']},'

                    else:
                        query = query + '{"' + arg[0] + '": "' + arg[1] + '"},'


    if len(orig_inclusion) > 0 and inclusion != "all":
        query = query[:-1]
        query = query + ']},'
    else:
        query = query + '},'

    query = query + '{'

    if len(fields) > 0:
        for f in fields:
            query = query + '"' + f + '": 1,'

        query = query[:-1]


    query = query + '})'


    query = query + '.toArray(function(err, docs) {'
    #query = query + 'console.log("Found the following records in routes.js!");\n'
    query = query + 'callback(docs);'
    query = query + '});'


    return query



def convertToPN(expression):
    precedence = {}
    precedence["*"] = precedence["/"] = 3
    precedence["+"] = precedence["-"] = 2
    precedence[")"] = 1

    stack  = []
    result = deque([])
    for token in expression[::-1]:
        if token == ')':
            stack.append(token)
        elif token == '(':
            while stack:
                t = stack.pop()
                if t == ")": break
                result.appendleft(t)
        elif token not in precedence:
            result.appendleft(token)
        else:
            # XXX: associativity should be considered here
            # https://en.wikipedia.org/wiki/Operator_associativity
            while stack and precedence[stack[-1]] > precedence[token]:
                result.appendleft(stack.pop())
            stack.append(token)

    while stack:
        result.appendleft(stack.pop())

    return list(result)


#generate the expression here for converting to prefix
def generateExpression(inclusion):
    temp = inclusion.replace(" AND", "+")
    temp = temp.replace(" OR", "+")
    temp = temp.replace("(", "")
    temp = temp.replace(")", "")
    temp = temp.split("+")

    e_to_i_mapping = dict() #mapping from expression to inclusion                                                                                                                                        
    alphabet = list(string.ascii_lowercase) #list of the alphabet                                                                                                                                        
    expression = inclusion

    for i in range(len(temp)):
        e_to_i_mapping[alphabet[i]] = temp[i]
        expression = expression.replace(temp[i], alphabet[i])

    expression = expression.replace("AND", "*")
    expression = expression.replace("OR", "+")
    expression = expression.replace(" ", "")

    return expression, e_to_i_mapping

if __name__ == '__main__':
    
    if len(sys.argv) < 4:
        print "Run as python construct_query.py [fields] [inclusion] [query_type]"
        sys.exit(-1)

    
    client = MongoClient()
    umls_db = client.umls

    fields = sys.argv[1] 
    inclusion = sys.argv[2]
    query_type = sys.argv[3]

    (expression, e_to_i_mapping) = generateExpression(inclusion)
    PN_expression = convertToPN(expression)
    print "Normal: " + expression
    print "Prefix: " + str(PN_expression)


    for i in range(len(PN_expression)):
        term = PN_expression[i]
        if term == "*":
            PN_expression[i] = "AND"
        elif term == "+":
            PN_expression[i] = "OR"
        else:
            PN_expression[i] = e_to_i_mapping[term]

    print "Converted expression: " + str(PN_expression)

    #query = constructQuery(fields, inclusion, query_type, umls_db)

    #print query
    
    """
    #expression = "(a - b) / c * (d + e - f / g)".replace(" ", "")
    expression = "a + b * c".replace(" ", "")
    print "Normal: " + expression
    print "Prefix: " + str(convertToPN(expression))
    """
