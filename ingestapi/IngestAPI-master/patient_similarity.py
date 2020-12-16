import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""                                                                                                                                                                                                   
In this script we take in as input the patient ID and type and return the community of patients and the type that characterizes the community 
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

#returns the file corresponding to the cluster to be returned
def getCluster(type, patientID):
    path = "/Users/gangopad/Company/ClinicalTrials/ClusterNodes/" + str(type)

    for filename in os.listdir(path):
        with open(path + "/" + filename) as f:
            for line in f:
                if patientID in line:
                    return filename

    return ""


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Run as python query.py [type] [patientID]"
        sys.exit(-1)

    type = sys.argv[1]
    patientID = sys.argv[2]

    type = type.replace('_', ' ');

    fname = getCluster(type, patientID)

    if fname != "":
        print "/Users/gangopad/Company/ClinicalTrials/Clusters/" + str(type) + "/" + fname[:-3] + "png"
        print "/Users/gangopad/Company/ClinicalTrials/TypeClusterPNGs/" + str(type) + "/" + fname + ".png"
    else:
        print "/Users/gangopad/Company/REST/Data/PNGs/file_not_found.png"
        print "/Users/gangopad/Company/REST/Data/PNGs/file_not_found.png"
