#!/usr/bin/env python

"""
API that pulls patient data from PracticeFusion and inserts into recruitment app
"""

import re, urlparse
import os
import base64
import json
from sys import argv
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

class EMRScraper(object):
    def __init__(self):
        #self.driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1120, 550)



    def scrapePracticeFusion(self, link, patientStore):
    	self.driver.get(link)
    	wait = WebDriverWait(self.driver, 10)
    	email=wait.until(lambda driver: driver.find_element_by_id('inputUsername'))
    	email.clear()
    	email.send_keys('ag3202@columbia.edu')
    	self.driver.find_element_by_id("inputPswd").send_keys("Gangopad123")
    	self.driver.execute_script('document.getElementById("loginButton").click()')

    	send_call_button = wait.until(lambda driver: driver.find_element_by_id('sendCallButton'))
    	send_call_button.click()
    	code = raw_input("Enter verification code: ")  
    	code_input = wait.until(lambda driver: driver.find_element_by_id('code'))
    	code_input.send_keys(code)
    	self.driver.find_element_by_id('sendCodeButton').click()


    	#now we are logged in. Access charts
    	chart = wait.until(lambda driver: driver.find_element_by_link_text('Charts'))
    	chart.click()


    	patient_names = ["Brenda", "Eric"]


    	for name in patient_names:
    		#just picking up Brenda for now -- generalize to all patients in list
    		patients = wait.until(lambda driver: driver.find_elements_by_class_name('p-link'))

        	patient = [x for x in patients if name == x.text][0]

    		#html_patients = self.driver.page_source
    		#parsePatientList(html_patients)
    		patient.click()

    		self.scrapePatient(patientStore)
    		sendPatient(patientStore, str(patient_names.index(name)))
    		patient_page = wait.until(lambda driver: driver.find_element_by_xpath('//*[@data-tracking="Patient lists"]'))
    		patient_page.click()
    		time.sleep(3)

        
        self.driver.quit()



    #code for scraping individual patient record
    def scrapePatient(self, patientStore):
    	wait = WebDriverWait(self.driver, 10)
    	#Hardcoding demographics for now. Can always scrape later
        patientStore["first_name"] = "Brenda"
        patientStore["last_name"] = "DemoOncology"
        patientStore["email"] = "brenda@gmail.com"
        patientStore["ssn"] = "122-367-4859"
        patientStore["dob"] = "7/15/1951"
        patientStore["gender"] = "Female"
        patientStore["race"] = "White"
        patientStore["ethnicity"] = "Not Hispanic or Latino"
        patientStore["address"] = "1234 North Way"
        patientStore["zipcode"] = "12345"

        problems = []
        family_history = []
        medications = []
        allergies = []


        #scrape page
        #print "Diagnoses\n"
        diagnoses_store  = []
        diagnoses_date_store = []
    	diagnoses = wait.until(lambda driver: driver.find_elements_by_xpath('//*[@data-element="diagnosis-item-text"]'))
        for diagnosis in diagnoses:
            diagnoses_store.append(diagnosis.text)
            #print diagnosis.text

        #print "\n\n Diagnosis dates \n"

        diagnoses_dates = wait.until(lambda driver: driver.find_elements_by_xpath('//*[@data-element="diagnosis-item-start-date"]'))
        for diagnosis_date in diagnoses_dates:
            diagnoses_date_store.append(diagnosis_date.text)
            #print diagnosis_date.text

        #populate problems list
        for diagnosis in diagnoses_store:
            icd_code = diagnosis.split()[0]
            title = diagnosis.replace(icd_code, "").strip()

            icd_code = icd_code.replace("(", "")
            icd_code = icd_code.replace(")", "")

            diagnosis_date = diagnoses_date_store[diagnoses_store.index(diagnosis)]
            diagnosis_date = diagnosis_date + " 12:00"


            problem = {}
            problem["title"] = title
            problem["icd_version"] = "ICD-10"
            problem["icd10_code"] = icd_code
            problem["snomed_ct_code"] = "None"
            problem["status"] = "Active"
            problem["date_diagnosis"] = diagnosis_date
            problem["date_onset"] = diagnosis_date
            problem["date_changed"] = diagnosis_date
            problem["notes"] = "No Notes"
            problems.append(problem)




        #print "\n\n Family history \n"
        family_history_link = wait.until(lambda driver: driver.find_elements_by_xpath('//*[@data-element="Family health history"]'))
        for hist in family_history_link:
            #print hist.text #parse this

            
            member = {}
            member["relationship"] = "Father"
            member["first_name"] = "Unknown"
            member["last_name"] = "Unknown"
            member["age"] = "0"
            member["dob"] = "09/10/1916"
            member["gender"] = "Male"
            family_history.append(member)

            member = {}
            member["relationship"] = "Mother"
            member["first_name"] = "Unknown"
            member["last_name"] = "Unknown"
            member["age"] = "0"
            member["dob"] = "05/12/1916"
            member["gender"] = "Male"
            family_history.append(member)
            


        #print "\n\n Medications \n"
        medications_link = wait.until(lambda driver: driver.find_elements_by_xpath('//*[@data-element="medication-name"]'))
        for med in medications_link:
            #print med.text

            medication = {}
            medication["drug_name"] = med.text.split()[0]
            medication["sig_note"] = "No sig notes"
            medication["indication"] = "No indications entered"
            medication["status"] = "Active"
            medication["date_prescribed"] = "09/10/2016 22:00"
            medication["date_started_taking"] = "08/15/2012 22:00"
            medication["date_stopped_taking"] = "09/18/2016 22:00"
            medication["quantity"] = "20"
            medication["package"] = "tablet"
            medication["refills"] = "1"
            medication["pharmacy_notes"] = "No pharmacy notes to provide"
            medication["notes"] = "20 mg oral"
            medication["order_status"] = "Ordered"
            medications.append(medication)



        #print "\n\n Allergies \n"
        allergies_link = wait.until(lambda driver: driver.find_elements_by_xpath('//*[@data-element="allergy-item-text"]'))
        for allergy_link in allergies_link:
            #print allergy_link.text
            allergy = {}
            allergy["type"] = "Non-Drug allergy"
            allergy["description"] = allergy_link.text
            allergy["reaction"] = "Bloating/gas" #this we are populating manually -- need to scrape automatically
            allergy["status"] = "active"
            allergy["notes"] = "No notes to produce"
            allergies.append(allergy)

        description = ""

        #print "\n\n Clinical notes \n"
        notes = wait.until(lambda driver: driver.find_elements_by_xpath('//*[@class="link-text"]'))
        num_notes = len(notes)
        seen_indices = set()

        for i in range(num_notes):
            description = ""
            notes = wait.until(lambda driver: driver.find_elements_by_xpath('//*[@class="link-text"]'))
            note = notes[i]
            if "Encounter" in note.text and i not in seen_indices:
                seen_indices.add(i)

                note.click()
                descriptions = wait.until(lambda driver: driver.find_elements_by_xpath('//*[@class="display-text"]'))
                #chief_complaint = descriptions[0].text
                #description = descriptions[1].text

                for d in descriptions:
                    description = description + d.text + "\n\n"

                #print "\n\n Description \n"
                #print description

                #populate the free notes in SOAP as a problem -- need to figure out where they actually go in DrChrono
                problem = {}
                problem["title"] = "Encounter for observation"
                problem["icd_version"] = "ICD-10"
                problem["icd10_code"] = "Z03.89"
                problem["snomed_ct_code"] = "None"
                problem["status"] = "Active"
                problem["date_diagnosis"] = "09/10/2016 22:00"
                problem["date_onset"] = "09/11/2016 22:00"
                problem["date_changed"] = "09/05/2016 22:00"
                problem["notes"] = description
                problems.append(problem)

                self.driver.execute_script("window.history.go(-1)")
                time.sleep(3)



        patientStore["problems"]  = problems
        patientStore["medications"] = medications
        patientStore["family_history"] = family_history
        patientStore["allergies"] = allergies



#strips unicode and control characters from string
def strip_control_characters(input):
    if input:

        import re

        # unicode invalid characters
        RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                         u'|' + \
                         u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                          (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           )
        input = re.sub(RE_XML_ILLEGAL, "", input)

        # ascii control characters
        #input = re.sub(r"[\x01-\x1F\x7F]", "", input)

    return input



#sends the patient record to recruitment app
def sendPatient(patientStore, event_index):
    #populate insert here
    emr = ""
    problems = patientStore["problems"]
    medications = patientStore["medications"]
    family_history = patientStore["family_history"]
    allergies = patientStore["allergies"]

    url = "http://ec2-54-237-210-158.compute-1.amazonaws.com:3000/insert"
    body = dict()
        
    for problem in problems:
    	for element in problem:
            emr = emr + element + ": " + problem[element] + "\n\n"

    for medication in medications:
        for element in medication:
            emr = emr + element + ": " + medication[element] + "\n\n"

    for member in family_history:
    	for element in member:
            emr = emr + element + ": " + member[element] + "\n\n"

    for allergy in allergies:
    	for element in allergy:
            emr = emr + element + ": " + allergy[element] + "\n\n"

    emr = strip_control_characters(emr)

    body["emr"] = emr
    body["patientID"] = "Practice-Fusion"
    event_id = "Practice-Fusion-" + event_index
    body["eventID"] = event_id
    body["type"] = "text"
    body["delimiter"] = "none"

    fout = open("bs.txt", "wb")
    fout.write(emr.encode('utf-8'))
    fout.close()

    headers={'Content-Type': 'application/json'}
    payload = json.dumps(body)

    

    #post data to insert in backend
    r = requests.post(url, headers=headers, data=payload)



if __name__ == "__main__":
    practice_fusion_link = 'https://static.practicefusion.com/apps/ehr/index.html?#/login'
    patientStore = {} #we are only scraping one patient for now. Easily generalizable to multiple

    scraper = EMRScraper()
    scraper.scrapePracticeFusion(practice_fusion_link, patientStore)
    time.sleep(3)

    

