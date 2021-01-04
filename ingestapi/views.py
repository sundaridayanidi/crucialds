from django.shortcuts import render


from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
# Create your views here.
from django.shortcuts import render
from django.template import RequestContext
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import math,random,string, json
from ingestapi.models import Users


#@login_required()
def index(request):
    context = RequestContext(request)
    records = {"Name":"Alfreds Futterkiste","City":"Berlin","Country":"Germany"}, {"Name":"Ana Trujillo Emparedados y helados","City":"México D.F.","Country":"Mexico"}, {"Name":"Antonio Moreno Taquería","City":"México D.F.","Country":"Mexico"}, {"Name":"Around the Horn","City":"London","Country":"UK"}, {"Name":"B's Beverages","City":"London","Country":"UK"}, {"Name":"Berglunds snabbköp","City":"Luleå","Country":"Sweden"}, {"Name":"Blauer See Delikatessen","City":"Mannheim","Country":"Germany"}, {"Name":"Blondel père et fils","City":"Strasbourg","Country":"France"}, {"Name":"Bólido Comidas preparadas","City":"Madrid","Country":"Spain"}, {"Name":"Bon app'","City":"Marseille","Country":"France"}, {"Name":"Bottom-Dollar Marketse","City":"Tsawassen","Country":"Canada"}, {"Name":"Cactus Comidas para llevar","City":"Buenos Aires","Country":"Argentina"}, {"Name":"Centro comercial Moctezuma","City":"México D.F.","Country":"Mexico"}, {"Name":"Chop-suey Chinese","City":"Bern","Country":"Switzerland"}, {"Name":"Comércio Mineiro","City":"São Paulo","Country":"Brazil"}
    return JsonResponse(records, safe = False)
    #return render_to_response('booking.html', 'records': records, context)

'''
    app.get("/", function(req, res) {
	    var accountMock = {
		"username": "nraboy",
		"password": "1234",
		"twitter": "@nraboy"
	    }
	    if(!req.query.username) {
		res.setHeader("Access-Control-Allow-Origin", "*");
		res.setHeader('Content-Type', 'application/json');
		return res.send({ "records":[ {"Name":"Alfreds Futterkiste","City":"Berlin","Country":"Germany"}, {"Name":"Ana Trujillo Emparedados y helados","City":"México D.F.","Country":"Mexico"}, {"Name":"Antonio Moreno Taquería","City":"México D.F.","Country":"Mexico"}, {"Name":"Around the Horn","City":"London","Country":"UK"}, {"Name":"B's Beverages","City":"London","Country":"UK"}, {"Name":"Berglunds snabbköp","City":"Luleå","Country":"Sweden"}, {"Name":"Blauer See Delikatessen","City":"Mannheim","Country":"Germany"}, {"Name":"Blondel père et fils","City":"Strasbourg","Country":"France"}, {"Name":"Bólido Comidas preparadas","City":"Madrid","Country":"Spain"}, {"Name":"Bon app'","City":"Marseille","Country":"France"}, {"Name":"Bottom-Dollar Marketse","City":"Tsawassen","Country":"Canada"}, {"Name":"Cactus Comidas para llevar","City":"Buenos Aires","Country":"Argentina"}, {"Name":"Centro comercial Moctezuma","City":"México D.F.","Country":"Mexico"}, {"Name":"Chop-suey Chinese","City":"Bern","Country":"Switzerland"}, {"Name":"Comércio Mineiro","City":"São Paulo","Country":"Brazil"} ] });
		//return res.send({"status": "error", "message": "missing username"});
		//return res.jsonp({status: 'error', message: 'missing username'});
	    } else if(req.query.username != accountMock.username) {
		return res.send({"status": "error", "message": "wrong username"});
		//return res.jsonp({"status": "error", "message": "wrong username"});
	    } else {
		return res.send(accountMock);
	    }
	});


'''




'''

	app.get("/getPassword", function(req, res) {
		if (!req.query.username) {
			return res.send({"status": "error", "message": "missing parameters"});

		} else {
			var query = { "username": req.query.username};
			var fields = {"password": 1, "role": 1};
  			db.collection("users").find(query, fields).toArray(function(err, result) {
    			if (err) throw err;
    			console.log(result);

    			res.setHeader('Content-Type', 'text/plain');
				res.setHeader("Access-Control-Allow-Origin", "*");
		        return res.send(result[0]);
  			});
		}
	});

'''

#@login_required()   
def addUser(request):
	data = {}
	data["username"] = request.GET["username"]

	data["trialID"] = request.GET["trialID"]
	
	data["role"] = request.GET["role"]
	data["password"] = res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8)) 
	print(data["password"])
	data["total_edc"] = "0"
	data["edc_time"] = "None"
	if (request.GET["username"] == "henrik@viedoc.com" or request.GET["username"] == "mikael@viedoc.com"):
		data["db"] = "viedoc"
	else:
		data["db"] = "clinical_studio"
	#query = { "username": request.GET["username"], "trialID": request.GET["trialID"]}
	count = Users.objects.filter(username= request.GET["username"], trialID= request.GET["trialID"]).count()
	print("c is ", count)
#	count = db.collection("users").find(query).count()

	if (count == 0):
		#we add 7 because we display seven in the timeline in AccelEDC
		data["pdf_history"] = [{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"}, {"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"}]
		#db.collection("users").insert(data)
		Users.objects.create(username= request.GET["username"], trialID=request.GET["trialID"], role=request.GET["role"], comments="vfuyvuv")
		#dump = json.dumps({'status':'200'})
		#return HttpResponse(dump, content_type='application/json')
		return JsonResponse({'status':'200'})
	else:
		return HttpResponse(status=200)
	



'''
	app.post("/addUser", function(req, res) {
		var credentials = "Basic cGF1bC5ncmFkeUBjbHNkcy5jb206Z3JzMm1nViQoZFIkMytASw==";

		if (!req.body.username || !req.body.trialID  || !req.body.role || !req.headers.authorization) {
			return res.send({"status": "error", "message": "missing parameters"});

	    } else if (req.headers.authorization != credentials) {
	    	return res.send({"status": "error", "message": "unauthorized"});

	    } else {
	    	
	    	var data = {};
	    	data["username"] = req.body.username;
	    	data["trialID"] = req.body.trialID;
	    	data["role"] = req.body.role;
	    	data["password"] = Math.random().toString(36).slice(-8);
	    	data["total_edc"] = "0";
	    	data["edc_time"] = "None";

	    	if (req.body.username == "henrik@viedoc.com" || req.body.username == "mikael@viedoc.com") {
	    		data["db"] = "viedoc";
	    	} else {
	    		data["db"] = "clinical_studio";
	    	}


			var query = { "username": req.body.username, "trialID": req.body.trialID};

	    	db.collection("users").find(query).count(function(err, count) {
	    
	    	if (count == 0) {
	    		//we add 7 because we display seven in the timeline in AccelEDC
	    		data["pdf_history"] = [{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"}, {"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"},{"Title": "None", "Time": "None", "Body": "No PDFs uploaded yet"}];
	    		db.collection("users").insert(data);

	    		res.setHeader("Access-Control-Allow-Origin", "*");
				return res.sendStatus(200);
	    	} else {
	    		res.setHeader("Access-Control-Allow-Origin", "*");
				return res.sendStatus(200);
	    	}
	    		
			});

	    }

	});


'''


#@login_required()   
def updateRole(request):
	Users.objects.filter(username =  request.GET["username"], trialID =  request.GET["trialID"]).update(role = request.GET["role"], multi = "true")
#	db.collection("users").update({"username": request.GET["username"], "trialID": request.GET["trialID"]}, { $set : {"role": request.GET["role"]}}, {"multi": true})
	return HttpResponse(status=200)    	


'''

	app.get("/updateRole", function(req, res) {
		if (!req.query.username || !req.query.trialID || !req.query.role) {
			return res.send({"status": "error", "message": "missing parameters"});
		} else {
			db.collection("users").update({"username": req.query.username, "trialID": req.query.trialID}, { $set : {"role": req.query.role}}, {"multi": true});
	    	res.setHeader("Access-Control-Allow-Origin", "*");
	    	res.setHeader('Access-Control-Allow-Methods', 'POST');
			res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
			return res.sendStatus(200);
		}
	});



'''

#@login_required()   
def addPDFHistory(request):
	title = request.GET["title"]
	title = (" ").join(title.split("_"))
	time = request.GET["time"]
	time = (" ").join(time.split("_"))
	body = request.GET["body"]
	body = (" ").join(body.split("_"))

	pdf = {"Title": title, "Time": time, "Body": body}
	username = request.GET["username"]
	trialID = request.GET["trialID"]
	#dat = []
	#dat.push(pdf)
	print(pdf)
	Users.objects.filter(username =  request.GET["username"], trialID =  request.GET["trialID"]).update(pdf_history = pdf)

#	db.collection("users").update({"username": username, "trialID": trialID}, {$push: { "pdf_history": { $each: dat }}});
	return HttpResponse(status=200)  





'''
	app.get("/addPDFHistory", function(req, res) {

		if (!req.query.username) {
			return res.send({"status": "error", "message": "missing username"});
		} else if (!req.query.trialID) {
			return res.send({"status": "error", "message": "missing trialID"});
		} else if (!req.query.Title) {
			return res.send({"status": "error", "message": "missing Title"});
		} else if (!req.query.Time) {
			return res.send({"status": "error", "message": "missing Time"});
		} else if (!req.query.Body) {
			return res.send({"status": "error", "message": "missing Body"});	

	    } else {
	    	var title = req.query.Title;
	    	title = title.split("_").join(" ");
	    	var time = req.query.Time;
	    	time = time.split("_").join(" ");
	    	var body = req.query.Body;
	    	body = body.split("_").join(" ");

	    	var pdf = {"Title": title, "Time": time, "Body": body};
	    	var username = req.query.username;
	    	var trialID = req.query.trialID;
	    	var dat = [];
	    	dat.push(pdf);


	    	db.collection("users").update({"username": username, "trialID": trialID}, {$push: { "pdf_history": { $each: dat }}});
	    	res.setHeader("Access-Control-Allow-Origin", "*");
	    	res.setHeader('Access-Control-Allow-Methods', 'POST');
			res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

			return res.sendStatus(200);
	    }
	});

'''
#@login_required()   
def addEDCSubmission(request):
	username = request.GET["username"]
	trialID = request.GET["trialID"]
	total_edc = request.GET["total_edc"]
	edc_time = request.GET["edc_time"]
	edc_time = (" ").join(edc_time.split("_"))
	Users.objects.filter(username =  request.GET["username"], trialID =  request.GET["trialID"]).update(total_edc= total_edc, edc_time = edc_time, multi = "true")
	# db.collection("users").update({"username": username, "trialID": trialID}, { $set : {"total_edc": total_edc, "edc_time": edc_time}}, {"multi": true});
	return HttpResponse(status=200)  			
'''
	app.get("/addEDCSubmission", function(req, res) {
		if (!req.query.username || !req.query.trialID || !req.query.total_edc || !req.query.edc_time) {
			return res.send({"status": "error", "message": "missing parameters"});

		} else {
			var username = req.query.username;
			var trialID = req.query.trialID;
			var total_edc = req.query.total_edc;
			var edc_time = req.query.edc_time;
			edc_time = edc_time.split("_").join(" ");
			db.collection("users").update({"username": username, "trialID": trialID}, { $set : {"total_edc": total_edc, "edc_time": edc_time}}, {"multi": true});
			res.setHeader("Access-Control-Allow-Origin", "*");
	    	res.setHeader('Access-Control-Allow-Methods', 'POST');
			res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

			return res.sendStatus(200);
		}
	});



'''

@login_required()      
def getSettings(request):
	query = { "db": request.GET["db"]}
	fields = {"username" : 1, "trialID": 1, "role": 1}
	if (db.collection("users").find(query, fields)):
		return HttpResponse(status=200)  

'''

	app.get("/getSettings", function(req, res) {
		if (!req.query.db) {
			return res.send({"status": "error", "message": "missing parameters"});

		} else {
			var query = { "db": req.query.db};
			var fields = {"username" : 1, "trialID": 1, "role": 1};
  			db.collection("users").find(query, fields).toArray(function(err, result) {
    			if (err) throw err;

    			res.setHeader('Content-Type', 'text/plain');
				res.setHeader("Access-Control-Allow-Origin", "*");
		        return res.send(result);
  			});
		}
	});




'''

   
@login_required()   
def logIP(request):
	ip = []
	ip.push(request.GET["ip"])
	if(request.GET["type"] == "log"):
		#db.collection("users").update({"username": req.query.username, "trialID": req.query.trialID}, {$push: { "IP_logs": { $each: ip }}});
		pass
	elif (request.GET["type"] == "submit"):
		pass
		#db.collection("users").update({"username": req.query.username, "trialID": req.query.trialID}, {$push: { "IP_lookup": { $each: ip }}});

	elif(request.GET["type"] == "delete"):
		pass
		#db.collection("users").update({"username": req.query.username, "trialID": req.query.trialID}, {$push: { "IP_delete": { $each: ip }}});
	return HttpResponse(status=200)  
'''



	app.get("/logIP", function(req, res) {
		if (!req.query.ip || !req.query.username || !req.query.trialID || !req.query.type) {
			return res.send({"status": "error", "message": "missing parameters"});
		} else {
			var ip = [];
			ip.push(req.query.ip);

			if (req.query.type == "log") {
				db.collection("users").update({"username": req.query.username, "trialID": req.query.trialID}, {$push: { "IP_logs": { $each: ip }}});

			} else if (req.query.type == "submit") {
				db.collection("users").update({"username": req.query.username, "trialID": req.query.trialID}, {$push: { "IP_lookup": { $each: ip }}});

			} else if (req.query.type == "delete") {
				db.collection("users").update({"username": req.query.username, "trialID": req.query.trialID}, {$push: { "IP_delete": { $each: ip }}});
			}

	    	res.setHeader("Access-Control-Allow-Origin", "*");
	    	res.setHeader('Access-Control-Allow-Methods', 'POST');
			res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
			return res.sendStatus(200);

		}
	});




'''

@login_required()   
def getTimeline(request):
	query = { "username": request.GET["username"], "trialID": request.GET["trialID"]};
	fields = {"pdf_history" : 1, "total_edc": 1, "edc_time": 1};
	if(db.collection("users").find(query, fields)):
		return HttpResponse(status=200)  

'''



	app.get("/getTimeline", function(req, res) {
		if (!req.query.username || !req.query.trialID) {
			return res.send({"status": "error", "message": "missing parameters"});

		} else {
			var query = { "username": req.query.username, "trialID": req.query.trialID};
			var fields = {"pdf_history" : 1, "total_edc": 1, "edc_time": 1};
  			db.collection("users").find(query, fields).toArray(function(err, result) {
    			if (err) throw err;

    			res.setHeader('Content-Type', 'text/plain');
				res.setHeader("Access-Control-Allow-Origin", "*");
		        return res.send(result[0]);
  			});
		}
	});


'''
import os 
#@login_required()     
def insert(request):
	options = {
	    'mode': 'text',
	    'pythonPath': '//usr/bin/python',
	    'pythonOptions': ['-u'],
	    'scriptPath': '/Users/gangopad/Company/REST/ApysAPI',
	#    //args: ["text", "100-01", "111", req.body.emr, "\n"]
	    'args': [request.GET["type"], request.GET["patientID"], request.GET["eventID"], request.GET["emr"], request.GET["delimiter"], request.GET["collectionName"], request.GET["recordType"], request.GET["language"], request.GET["languageDict"] ] 
	}
	os.system('python /home/rt/Downloads/dsrc/crucialds/ingestapi/IngestAPI-master/insert.py [request.GET["type"] request.GET["patientID"] request.GET["eventID"] request.GET["emr"] request.GET["delimiter"] request.GET["collectionName"] request.GET["recordType"] request.GET["language"] request.GET["languageDict"]')
	return HttpResponse(status=200)      
    
    
'''



    app.post("/insert", function(req, res) {
	    
	    if(!req.body.emr || !req.body.type || !req.body.patientID || !req.body.eventID || !req.body.delimiter || !req.body.collectionName || !req.body.recordType || !req.body.language || !req.body.languageDict) {
		console.log("status: error");
		return res.send({"status": "error", "message": "missing parameters"});
		
	    } else {
		var PythonShell = require('python-shell');

		console.log(req.body.eventID);

		var options = {
		    mode: 'text',
		    pythonPath: '//anaconda/bin/python',
		    pythonOptions: ['-u'],
		    scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
		    //args: ["text", "100-01", "111", req.body.emr, "\n"]
		    args: [req.body.type, req.body.patientID, req.body.eventID, req.body.emr, req.body.delimiter, req.body.collectionName, req.body.recordType, req.body.language, req.body.languageDict]  
		};

		console.log(req.body.emr);

		PythonShell.run('insert.py', options, function (err, results) {
			if (err) throw err;
			// results is an array consisting of messages collected during execution
			console.log('results: %j', results);
		    });

		res.setHeader("Access-Control-Allow-Origin", "*");
		return res.sendStatus(200);
	    }
	    

	    

	});

'''


#@login_required()     
def delete(request):
	options = {
	    'mode': 'text',
	    'pythonPath': '//usr/bin/python',
	    'pythonOptions': ['-u'],
	    'scriptPath': '/Users/gangopad/Company/REST/ApysAPI',
	#    //args: ["text", "100-01", "111", req.body.emr, "\n"]
	    'args': [request.GET["type"], request.GET["patientID"], request.GET["eventID"], request.GET["emr"], request.GET["delimiter"], request.GET["collectionName"], request.GET["recordType"], request.GET["language"], request.GET["languageDict"] ] 
	}
	os.system('python /home/rt/Downloads/dsrc/crucialds/ingestapi/IngestAPI-master/delete.py [request.GET["type"] request.GET["patientID"] request.GET["eventID"] request.GET["emr"] request.GET["delimiter"] request.GET["collectionName"] request.GET["recordType"] request.GET["language"] request.GET["languageDict"]')
	return HttpResponse(status=200)      
    

'''    

	app.get("/delete", function(req, res) {
	    
	    if(!req.query.eventID || !req.query.collectionName) {
		return res.send({"status": "error", "message": "missing parameters"});
	    } else {
		var PythonShell = require('python-shell');

		console.log(req.query.eventID);

		var options = {
		    mode: 'text',
		    pythonPath: '//anaconda/bin/python',
		    pythonOptions: ['-u'],
		    scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
		    //args: ["text", "100-01", "111", req.body.emr, "\n"]
		    args: [req.query.eventID, req.query.collectionName]  
		};

		//console.log(req.body.emr);

		PythonShell.run('delete.py', options, function (err, results) {
			if (err) throw err;
			// results is an array consisting of messages collected during execution
			console.log('results: %j', results);
			res.setHeader('Content-Type', 'text/plain');
			res.setHeader("Access-Control-Allow-Origin", "*");
		        return res.send(results[0]);
		      
		    });


	    }
	    

	    

	});

'''

def costing(request):

	_type = request.GET["type"] + ",cost"
	inclusion = "cost>0"
	costing = {}
	# findDocuments(db, umls_db, _type, inclusion, "inclusion", req.query.collectionName, "false", function(docs)		
	for i in range(docs.length):
		tmp = docs[i]
		for key in tmp: 
				if (key == "cost"):
					cost = tmp[key]
				elif (key != "_id"):
					vals = tmp[key]
					vals = string(vals).toLowerCase()			    
				
				if (vals in costing) :
					val = costing[vals]
					val = val + cost
					costing[vals] = val
				else:
					costing[vals] = cost
		return JsonResponse(costing, safe = False)


'''


    //given the type (ie physician, Professional or Occupational Group) returns the cost breakdown
    app.get("/costing", function(req, res) {
	    var type;
	    var vals;
	    var tmp;
	    var cost;
            
	    if(!req.query.type || !req.query.collectionName) {
                return res.send({"status": "error", "message": "missing parameters! [type] [collection]"});

            } else {
		type = req.query.type + ",cost";
		inclusion = "cost>0";

		costing = {};

		findDocuments(db, umls_db, type, inclusion, "inclusion", req.query.collectionName, "false", function(docs) {
			console.log(docs.length);

			for (i = 0; i < docs.length; i++) {
			    tmp = docs[i];
			    for (var key in tmp) {
				if (key == "cost") {
				    cost = tmp[key];
				} else if (key != "_id") {
				    //vals = tmp[key].toLowerCase(); //this is a specific element for the given type
				    vals = tmp[key];
				    vals = String(vals).toLowerCase();
				}
			    }
				
				if (vals in costing) {
				    val = costing[vals];
				    val = val + cost;
				    costing[vals] = val;

				} else {
				    costing[vals] = cost;
				}

			}


			//return res.json(JSON.stringify(costing));
			res.setHeader("Access-Control-Allow-Origin", "*");
			res.setHeader('Content-Type', 'application/json');
			return res.json(costing);

		    });

	    }
    });
'''

def readmissions(request):
	_type = "patient_id"
	inclusion = request.GET["inclusion"]
	collectionName = request.GET["collectionName"]
	if (request.GET["exclusion"]):
		exclusion = request.GET["exclusion"]
	else:
		exclusion = ""
		# findDocuments(db, umls_db, type, inclusion, "inclusion", collectionName, "false", function(docs) {
        #                 console.log(docs.length);
        #                 findDocuments(db, umls_db, _type, exclusion, "exclusion", collectionName, "false", function(docs2) {
        #                         console.log(docs2.length);
	docs2_ids = []
	for i in range(docs2.length):
		docs2_ids[i] = String(docs2[i]._id)
		count = 0
		finalDocs = []
	for i in range(docs.length):                                                                                                           
		if (docs2_ids.indexOf(String(docs[i]._id)) > -1):
			pass
		else:
			finalDocs[count] = docs[i]
			count = count + 1
                                			
		readmissions = {}
		# here we find patient IDs that occurred more than once and add to list
		for i in range(finalDocs.length): 
			tmp = finalDocs[i]
			for key in tmp:
				if (key != "_id"):
					vals = tmp[key]
					if (vals in readmissions):
						val = readmissions[vals]
						val = val + 1
						readmissions[vals] = val
					else:
						readmissions[vals] = 1
				filtered_readmissions = {}
				count = 0
			# here we loop through readmissions and only keep keys that have value greater than 1
			for key in readmissions:
				val = readmissions[key]

				if (val > 1):
					filtered_readmissions[key] = val

				res.setHeader("Access-Control-Allow-Origin", "*")
				res.setHeader('Content-Type', 'application/json')
				return res.json(filtered_readmissions)