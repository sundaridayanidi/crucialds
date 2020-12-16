"""
API wrapper - connecting CRC app to Clinical Studio
"""

import os
import base64
import requests
import json
from datetime import datetime
from datetime import timedelta
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from sys import argv
import time
import cgi
import urlparse
from uuid import uuid4

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
urllib3.disable_warnings(urllib3.exceptions.SNIMissingWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



from urllib3.connection import UnverifiedHTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool
from google.cloud import translate


#mappings for each form - key is fld_name and value is value type
VITAL_SIGNS = {'vstemp': 'temperature', 'vshr': 'heart_rate', 'vssysbp': 'blood_pressure_sys', 'vswt': 'weight', 'vsdiabp': 'blood_pressure_dia', 'vsdt': 'date', 'vsnd': 'not_done', 'vstm': 'time', 'vsrr': 'respiratory_rate'}
MEDICAL_HISTORY = {'mhrf_05a_diet': 'diet', 'mhrf_06a': 'neuropathy_linkback', 'mhrf_03c_car': 'car', 'mhrf_04a': 'current_smoker', 'mhrf_07_desc': 'medical_history_other_description', 'mhrf_dt': 'date', 'mhrf_06c4': 'neuropathy_significant', 'mhrf_06c2_ot': 'neuropathy_other', 'mhrf_05a_oral': 'oral', 'mhrf_06c2_weak': 'neuropathy_weakness', 'mhrf_06b_unk': 'etiology unknown', 'mhrf_06c2_numb': 'neuropathy_numbness', 'mhrf_06c3': 'neuropathy_severity', 'mhrf_06c': 'neuropathy_residual', 'mhrf_03': 'atherosclerotic', 'mhrf_03a_cad': 'cad', 'mhrf_06c1ot': 'neuropathy_complaint', 'mhrf_06b_desc': 'etiology', 'mhrf_06c2_pain': 'neuropathy_pain', 'mhrf_07': 'medical_history_other', 'mhrf_01': 'hyperlipidemia', 'mhrf_05a_ins': 'insulin', 'mhrf_03b_pvd': 'pvd', 'mhrf_02': 'hypertension', 'mhrf_05': 'diabetes', 'mhrf_04': 'smoker', 'mhrf_06c2_pare': 'neuropathy_paresthesia', 'mhrf_06': 'neuropathy'}
PHYSICAL_EXAM = {'pe_temp': 'temperature', 'pe_htunit': 'height_unit', 'pe_ht': 'height', 'pe_wtunit': 'weight_unit', 'pe_bmi': 'bmi', 'pe_wt': 'weight', 'pe_dt': 'date', 'pe_temp_units': 'temperature_unit'}
PROCEDURE = {'proc_deploy': 'device deployed', 'proc_pulse_tim': 'pulse_time', 'proc_pulse_tib': 'posterior tibial', 'proc_comp_time_stop1': 'light pressure methods time stop 1', 'proc_hep_act': 'act_secs', 'proc_pulse_ped_nd': 'dorsalis_pedis_not_done', 'proc_pulse_ped': 'dorsalis pedis', 'proc_hep_na': 'heparin_na', 'proc_target_perip_sp': 'peripheral_specify', 'proc_comp_time_start1': 'light pressure methods time start 1', 'proc_comp_time_start2': 'light pressure methods time start 2', 'proc_sheath_size': 'sheath_size', 'proc_branch': 'branch', 'proc_comp_time_stop2': 'light pressure methods time stop 2', 'proc_ae': 'procedure_ae', 'proc_target_oth_sp': 'other_specify', 'proc_comp': 'light pressure methods', 'proc_act_nd': 'act_not_done', 'proc_pulse_tib_nd': 'posterior_tibial_not_done', 'proc_bp_dias': 'dias_bp', 'proc_bp_sys': 'sys_bp', 'proc_loc': 'location', 'proc_multi_kit': 'more_than_one_kit', 'proc_multi_kit_desc': 'more_than_one_kit_description', 'proc_target': 'procedure_target', 'proc_comp_date1': 'light pressure methods date 1', 'proc_comp_date2': 'light pressure methods date 2', 'proc_comp2_na': 'light pressure methods not taken', 'proc_type': 'procedure_type', 'proc_bp_tim': 'bp_time', 'proc_pulse_nd': 'pulse_not_taken', 'proc_dt': 'date', 'proc_hep_act_tim': 'act_time_drawn', 'proc_print': 'recorded_and_printed', 'proc_deploy_desc': 'device deployed description'}
CONMED = {'cmdosfrq': 'frequency', 'cmmhno': 'medical history id', 'cmdstxt': 'dosage', 'cmaeno': 'adverse event id', 'cmstdat': 'start date', 'cmongo': 'ongoing', 'cmdosu': 'dose_unit', 'cmendat': 'end date', 'indication': 'indication', 'cmdosfrm': 'form', 'cmroute': 'route', 'cmtrt': 'name'}
DEMOGRAPHY = {'dem_dt': 'date', 'dem_birthdat': 'dob', 'dem_age':'age', 'dem_sex': 'sex', 'dem_race': 'race', 'dem_raceoth': 'race_other'}
ADVERSE_EVENTS = {'aespid': 'ae_number', 'aeterm': 'adverse_event', 'aestdat' : 'start_date', 'aeongo': 'ongoing', 'aeendat': 'end_date', 'aesev': 'severity', 'aeser' : 'serious', 'aerel' : 'related_treatment', 'aeacn' : 'action_taken', 'aeacnoth' : 'other_action_taken', 'aeout' : 'outcome', 'ae_code' : 'meddra_code'}
LOG_MEDICAL_HISTORY = {'mhdov': 'date', 'mhny': 'has_medical_history', 'mhname': 'event_name', 'mhstdt': 'start_date', 'mhenddt': 'end_date', 'mhong': 'ongoing'}
LOG_DEMOGRAPHICS = {'birthdt': 'dob', 'age': 'age', 'gender': 'gender', 'ethnic' : 'ethnicity', 'race' : 'race', 'raceoth': 'race_other', 'city': 'city', 'state' : 'state', 'country' : 'country', 'form_field_4': 'smoker'}
LOG_ADVERSE_EVENTS = {'ae_code': 'meddra_code', 'aestdt': 'start_date', 'aesttm': 'ae_start_time', 'aesttmunk': 'unknown_start_time', 'aespdt': 'ae_stop_date', 'aesptm': 'ae_stop_time', 'aesptmunk': 'ae_stop_time_unknown', 'aealtcprex': 'alternate_causality_preexisting', 'aealtclntil': 'alternate_causality_intercurrent_illness', 'aealtccm': 'alternate_causality_conmed', 'aealtccmsp': 'alternate_causality_conmed_specify', 'aealtcoth': 'alternate_causality_other', 'aealtcothsp': 'alternate_causality_other_specify', 'acn': 'action_taken', 'aetrtny': 'treatment_given', 'out': 'outcome'}


#global variables for subject id and visit number
VISIT_NO_VAR = "Baseline"
SUBJECT_ID_VAR = "100-001"
SITE = "Gangopadhy"
VISIT_TYPE = "Scheduled"



CREDENTIALS = dict() #key is the trial ID and username. values are the password, visit_no_var, subject_id_var, site, visit_type
TOKEN_CREDENTIALS = dict() #key is the token and values are username, password, token time, 

CLINICAL_STUDIO_USERNAME = "paul.grady@clsds.com"
CLINICAL_STUDIO_PASSWORD = "grs2mgV$(dR$3+@K"



class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        parsed_path = urlparse.urlparse(self.path)

        query = str(parsed_path.query)

        if "token" in query:
            token = query.replace("token=", "").strip()
            (response_token, message) = authorizeToken(token)
            print "MESSAGE: " + message
            self.send_response(response_token)
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)

        elif "populate" in query:
            populateCohort()
            self.wfile.write("<html><body><h1>" + str(parsed_path.query) + "</h1></body></html>")





    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data                                    
        post_data = self.rfile.read(content_length) # <--- Gets the data itself     
        content_type = self.headers['Content-Type']

        if "multipart" in content_type:
        	boundary = content_type.strip(";").split()
        	boundary = boundary[1].strip().split("=")
        	boundary = boundary[1].strip()
        	parseData(post_data, boundary)
        	

        elif "text/plain" in content_type:
        	write(post_data)

        elif 'Authorization' in self.headers:
            auth = self.headers['Authorization']
            (response_token, message) = authorizeClient(auth, post_data)
            print "MESSAGE: " + message
            self.send_response(response_token)
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)


       	#self._set_headers()
       	#self.send_response(200)
        #self.wfile.write("<html><body><h1>POST!</h1></body></html>")



    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', self.headers.dict['origin'])
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")

        #print self.headers
        #content_length = int(self.headers['Content-Length']) # <--- Gets the size of data                                                    
        #post_data = self.rfile.read(content_length) # <--- Gets the data itself                                                              
        #parseData(post_data)



#authorizes the token and responds to GET request
def authorizeToken(token):
    time = datetime.now()
    global TOKEN_CREDENTIALS
    credential_data = TOKEN_CREDENTIALS[token]

    token_time = credential_data["token_time"]
    username = credential_data["username"]
    trial_id = credential_data["trial_id"]
    client_token = credential_data["client_token"]
    token_time = credential_data["token_time"]
    role =  credential_data["role"]
    password = credential_data["password"]

    time_delta = time - token_time
    time_delta = time_delta.seconds

    print "Token: " + token
    print "Client token: " + str(client_token)
    print "TIME DELTA: " + str(time_delta)

    if time_delta > 30 or str(token) != str(client_token):
        message = {"Username" : "Error"}
        message = json.dumps(message)
        response_token = 401
    else:

        #pull the site name
        sites = getSites("OAUTH2_" + username, password)
        visit_types = getVisitType("OAUTH2_" + username, password)

        message = {"Username" : username, "TrialID": trial_id, "Role": role, "Site": sites, "VisitType": visit_types}
        message = json.dumps(message)
        response_token = 200
        TOKEN_CREDENTIALS.pop(token)

    return response_token, message



#checks auth to see if they match valid username/password
def authorizeClient(auth, data):
    global CLINICAL_STUDIO_USERNAME
    global CLINICAL_STUDIO_PASSWORD
    global TOKEN_CREDENTIALS
    global CREDENTIALS

    response_token = 401
    message = {"Token" : "None"}
    message = json.dumps(message)
    data = json.loads(data)

    client_auth = CLINICAL_STUDIO_USERNAME + ":" + CLINICAL_STUDIO_PASSWORD
    client_auth = 'Basic ' + base64.b64encode(bytes(client_auth), 'utf-8')

    if auth != client_auth:
        return response_token, message
    else:
        response_token = 200
        rand_token = uuid4()
        message = {"Token" : str(rand_token)}
        message = json.dumps(message)
        username = data["email"]
        trial_id = data["trialID"]
        role = data["roleType"]

        password = data["token"]
        client_token = rand_token
        token_time =  datetime.now()

        credential_data = {}
        credential_data["username"] = username
        credential_data["trial_id"] = trial_id
        credential_data["password"] = password
        credential_data["role"] = role
        credential_data["client_token"] = client_token
        credential_data["token_time"] = token_time

        addUser(username, trial_id, role)

        TOKEN_CREDENTIALS[str(client_token)] = credential_data
        CREDENTIALS[username] = credential_data


        return response_token, message




"""
######DEPRECATED#####
#pulls the credentials and sets the global variables accordingly (deprecated -- use authorizeClient instead)
"""
def getCredentials(token):
    global USERNAME
    global PASSWORD
    
    url = "https://webapi.clinicalstudio.com/api/user/18"
    authstring = "anirban@zircontechnologies.com:Gangopad123"
    authstring = 'Basic ' + base64.b64encode(bytes(authstring), 'utf-8')
    headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Accept-Language': 'en', 'Authorization': authstring, 'User-Agent': 'api/1.0'}
    credentials = dict()

    credentials["email"] = username
    payload = json.dumps(credentials)

    r = requests.post(url, data=payload, headers=headers)
    print r.status_code
    print r.text
    body = json.loads(r.text)

    USERNAME = username
    PASSWORD = body["token"]



#checks if user exists. If not adds to database
def addUser(username, trial_id, role):
    #url = "http://demo.zircontechnologies.com:3000/addUser"                                                         
    url = "http://localhost:3000/addUser"
    body = dict()
    auth_username = "paul.grady@clsds.com"
    auth_password = "grs2mgV$(dR$3+@K"

    client_auth = auth_username + ":" + auth_password
    client_auth = 'Basic ' + base64.b64encode(bytes(client_auth), 'utf-8')
    headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': client_auth}

    body["username"] = username
    body["role"] = role
    body["trialID"] = str(trial_id)

    payload = json.dumps(body)

    #post data to insert in backend                                                                                  
    r = requests.post(url, headers=headers, data=payload)
    print r.status_code



#populates the given form 
def populateForm(url, headers, form_id, level_id, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list):
    routing_type = "7"
    url = str(url) + "/form/" + routing_type
    new_form = dict()
    new_form["form_id"] = str(form_id)
    new_form["level_id"] = str(level_id)
    new_form["pk_id"] = str(form_data_primary_key)
    new_form["int_id"] = str(visit_interval_primary_key)
    new_form["ver_id"] = str(form_version_id)
    new_form["sub_id"] = str(subject_primary_key)
    new_form["sub_profile_id"] = subject_id.replace('"', '')
    new_form["vee_id"] = str(vee_id)
    new_form["latitude"] = str(latitude)
    new_form["longitude"] = str(longitude)
    new_form["table_rows_list"] = table_rows_list
	

    """
	#FUZZY MAPPING STUFF -- PUT IN MAP methods
    form = json.loads(form)
    values = form["field_value_list"] #populate the values here and read to form json
    form_data = form["form_data"]
    pages = form_data["pages"]

    for page in pages:
        objects = page["objects"] #we can get fldname and fldid for each relevant field from here

    for fields in values:
        if fields["fld_name"] == "vsdiabp":
            old_fields = fields
	    fields["fld_value"] = "98"
	    fields["fld_value_decode"] = "98"
	    
	    values[values.index(old_fields)] = fields
	"""

    new_form["field_value_list"] = field_value_list

    payload = json.dumps(new_form)
    print payload

    #print payload
    r = requests.post(url, data=payload, headers=headers)
    print r.status_code
    print r.text



#returns for each subject ID the list of forms to be completed
def getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key):
    url = str(url) + "/form/" + str(routing_type) + "/" + str(level) + "/" + str(form_id) + "/" + str(form_data_primary_key) + "/" + str(visit_interval_primary_key) + "/" + str(form_version_id) + "/" + str(requesting_device_type) + "/" + str(subject_primary_key)
    print url
    r = requests.get(url, headers=headers)
    form = r.text

    return form


#returns primary key of the subject
def getSubjectPrimaryKey(url, headers, subject_id, site):
    url = str(url) + "/subject/1"  
    r = requests.get(url, headers=headers)
    body = json.loads(r.text)

    for subject in body["sub_registration"]:
        if subject_id == subject["sub_profile_id"] and site == subject["sub_site_txt"]:
            return subject["sub_id"]



#gets the visit type
def getVisitType(username, token):
    url = "https://webapi.clinicalstudio.com/api/visit/1/-1"
    authstring = username + ":" + token
    #authstring = "anirban@mekhoshealth.com:Gangopad123"
    authstring = 'Basic ' + base64.b64encode(bytes(authstring), 'utf-8')
    headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Accept-Language': 'en', 'Authorization': authstring, 'User-Agent': 'api/1.0'}
    visit_types = ""

    r = requests.get(url, headers=headers)
    body = json.loads(r.text)

    for visit in body["int_list"]:
        visit_types  = visit_types + visit["int_name"] + ";-/"

    visit_types = visit_types[:-3]

    return visit_types


#gets the site given username, password
def getSites(username, token):
    url = "https://webapi.clinicalstudio.com/api/site/2"
    authstring = username + ":" + token
    #authstring = "anirban@mekhoshealth.com:Gangopad123"
    authstring = 'Basic ' + base64.b64encode(bytes(authstring), 'utf-8')
    headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Accept-Language': 'en', 'Authorization': authstring, 'User-Agent': 'api/1.0'}
    sites = ""

    r = requests.get(url, headers=headers)
    body = json.loads(r.text)

    for site in body["site_list"]:
        sites  = sites + site["site_name"] + ";-/"

    sites = sites[:-3]

    return sites


#pulls the site ID for the given site name
def getSiteID(url, headers, site_name):
    url = str(url) + "/site/1"  
    r = requests.get(url, headers=headers)
    body = json.loads(r.text)

    for site in body["study_sites"]:
        if site_name == site["site_name"]:
            return site["site_id"]




#authenticates and gets user description
def authenticate(url, headers):
    url = str(url) + "/user"
    r = requests.get(url, headers=headers)
    print r.text




#maps and submits elements from demographics
def mapDemographics(data, date, time, form):
    global DEMOGRAPHY
    form = json.loads(form)
    values = form["field_value_list"] #populate the values here and read to form json
    table_rows_list = []
    race_options = {"american indian": "1", "alaska native": "1", "asian": "2", "black": "3", "african american": "3", "white": "4", "other": "5"}

    age = data["age"]
    sex = "1" if data["sex"] == "male" else "2"
    race = race_options[data["race"]] if data["race"] in race_options else "5"
    race_other = data["race"] if race == "5" else "unknown"
    dob = data["dob"]

    if dob != "" and "-" not in dob:
        d = datetime.strptime(dob, '%b %d %Y')
        dob = d.strftime('%Y-%m-%d')


    #dob = datetime.utcnow() - timedelta(days=(int(age) * 365))
    #dob = dob.strftime("%Y-%m-%dT%H:%M:%S")

    demography_values = {"date": date, "dob": dob, "age": age, "sex": sex, "race": race, "race_other": race_other}

    for fields in values:
        if fields["fld_name"] in DEMOGRAPHY:
            old_fields = fields
            fields["fld_value"] = demography_values[DEMOGRAPHY[fields["fld_name"]]]
            #fields["fld_value_decode"] = vital_signs_values[MEDICAL_HISTORY[fields["fld_name"]]]
            values[values.index(old_fields)] = fields

    return values, table_rows_list



#maps and submits elements from physical exam
def mapPhysicalExam(data, date, time, form):
    global PHYSICAL_EXAM
    physical_exam_values = {"date": date, "weight": "200", "weight_unit": "2", "height": "60", "height_unit": "2", "bmi": "20", "temperature": "99", "temperature_unit": "2"}
    form = json.loads(form)
    values = form["field_value_list"] #populate the values here and read to form json
    table_rows_list = []
    
    for fields in values:
        if fields["fld_name"] in PHYSICAL_EXAM:
            old_fields = fields
            fields["fld_value"] = physical_exam_values[PHYSICAL_EXAM[fields["fld_name"]]]
            #fields["fld_value_decode"] = vital_signs_values[MEDICAL_HISTORY[fields["fld_name"]]]
            values[values.index(old_fields)] = fields

    return values, table_rows_list



#maps and submits elements from medical history
def mapMedicalHistory(data, date, time, smoker, conmeds, form):
    global MEDICAL_HISTORY
    form = json.loads(form)
    values = form["field_value_list"] #populate the values here and read to form json
    table_rows_list = []
    diseases = set()
    meds = set()
    neuropathy_linkback = "none"
    
    for c in conmeds:
        meds.add(c["Medication/Non-drug therapy"])

    for d in data:
        disease = d["Diagnosis/Condition/Surgery"]
        diseases.add(disease)
        
        if "neuropathy" in disease:
            neuropathy_linkback = d["Linkback"]

    hyperlipidemia = "1" if "hyperlipidemia" in diseases else "2"
    hypertension = "1" if "hypertension" in diseases else "2"
    atherosclerotic = "1" if "cad" in diseases or "myocardial infarction" in diseases or "pvd" in diseases or "carotid" in diseases else "2"
    cad = "1" if "cad" in diseases else "2"
    pvd = "1" if "pvd" in diseases else "2"
    carotid = "1" if "carotid" in diseases else "2"
    smoker = "1" if smoker == "True" else "2"
    diabetes = "1" if "diabetes" in diseases or "dm" in diseases or "diabetes mellitus" in diseases else "2"
    insulin = "1" if "insulin" in meds else "2"
    oral = "1" if "amaryl" in meds or "metformin" in meds else "2"
    neuropathy = "1" if "neuropathy" in diseases else "2"
    etiology_unknown = "2" if neuropathy_linkback == "none" else "1"
    neuropathy_paresthesia = "1" if "paresthesia" in diseases else "2"
    neuropathy_weakness = "2" if neuropathy == "2" else "1"
    neuropathy_pain = "2" if neuropathy == "2" else "1"
    neuropathy_numbness = "2" if neuropathy == "2" else "1"
    neuropathy_other = "2"
    neuropathy_severity = "1" 
    neuropathy_significant = "1"
    neuropathy_residual = "2" if neuropathy == "2" else "1"
    medical_history_other_description = ','.join(map(str, diseases))


    medical_history_values = {"date": date, "hyperlipidemia": hyperlipidemia, "hypertension": hypertension, "atherosclerotic": atherosclerotic, "cad": cad, "pvd": pvd, "car": carotid, "smoker": smoker, "current_smoker": smoker, "diabetes": diabetes, "insulin": insulin, "diet": "1", "oral": oral, "neuropathy": neuropathy, "neuropathy_linkback": neuropathy_linkback, "etiology": neuropathy_linkback, "etiology unknown": etiology_unknown, "neuropathy_residual": neuropathy_residual, "neuropathy_paresthesia": neuropathy_paresthesia, "neuropathy_weakness": neuropathy_weakness, "neuropathy_pain": neuropathy_pain, "neuropathy_numbness": neuropathy_numbness, "neuropathy_other": neuropathy_other, "neuropathy_severity": neuropathy_severity, "neuropathy_significant": neuropathy_significant, "medical_history_other": "1", "medical_history_other_description": medical_history_other_description, "neuropathy_complaint": "1"}

    
    for fields in values:
        if fields["fld_name"] in MEDICAL_HISTORY:
            old_fields = fields
            fields["fld_value"] = medical_history_values[MEDICAL_HISTORY[fields["fld_name"]]]
            fields["fld_value_decode"] = ""
            #fields["fld_value_decode"] = vital_signs_values[MEDICAL_HISTORY[fields["fld_name"]]]
            values[values.index(old_fields)] = fields
        
        """
        #TESTING
        if fields["fld_name"] == "mhrf_02":
            old_fields = fields
            fields["fld_value"] = "2"
            fields["fld_value_decode"] = ""
            values[values.index(old_fields)] = fields

		"""
    return values, table_rows_list


#maps elements for log medical history
def mapLogMedicalHistory(d, date, time, form):
    global LOG_MEDICAL_HISTORY
    form = json.loads(form)
    values = form["field_value_list"] #populate the values here and read to form json
    table_rows_list = []

    start_date = d["Start Date"]
    end_date = d["End Date"]

    sdate = start_date.split()

    if len(sdate) > 3:
        sdate = sdate[1] + " " + sdate[2] + " " + sdate[3]
        d = datetime.strptime(sdate, '%b %d %Y')
        start_date = d.strftime('%m-%d-%Y')

    edate = start_date.split()

    if len(edate) > 3:
        edate = edate[1] + " " + edate[2] + " " + edate[3]
        d = datetime.strptime(edate, '%b %d %Y')
        end_date = d.strftime('%m-%d-%Y')


    #PULL FIELDS FROM D INTO VARIABLES SPECIFIED IN BELOW DICT

    medical_history_values = {"start date": start_date, "end date": end_date, "date": date, "has_medical_history": has_medical_history, "event_name": disease, "ongoing": ongoing} #FINISH THIS

    for fields in values:
        if fields["fld_name"] in CONMED:
            old_fields = fields
            fields["fld_value"] = medical_history_values[CONMED[fields["fld_name"]]]
            fields["fld_value_decode"] = ""
            values[values.index(old_fields)] = fields


    return values, table_rows_list


#maps and submits elements from conmed
def mapConcomitantMedication(d, date, time, form):
    global CONMED
    form = json.loads(form)
    values = form["field_value_list"] #populate the values here and read to form json
    table_rows_list = []
    name = d["Medication/Non-drug therapy"]
    indication = d["Linkback"]
    dosage = str(d["Dose (per admin)"]) if "Dose (per admin)" in d else "N/A"
    start_date = d["Start Date"]

    sdate = start_date.split()

    if len(sdate) > 3:
    	sdate = sdate[1] + " " + sdate[2] + " " + sdate[3]
    	d = datetime.strptime(sdate, '%b %d %Y')
    	start_date = d.strftime('%m-%d-%Y')

    conmed_values = {"name": name, "indication": indication, "adverse event id": "0", "medical history id": "0", "dosage": dosage, "dose_unit": "2", "form": "6", "frequency": "2", "route": "5", "start date": start_date, "end date": date, "ongoing": "1"}

    for fields in values:
        if fields["fld_name"] in CONMED:
            old_fields = fields
            fields["fld_value"] = conmed_values[CONMED[fields["fld_name"]]]
            fields["fld_value_decode"] = ""
            values[values.index(old_fields)] = fields


    return values, table_rows_list


#maps and submits elements from AE
def mapAdverseEvents(d, date, time, form, index):
    global CONMED
    form = json.loads(form)
    values = form["field_value_list"] #populate the values here and read to form json
    table_rows_list = []
    adverse_event = d["Adverse Event"]
    start_date = d["Start Date"]
    end_date = d["End Date"]

    sdate = start_date.split()

    if len(sdate) > 3:
        sdate = sdate[1] + " " + sdate[2] + " " + sdate[3]
        d = datetime.strptime(sdate, '%b %d %Y')
        start_date = d.strftime('%m-%d-%Y')


    ae_values = {'ae_number': index, 'adverse_event' : adverse_event, 'start_date': start_date, 'ongoing' : '1', 'end_date': end_date, 'severity': '1', 'serious' : '1', 'related_treatment' : '1', 'action_taken' : '1', 'other_action_taken' : 'N/A', 'outcome' : '3', 'ae_code': ''}

    for fields in values:
        if fields["fld_name"] in ADVERSE_EVENTS:
            old_fields = fields
            fields["fld_value"] = ae_values[ADVERSE_EVENTS[fields["fld_name"]]]
            fields["fld_value_decode"] = ""
            values[values.index(old_fields)] = fields


    return values, table_rows_list




#maps and returns elements from vital signs
def mapVitalSigns(data, date, time, form):
    global VITAL_SIGNS
    data = data[0] #change this if data changes from list to dict

    vital_signs_values = {"date": date, "time": time, "blood_pressure_sys": data["sys_bp"], "blood_pressure_dia": data["dia_bp"], "heart_rate": data["heart_rate"], "respiratory_rate": data["resp_rate"], "temperature": data["temperature"], "weight": data["weight"], "not_done": "0"}
    form = json.loads(form)
    values = form["field_value_list"] #populate the values here and read to form json
    table_rows_list = []


    for fields in values:
        if fields["fld_name"] in VITAL_SIGNS:
            old_fields = fields
            fields["fld_value"] = vital_signs_values[VITAL_SIGNS[fields["fld_name"]]]
            #fields["fld_value_decode"] = vital_signs_values[VITAL_SIGNS[fields["fld_name"]]]
            values[values.index(old_fields)] = fields

    return values, table_rows_list


#populates medical history log forms
def populateLogMedicalHistory(url, headers, routing_type, level, form_version_id, subject_primary_key, requesting_device_type, subject_id, latitude, longitude, response):
    form_data_primary_key = "-1"
    visit_interval_primary_key = "-1"
    vee_id = "-1"
    form_id = "-1"

    response = json.loads(response)
    data_type = response["type"]
    data = response["data"]
    date = response["date"]
    time = response["time"]

    if "Unknown" in date:
        date = ""
    else:
        date = date.split()
        date = date[1] + " " + date[2] + " " + date[3]
        d = datetime.strptime(date, '%b %d %Y')
        date = d.strftime('%m-%d-%Y')


    form_url = str(url) + "/form/1/" + str(subject_primary_key)

    r = requests.get(form_url, headers=headers)
    body = json.loads(r.text)

    for form in body["form_list"]:
        if form["form_name"] == "Medical / Surgical History":
            form_id = form["form_id"]


    for medical_history in data:
        form = getForm(url, headers, routing_type, level_id, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
        (field_value_list, table_rows_list) = mapLogMedicalHistory(medical_history, date, time, form) 
        populateForm(url, headers, form_id, level_id, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
        


#populates the conmed log forms
def populateConcomitantMedication(url, headers, routing_type, level_id, form_version_id, subject_primary_key, requesting_device_type, subject_id, latitude, longitude, response):
    form_data_primary_key = "-1"
    visit_interval_primary_key = "-1"
    vee_id = "-1"
    form_id = "-1"

    response = json.loads(response)
    data_type = response["type"]
    data = response["data"]
    date = response["date"]
    time = response["time"]

    if "Unknown" in date:
        date = ""
    else:
        date = date.split()
        date = date[1] + " " + date[2] + " " + date[3]
        d = datetime.strptime(date, '%b %d %Y')
        date = d.strftime('%m-%d-%Y')


    form_url = str(url) + "/form/1/" + str(subject_primary_key)

    r = requests.get(form_url, headers=headers)
    body = json.loads(r.text)

    for form in body["form_list"]:
    	if form["form_name"] == "Concomitant Medication" or form["form_name"] == "Medications":
    		form_id = form["form_id"]



    for med in data:
        form = getForm(url, headers, routing_type, level_id, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
        (field_value_list, table_rows_list) = mapConcomitantMedication(med, date, time, form) 
        populateForm(url, headers, form_id, level_id, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    			


#populates the AE log forms
def populateAdverseEvents(url, headers, routing_type, level_id, form_version_id, subject_primary_key, requesting_device_type, subject_id, latitude, longitude, response):
    form_data_primary_key = "-1"
    visit_interval_primary_key = "-1"
    vee_id = "-1"
    form_id = "-1"

    response = json.loads(response)
    data_type = response["type"]
    data = response["data"]
    date = response["date"]
    time = response["time"]
    index = 0

    if "Unknown" in date:
        date = ""
    else:
        date = date.split()
        date = date[1] + " " + date[2] + " " + date[3]
        d = datetime.strptime(date, '%b %d %Y')
        date = d.strftime('%m-%d-%Y')


    form_url = str(url) + "/form/1/" + str(subject_primary_key)
    r = requests.get(form_url, headers=headers)
    body = json.loads(r.text)

    for form in body["form_list"]:
        if form["form_name"] == "Adverse Event":
            form_id = form["form_id"]

    for ae in data:
        form = getForm(url, headers, routing_type, level_id, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
        (field_value_list, table_rows_list) = mapAdverseEvents(ae, date, time, form, index) 
        populateForm(url, headers, form_id, level_id, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
        index = index + 1


#pulls last line in the string
def getLastLine(element):
	"""
	for last in (line for line in element.split("\n") if line.rstrip('\n')):
   		pass
   	"""

   	element = element.split("\n")
   	return element[-2].strip()



#this returns the EMR in HTML readable format
def getBody(emr):
    emr = emr.replace("&", "&amp;")
    emr = emr.replace("<", "&lt;")
    emr = emr.replace(">", "&gt;")
    emr = emr.replace('"', "&quot;")
    emr = "<p>" + emr + "</p>"
    emr = emr.replace("\n", "<br>")

    return emr


#translates using API
def translateEMR(body, language):
    HTTPSConnectionPool.ConnectionCls = UnverifiedHTTPSConnection
    translate_client = translate.Client()
    emr = ""
    languageDict = {}
    languageDict["original"] = getBody(body)
    body = body.split("\n")


    for line in body:
        text = line.strip()
        result = translate_client.translate(text, target_language="en", source_language=language)
        
        emr = emr + result['translatedText'].encode('utf-8') + "\n"
        languageDict[result['translatedText'].encode('utf-8')] = text




    return emr, languageDict



#parse data and pull out payload
def parseData(data, boundary):
    data = data.split(boundary)
    languageMap = {"en" : "English", "es" : "Spanish", "sv": "Swedish", "fr": "French"}
    name = ""
    visit_type = ""
    site = ""
    visit_number = ""
    notes = ""
    emr = ""
    emr_type = ""
    language = ""
    username = ""
    trialID = ""
    languageDict = {}

    for element in data:
        if 'name="name"' in element:
            name = getLastLine(element)
        elif 'name="visit_type"' in element:
            visit_type = getLastLine(element)
        elif 'name="site"' in element:
            site = getLastLine(element)
        elif 'name="type"' in element:
            emr_type = getLastLine(element)
        elif 'name="visit"' in element:
            visit_number = getLastLine(element)
        elif 'name="notes"' in element:
            notes = getLastLine(element)
        elif 'name="file"' in element:
            emr = element
        elif 'name="language"' in element:
            language = getLastLine(element)
        elif 'name="username"' in element:
            username = getLastLine(element)
        elif 'name="trialID"' in element:
            trialID = getLastLine(element)


    filename = "test.pdf"
    f = open(filename, 'wb')
    f.write(emr)
    f.close()
    
    os.system("qpdf --object-streams=disable -qdf test.pdf test_success.pdf")
    os.system("python pdf2txt.py test_success.pdf > test.txt")

    print "name: " + name
    print "visit number: " + visit_number
    print "site: " + site
    print "visit type: " + visit_type
    print "emr type: " + emr_type
    print "Language: " + language


    with open("test.txt") as f:
        emr = f.read()

    if language != "en":
        (emr, languageDict) = translateEMR(emr, language)


    emr = strip_control_characters(emr)
    #print emr

    url = "http://localhost:3000/insert"
    body = dict()

    body["emr"] = emr
    body["patientID"] = name.strip()
    event_id = visit_number.strip().replace(" ", "-")
    event_id = str(name.strip()) + "-" + str(event_id)
    body["eventID"] = event_id
    body["type"] = "text"
    body["delimiter"] = "none"
    body["collectionName"] = "clinical_studio"
    body["recordType"] = emr_type
    body["language"] = languageMap[language]
    body["languageDict"] = json.dumps(languageDict)


    headers={'Content-Type': 'application/json'}
    payload = json.dumps(body)

    #post data to insert in backend
    r = requests.post(url, headers=headers, data=payload)
    setCredentials(username, name, visit_number, visit_type, site) #sets defaults in case user was logged in via username/pwd instead of token

    print r.status_code
    #time.sleep(60)
    #write(name, visit)
	


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


#sets the credentials for the user that uploaded the pdf
def setCredentials(username, name, visit_number, visit_type, site):
    global CREDENTIALS

    if username in CREDENTIALS:
        credential_data = CREDENTIALS[username]
        credential_data["name"] = name
        credential_data["visit_number"] = visit_number
        credential_data["visit_type"] = visit_type
        credential_data["site"] = site
    else:
        credential_data = {}
        credential_data["name"] = name
        credential_data["visit_number"] = visit_number
        credential_data["visit_type"] = visit_type
        credential_data["site"] = site
        credential_data["password"] = "Gangopad123"

    CREDENTIALS[username] = credential_data



#returns for each subject ID the list of forms to be completed and their metadata
def write(response):
    global CREDENTIALS

    routing_type = "2"
    level = "-1"
    form_version_id = "1"
    requesting_device_type = "2"
    longitude = "-1"
    latitude = "-1"
    vee_id = "-1"
    visit_interval_primary_key = "-1"
    form_data_primary_key = "-1"

    resp = json.loads(response)
    data_type = resp["type"]
    subject_id = resp["name"]
    visit_number = resp["visit_number"]
    site_name = resp["site"]
    visit_type = resp["visit_type"]
    username = resp["username"]
    #trial_id = resp["trialID"]

    credential_data = CREDENTIALS[username]
    password = credential_data["password"]

    #required to authorize with CS if AccelEDC accessed via redirect
    if "client_token" in credential_data:
        username = "OAUTH2_" + username


    url = "https://webapi.clinicalstudio.com/api"
    #url = "http://webdev.clinicalstudio.com/api"
    authstring = username + ":" + password
    #authstring = "anirban@mekhoshealth.com:Gangopad123"
    authstring = 'Basic ' + base64.b64encode(bytes(authstring), 'utf-8')
    headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Accept-Language': 'en', 'Authorization': authstring, 'User-Agent': 'api/1.0'}


    print "Subject ID: " + subject_id
    print "Visit Number: " + visit_number
    print "Site: " + site_name
    print "Visit type: " + visit_type
    print "Username: " + username
    print "Password: " + password
 
    #authenticate(url, headers)
    subject_primary_key = getSubjectPrimaryKey(url, headers, subject_id, site_name)
    site_id = getSiteID(url, headers, site_name)

    

    if data_type == "Medication Tracking":
    	populateConcomitantMedication(url, headers, routing_type, level, form_version_id, subject_primary_key, requesting_device_type, subject_id, latitude, longitude, response)
    elif data_type == "Adverse Events":
        populateAdverseEvents(url, headers, routing_type, level, form_version_id, subject_primary_key, requesting_device_type, subject_id, latitude, longitude, response)
    elif visit_type == "Scheduled":
    	writeScheduledEvents(url, headers, response, subject_id, visit_number, routing_type, level, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key, vee_id, latitude, longitude, data_type)
    elif visit_type == "Unscheduled":
    	writeUnscheduledEvents(url, headers, response, subject_id, visit_number, routing_type, level, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key, vee_id, latitude, longitude, data_type)


#populates the cohort 
def populateCohort(username, password, patients):
    routing_type = "2"
    level = "-1"
    form_version_id = "1"
    requesting_device_type = "2"
    longitude = "-1"
    latitude = "-1"
    vee_id = "-1"
    visit_interval_primary_key = "-1"
    form_data_primary_key = "-1"


    url = "https://webapi.clinicalstudio.com/api"
    username = "OAUTH2_" + username
    authstring = username + ":" + password
    authstring = 'Basic ' + base64.b64encode(bytes(authstring), 'utf-8')
    headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Accept-Language': 'en', 'Authorization': authstring, 'User-Agent': 'api/1.0'}

    #FIRST ENROLL 100 PATIENTS THROUGH THE API (HOW DO WE DO THIS?)

    for patient in patients:
        #first get the appropriate data for each patient from REST api

        subject_primary_key = getSubjectPrimaryKey(url, headers, subject_id, site_name) #WILL NEED TO PASS IN AN EXISTING SUBJECT ID
        site_id = getSiteID(url, headers, site_name)
        populateConcomitantMedication(url, headers, routing_type, level, form_version_id, subject_primary_key, requesting_device_type, subject_id, latitude, longitude, response)
        populateLogDemographics()
        populateLogMedicalHistory()
        populateAdverseEvents(url, headers, routing_type, level, form_version_id, subject_primary_key, requesting_device_type, subject_id, latitude, longitude, response)



#writes to the EDC for unscheduled events
def writeUnscheduledEvents(url, headers, response, subject_id, visit_number, routing_type, level, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key, vee_id, latitude, longitude, data_type):
    event_url = str(url) + "/visit/2/1"
    r = requests.get(event_url, headers=headers)
    body = json.loads(r.text)

    response = json.loads(response)
    data_type = response["type"]
    data = response["data"]
    date = response["date"]
    time = response["time"]

    if "Unknown" in date:
        date = ""
    else:
        date = date.split()
        date = date[1] + " " + date[2] + " " + date[3]
        d = datetime.strptime(date, '%b %d %Y')
        date = d.strftime('%m-%d-%Y')



    for visit in body["ev_list"]:
    	if visit["ev_name"] == visit_number:
    		for form in visit["form_list"]:
    			form_id = form["form_id"]
    			form_name = form["form_name"]
    			form_version_id = form["prot_id"]
    			vee_id = form["ev_id"]

    			if form_name == "Medical History" and data_type == "Medical History":
                            print "Getting and populating form!"
                            smoker = response["smoker"]
                            conmeds = response["meds"]
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapMedicalHistory(data, date, time, smoker, conmeds, form)
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    			
    			elif form_name == "Physical Exam" and data_type == "Physical Examination":
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapPhysicalExam(data, date, time, form)
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 

                        elif form_name == "Vital Signs" and data_type == "Vital Signs":
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapVitalSigns(data, date, time, form)
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    			
    			
    			#unused for now but may be relevant if we want to write to scheduled form
    			elif form_name == "Concomitant Medication" and data_type == "Medication Tracking":
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapConcomitantMedication(data, date, time, form)   
                            vee_id = "-1"                         
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    						
    			elif form_name == "Demography" and data_type == "Demographics":
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapDemographics(data, date, time, form)                            
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    			



#writes to the EDC for scheduled events
def writeScheduledEvents(url, headers, response, subject_id, visit_number, routing_type, level, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key, vee_id, latitude, longitude, data_type):
    subject_url = str(url) + "/subject/4/" + str(subject_primary_key)
    r = requests.get(subject_url, headers=headers)
    body = json.loads(r.text)

    response = json.loads(response)
    data_type = response["type"]
    data = response["data"]
    date = response["date"]
    time = response["time"]

    if "Unknown" in date:
        date = ""
    else:
        date = date.split()
        date = date[1] + " " + date[2] + " " + date[3]
        d = datetime.strptime(date, '%b %d %Y')
        date = d.strftime('%m-%d-%Y')


    for visit in body["int_list"]:
    	if visit["int_name"] == visit_number:
    		for form in visit["form_list"]:
    			form_id = form["form_id"]
    			visit_interval_primary_key = form["int_id"]
    			form_data_primary_key = form["trans_id"]
    			form_name = form["form_name"]


    			if form_name == "Medical History" and data_type == "Medical History":
                            smoker = response["smoker"]
                            conmeds = response["meds"]
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapMedicalHistory(data, date, time, smoker, conmeds, form)        
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    			
    			elif form_name == "Physical Exam" and data_type == "Physical Examination":
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapPhysicalExam(data, date, time, form)
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 

                        elif form_name == "Vital Signs" and data_type == "Vital Signs":
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapVitalSigns(data, date, time, form)
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    			
    			#unused for now but may be relevant if we want to write to unscheduled form
    			elif form_name == "Concomitant Medication" and data_type == "Medication Tracking":    						
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapConcomitantMedication(data, date, time, form)                            
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    						
    			elif form_name == "Demography" and data_type == "Demographics":
                            form = getForm(url, headers, routing_type, level, form_id, form_data_primary_key, visit_interval_primary_key, form_version_id, requesting_device_type, subject_primary_key)
                            (field_value_list, table_rows_list) = mapDemographics(data, date, time, form)                            
                            populateForm(url, headers, form_id, level, form_data_primary_key, visit_interval_primary_key, form_version_id, subject_primary_key, subject_id, vee_id, latitude, longitude, field_value_list, table_rows_list) 
    	



def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()



if __name__ == "__main__":

    run(port=int("7766"))  
    #4) Figure out how to generate queries

