import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""                                                                                                                                                                                            
In this script we take in as input the keyword and EMR and return the PNG file and text blob corresponding to it as in accordance with PatientViewer
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


#recurses through the Nodes folder in REST/Data to get the appropriate filename
def getPNG(keyword, patientID):
    path = "/Users/gangopad/Company/REST/Data/Nodes/" + str(patientID)

    for filename in os.listdir(path): 
        with open(path + "/" + filename) as f:
            for line in f:
                line = line.strip()

                if keyword in line:
                    return filename

    return ""


def getText(keyword, patientID, fname):
    path = "/Users/gangopad/Company/REST/Data/Text/" + str(patientID)

    if fname != "":
        with open("/Users/gangopad/Company/REST/Data/Text/" + str(patientID) + "/" + fname) as f:
            data = f.read()

            data = data.lower()
            keyword = keyword.lower()

            if keyword in data:
                return fname
            else:
                for filename in os.listdir(path):
                    with open(path + "/" + filename) as f:
                        for line in f:
                            line = line.strip()

                            if keyword in line:
                                return filename

    return ""


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Run as python query.py [keyword] [patientID]"
        sys.exit(-1)

    keyword = sys.argv[1]
    patientID = sys.argv[2]

    #print keyword
    #print patientID

    if keyword == None or patientID == None:
        print "/Users/gangopad/Company/REST/Data/PNGs/file_not_found.png"
        print "/Users/gangopad/Company/REST/Data/Text/file_not_found"
        sys.exit(0);


    fname = getPNG(keyword, patientID)
    text_fname = getText(keyword, patientID, fname)


    if fname != "":
        print "/Users/gangopad/Company/REST/Data/PNGs/" + str(patientID) + "/" + fname + ".png"
    else:
        print "/Users/gangopad/Company/REST/Data/PNGs/file_not_found.png"

    if text_fname != "":
        print "/Users/gangopad/Company/REST/Data/Text/" + str(patientID) + "/" + text_fname
    else:
        print "/Users/gangopad/Company/REST/Data/Text/file_not_found"
