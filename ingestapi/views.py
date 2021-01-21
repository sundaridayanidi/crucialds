from django.shortcuts import render


from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
# Create your views here.
from django.shortcuts import render
from django.template import RequestContext
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import math,random,string 
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
		Users.objects.create(id=767, username= request.GET["username"], trialID=request.GET["trialID"], role="ytrytf", comments="vfuyvuv")
		return HttpResponse(status=200)
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
					vals = String(vals).toLowerCase()			    
				
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

'''

    //given query, returns all patients that have a record within 30 days
    app.get("/readmissions", function(req, res) {
	    var type;
            var inclusion;
            var exclusion;
            var tmp;
            var vals;
	    var collectionName;

            if(!req.query.inclusion || !req.query.collectionName) {
                return res.send({"status": "error", "message": "missing parameters! [inclusion] [collection]"});

            } else {

		type = "patient_id";
		inclusion = req.query.inclusion;
		collectionName = req.query.collectionName;

                //initialize exclusion, type
		if (req.query.exclusion) {
                    exclusion = req.query.exclusion;
                } else {
                    exclusion = "";
                }

		findDocuments(db, umls_db, type, inclusion, "inclusion", collectionName, "false", function(docs) {
                        console.log(docs.length);
                        findDocuments(db, umls_db, type, exclusion, "exclusion", collectionName, "false", function(docs2) {
                                console.log(docs2.length);

                                docs2_ids = [];
                                for (i = 0; i < docs2.length; i++) {
                                    docs2_ids[i] = String(docs2[i]._id);
                                }

                                //console.log("Length of docs2_ids " + docs2_ids.length);                                                                                

                                var count = 0;
                                finalDocs = [];
                                for (i = 0; i < docs.length; i++) {
                                    // console.log(docs[i]._id);                                                                                                           

                                    if (docs2_ids.indexOf(String(docs[i]._id)) > -1) {
                                        //console.log("The above is in docs2!");
                                    } else {
                                        //console.log("The above is not in docs2!");   
					finalDocs[count] = docs[i];
                                        count = count + 1;
                                    }
                                }

				
				readmissions = {}
				//here we find patient IDs that occurred more than once and add to list 
				for (i = 0; i < finalDocs.length; i++) {
				    tmp = finalDocs[i];
                                    for (var key in tmp) {
                                        if (key != "_id") {
                                            vals = tmp[key];

                                            if (vals in readmissions) {
                                                val = readmissions[vals];
                                                val = val + 1;
                                                readmissions[vals] = val;

                                            } else {
                                                readmissions[vals] = 1;
                                            }
                                            
                                        }
                                    }

				}

				filtered_readmissions = {};
				var count = 0;
				//here we loop through readmissions and only keep keys that have value greater than 1
				for (var key in readmissions) {
				    val = readmissions[key];

				    if (val > 1) {
					filtered_readmissions[key] = val;
				    }
				}

                                //we return docs - docs2
				res.setHeader("Access-Control-Allow-Origin", "*");
                                res.setHeader('Content-Type', 'application/json');
				return res.json(filtered_readmissions);
                            });
                    });

	    }

	});

'''
def  linkback(request):
	exclusion = ""
	inclusion = request.GET["condition"]
	_type = ""
	if inclusion.index("<") > -1 or inclusion.index(">") > -1:
		temp_inclusion = inclusion.split(",")
		
		for element in temp_inclusion:
			val = temp_inclusion[element]
			
			if val.index("<") > -1:
				val = val.split("<")
				_type = _type + val[0] + ","

			elif val.index(">") > -1:
				val = val.split(">")
				_type = _type + val[0] + ","
			
			else:
				_type = _type + val + ","
				_type = _type + "event_id"
				_type = request.GET["condition"] + ",event_id"


		# findDocuments(db, umls_db, type, inclusion, "inclusion", req.query.collectionName, "true", function(docs) {
        #             console.log(docs.length);
		for i in range(docs.length):
			tmp = docs[i]

		for key in tmp:
			if key != "event_id" and key != "_id":
				writeTmp["Event ID"] = tmp["event_id"]
				writeTmp["Condition"] = key
				writeTmp["Raw text"] = tmp[key]
				finalDocs.push(writeTmp)
				writeTmp = {}

		res.setHeader("Access-Control-Allow-Origin", "*")
		res.setHeader('Content-Type', 'application/json')
		return res.json(finalDocs)
'''
    //supports one query at a time
    app.get("/linkback", function(req, res) {
	    var type;
	    var inclusion;
	    var exclusion;
	    var val;
	    var event;
	    var writeTmp = {};
	    var finalDocs = [];
	    
	    if (!req.query.condition || !req.query.collectionName) {
		return res.send({"status": "error", "message": "missing condition"});
	    } else {
		exclusion = "";
		inclusion = req.query.condition;
		type = "";
		
		if (inclusion.indexOf("<") > -1 || inclusion.indexOf(">") > -1) {
		    var temp_inclusion = inclusion.split(",");

		    for (var element in temp_inclusion) {

			val = temp_inclusion[element];
			
			if (val.indexOf("<") > -1) {
			    val = val.split("<");
			    type = type + val[0] + ",";

		       } else if (val.indexOf(">") >-1) {
			    val = val.split(">");
                            type = type + val[0] + ",";

		        } else {
			    type = type + val + ",";
			}
		    }
		    
		    type = type + "event_id";

		} else {
		    type = req.query.condition + ",event_id";
		}

		findDocuments(db, umls_db, type, inclusion, "inclusion", req.query.collectionName, "true", function(docs) {
                    console.log(docs.length);


		    for (i = 0; i < docs.length; i++) {
			tmp = docs[i];

			for (var key in tmp) {
			    if (key != "event_id" && key != "_id") {
				writeTmp["Event ID"] = tmp["event_id"];
				writeTmp["Condition"] = key;
				writeTmp["Raw text"] = tmp[key];
				finalDocs.push(writeTmp);
				writeTmp = {};

			    } 
			}
		    }

		    res.setHeader("Access-Control-Allow-Origin", "*");
		    res.setHeader('Content-Type', 'application/json');
		    return res.json(finalDocs);

		});
	    }

    });

'''
def  distribution(request):
                if request.GET["inclusion"]:
                    inclusion = request.GET["inclusion"]
                else:
                    inclusion = ""

                if request.GET["exclusion"]:
                    exclusion = request.GET["exclusion"]
                else:
                    exclusion = ""

                _type = request.GET["type"]
 

		# findDocuments(db, umls_db, type, inclusion, "inclusion", req.query.collectionName, "false", function(docs) {
        		# console.log(docs.length)
        # findDocuments(db, umls_db, type, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
            # console.log(docs2.length)

# docs2_ids = []
# for i in range(docs2.length):
# 	docs2_ids[i] = String(docs2[i]._id)  
# 	console.log("Length of docs2_ids " + docs2_ids.length);                                                                                  
# count = 0
# finalDocs = []
# for i in range(docs.length):
# 	pass
		
# if (docs2_ids.index(String(docs[i]._id)) > -1):
# 	pass                                                                                                               
# else:
# 	pass                                                                                           
		
# finalDocs[count] = docs[i]
# count = count + 1


#                 #                 //finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 });                                                                          
# 				# console.log("Final docs " + finalDocs.length);

# distribution = {}
# # //we compute the percentage breakdown of the types by element and return the result in a JSON blob
# for i in range(finalDocs.length):
# 	tmp = finalDocs[i]
					
# for key in tmp:
# 	if (key != "_id"):
# 		vals = tmp[key]
					    
# 	if type != "string" and type != "number":
# 		for v in vals:
# 			# //console.log(vals[v]);

# 			if vals[v] in distribution:
# 				val = distribution[vals[v]]
# 				val = val + 1
# 				distribution[vals[v]] = val
# 			else:
# 				distribution[vals[v]] = 1
# 				vals = vals.split('_').join('')
# 							#  some physician entries have _. We get rid of them
# 		if (vals in distribution):
# 			val = distribution[vals]
# 			val = val + 1
# 			distribution[vals] = val
# 		else:
# 			distribution[vals] = 1
# num_patients = finalDocs.length
# finalDistribution = {}
# 				# var total  = 0;

# for i in distribution:
# 	val = distribution[i]
# 	val = (val * 1.0)/num_patients
# 	distribution[i] = val
# 	total = total + val
		
# 	console.log(distribution);
# 	console.log("The sum of the percentages is " + String(total));

# keysSorted = Object.keys(distribution).sort(function(a,b){return distribution[b]-distribution[a]})

# ind = 1
# for k in keysSorted:
# 	finalDistribution[keysSorted[k]] = parseFloat(parseFloat(Math.round(distribution[keysSorted[k]] * 100) / 100).toFixed(2))

	# console.log(finalDistribution)
				
# return res.json(JSON.stringify(finalDistribution))
# res.setHeader("Access-Control-Allow-Origin", "*")
# res.setHeader('Content-Type', 'application/json')
# return res.json(finalDistribution)



# def countdistribution(request):
	
# 	if (request.GET["inclusion"]):
# 		inclusion = request.GET["inclusion"]
# 	else:
# 		inclusion = "";
# 	if request.GET["exclusion"]:
# 		exclusion = request.GET["exclusion"]
		
# 	else:
# 		exclusion = ""

	# _type = request.GET["type"] + String(",patient_id")
	# numTerms = parseInt(request.GET["num"] )	

		# findDocuments(db, umls_db, type, inclusion, "inclusion", req.query.collectionName, "false", function(docs) {
        #                 console.log(docs.length);
        #                 findDocuments(db, umls_db, type, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
        #                         console.log(docs2.length);

# docs2_ids = [];
# for i in range(docs2.length):
# 	docs2_ids[i] = String(docs2[i]._id)
                                                                                  
# count = 0
# finalDocs = []
# for i in range(docs.length):
# 	pass
   
# 	if (docs2_ids.index(String(docs[i]._id)) > -1):
# 		console.log("The above is in docs2!")
# 	else:                                                                               
# 		finalDocs[count] = docs[i]
		# count = count + 1
                        
	# finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 });                                                                          
	# console.log("Final docs " + finalDocs.length)

	# distribution = {}
	# seen_patients = []
    # we compute the percentage breakdown of the types by element and return the result in a JSON blob
	# for i in range(finalDocs.length):
	# 	tmp = finalDocs[i]

	# console.log(tmp["patient_id"])
	# console.log(seen_patients.indexOf(String(tmp["patient_id"])));
				   
	# if (seen_patients.index(String(tmp["patient_id"])) == -1):
					# add the unseen patient ID to the list of seen. We only want to count on unique patients not unique records
					# seen_patients.push(tmp["patient_id"])

# for key in tmp:
# 		if (key != "_id" and key != "patient_id"):
# 			vals = tmp[key]
					
# 		if (type != "string" and type != "number"):
# 			for v in vals:
# 				console.log(vals[v])

# 				if (vals[v] in distribution):
# 					val = distribution[vals[v]]
# 					val = val + 1
# 					distribution[vals[v]] = val
# 				else:
# 					distribution[vals[v]] = 1
# 					# some physician entries have _. We get rid of them
# 					vals = vals.split('_').join('');  
						
# 				if (vals in distribution):
# 					val = distribution[vals]
# 					val = val + 1
# 					distribution[vals] = val
# 				else:
# 					distribution[vals] = 1
                                            

				# here we do the same as above for the qualified incl/excl criteria
				

# finalDistribution = {}

				
				# //console.log(distribution);

				# keysSorted = Object.keys(distribution).sort(function(a,b){return distribution[b]-distribution[a]})

# ind = 1
# for k in keysSorted:
# 	finalDistribution[keysSorted[k]] = distribution[keysSorted[k]]
# 	if (ind >= numTerms):
# 		break
# 	ind = ind + 1

# res.setHeader("Access-Control-Allow-Origin", "*")
# res.setHeader('Content-Type', 'application/json')
# res.json(finalDistribution)				

'''
    //returns the distribution of counts. also takes in the number to return
    app.get("/countdistribution", function(req, res) {
	    var type;
            var inclusion;
            var exclusion;
	    var tmp;
	    var vals;
	    var numTerms;
	    var ind;
	       
	    if(!req.query.type || !req.query.num || !req.query.collectionName) {
                return res.send({"status": "error", "message": "missing parameters! [type] [num]"});

            } else {
                //initialize inclusion, exclusion, fields                                                                                                                                         
                if (req.query.inclusion) {
                    inclusion = req.query.inclusion;
                } else {
                    inclusion = "";
                }

                if (req.query.exclusion) {
                    exclusion = req.query.exclusion;
                } else {
                    exclusion = "";
                }

                type = req.query.type + String(",patient_id");
		numTerms = parseInt(req.query.num);

		findDocuments(db, umls_db, type, inclusion, "inclusion", req.query.collectionName, "false", function(docs) {
                        console.log(docs.length);
                        findDocuments(db, umls_db, type, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
                                console.log(docs2.length);

                                docs2_ids = [];
                                for (i = 0; i < docs2.length; i++) {
                                    docs2_ids[i] = String(docs2[i]._id);
                                }

                                //console.log("Length of docs2_ids " + docs2_ids.length);                                                                                    
                                var count = 0;
                                finalDocs = [];
                                for (i = 0; i < docs.length; i++) {
                                    // console.log(docs[i]._id);
   
				    if (docs2_ids.indexOf(String(docs[i]._id)) > -1) {
                                        //console.log("The above is in docs2!");                                                                                                               
				    } else {
                                        //console.log("The above is not in docs2!");                                                                                           
					finalDocs[count] = docs[i];
                                        count = count + 1;
                                    }
                                }


                                //finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 });                                                                          
				console.log("Final docs " + finalDocs.length);

				var distribution = {};
				var seen_patients = [];
                                //we compute the percentage breakdown of the types by element and return the result in a JSON blob
				for (i = 0; i < finalDocs.length; i++) {
				    tmp = finalDocs[i];

				    //console.log(tmp["patient_id"]);
				    //console.log(seen_patients.indexOf(String(tmp["patient_id"])));
				   
				    if (seen_patients.indexOf(String(tmp["patient_id"])) == -1) {
					//add the unseen patient ID to the list of seen. We only want to count on unique patients not unique records
					seen_patients.push(tmp["patient_id"]);

                                    for (var key in tmp) {
					if (key != "_id" && key != "patient_id") {
					    vals = tmp[key];
					        
					    if (typeof vals != "string" && typeof vals != "number") { 
						for (var v in vals) {
						    //console.log(vals[v]);

						    if (vals[v] in distribution) {
							val = distribution[vals[v]];
							val = val + 1;
							distribution[vals[v]] = val;

						    } else {
							distribution[vals[v]] = 1;
						    }
						}

					    }   else {

						vals = vals.split('_').join('');  //some physician entries have _. We get rid of them
						if (vals in distribution) {
                                                    val = distribution[vals];
                                                    val = val + 1;
                                                    distribution[vals] = val;

                                                } else {
                                                    distribution[vals] = 1;
                                                }
					    }
					}
				    }
				    }
                                }

				//here we do the same as above for the qualified incl/excl criteria
				

				var finalDistribution = {};

				
				//console.log(distribution);

				keysSorted = Object.keys(distribution).sort(function(a,b){return distribution[b]-distribution[a]});

				ind = 1;
				for (k in keysSorted) {
				    finalDistribution[keysSorted[k]] = distribution[keysSorted[k]];
				      if (ind >= numTerms) {
				          break;
				      }

				      ind = ind + 1;

				}
				console.log(finalDistribution);
				//return res.json(JSON.stringify(finalDistribution));
				res.setHeader("Access-Control-Allow-Origin", "*");
				res.setHeader('Content-Type', 'application/json');
				return res.json(finalDistribution);
                            });
                    });

            }



	});


'''

# def othercountdistribution(request):
# 	if (request.GET["inclusion"]):
# 		inclusion = request.GET["inclusion"]
# 	else:
# 		inclusion = ""
    
# 	if (request.GET["exclusion"]):
#                     exclusion = request.GET["exclusion"]
# 	else:
# 		exclusion = ""

# _type = request.GET["type"] + String(",patient_id")
# numTerms = parseInt(request.GET["num"])

# 		# findDocuments(db, umls_db, type, inclusion, "inclusion", req.query.collectioName, "false", function(docs) {
#                         # console.log(docs.length);
#                         # findDocuments(db, umls_db, type, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
#                                 # console.log(docs2.length);

# 				# findDocuments(db, umls_db, type, other_inclusion, "inclusion", req.query.collectionName, "false", function(docs3) {
# 				#     console.log(docs3.length);

# docs2_ids = []
# docs_ids = []
# for i in range(docs2.length):
# 		docs2_ids[i] = String(docs2[i]._id)
	
# for i in range(docs.length):
#         docs_ids[i] = String(docs[i]._id)
#         console.log("Length of docs2_ids " + docs2_ids.length);                                                                                    
    
# count = 0
# finalDocs = []
# for i in range(docs3.length):
#         console.log(docs[i]._id);

# if (docs_ids.index(String(docs3[i]._id)) > -1):
#         console.log("The above is in docs2!")
# if (docs2_ids.index(String(docs3[i]._id)) > -1):
# 	finalDocs[count] = docs3[i]
# 	count = count + 1

# else:
# 	console.log("The above is not in docs2!")                                                                                          
# 	finalDocs[count] = docs3[i]
# 	count = count + 1


# 	# codocs of diseases that fit inclusion/exclusion criteria. we get this to get the list of type values for the qualified query                     unt = 0

# countfinalDocs = [] 

# for i in range(docs.length):
#     console.log(docs[i]._id)                                                                                                                                
# if (docs2_ids.index(String(docs[i]._id)) > -1):
#     console.log("The above is in docs2!")                                                                                                                    
# else:
#     console.log("The above is not in docs2!")                                                                                                              
#     countfinalDocs[count] = docs[i]
#     count = count + 1
    
# 	# finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 })                                                                        
# 	# console.log("Final docs " + finalDocs.length);

# distribution = {}
# seen_patients = []
#     # we compute the percentage breakdown of the types by element and return the result in a JSON blob
# for i in range(finalDocs.length):
# 	tmp = finalDocs[i]
		
# 	if (seen_patients.index(String(tmp["patient_id"])) == -1):
#         	# add the unseen patient ID to the list of seen. We only want to count on unique patients not unique records                                                 
# 		seen_patients.push(tmp["patient_id"])
				    
# for key in tmp:
			
# 	if (key != "_id" and key != "patient_id"):
# 		vals = tmp[key]
					            
# 	if (type!= "string" and type != "number"):
			
# 		for v in vals:
# 			console.log(vals[v])

# 	if (vals[v] in distribution):
# 		val = distribution[vals[v]]
# 		val = val + 1
# 		distribution[vals[v]] = val
# 	else:
# 		distribution[vals[v]] = 1
# 					# some physician entries have _. We get rid of them
# 		vals = vals.split('_').join('')  
				
# 	if (vals in distribution):
# 		val = distribution[vals]
# 		val = val + 1
# 		distribution[vals] = val
    
# 	else: 
# 		distribution[vals] = 1

# 	finalDistribution = {}
				
# 				# compute the distribution for the selected query and sort the keys by descending order of counts. Needed for outputting for those keys the counts for rest of cohort
# countdistribution = {}
# seen_patients = []
                                                                              
# for i in range(countfinalDocs.length):
#     tmp = countfinalDocs[i]

# if (seen_patients.index(String(tmp["patient_id"])) == -1):
#     # add the unseen patient ID to the list of seen. We only want to count on unique patients not unique records                                    
# 	seen_patients.push(tmp["patient_id"])
			
# for key in tmp:
#     if (key != "_id" and key != "patient_id"):
#         vals = tmp[key]

#     if (type!= "string" and type != "number"):
#         for v in vals:
#         	console.log(vals[v])                                                                                                                         

#     	if (vals[v] in countdistribution):
# 			val = countdistribution[vals[v]]
#         	val = val + 1
#         	countdistribution[vals[v]] = val
# 		else:
                            	
# 				countdistribution[vals[v]] = 1
                
# 				vals = vals.split('_').join('');  //some physician entries have _. We get rid of them                                                                
                                                
# 	if (vals in countdistribution):
#         val = countdistribution[vals]
#         val = val + 1
#         countdistribution[vals] = val
# 	else:
#         countdistribution[vals] = 1
                		    

# 	# keysSorted = Object.keys(countdistribution).sort(function(a,b){return countdistribution[b]-countdistribution[a]});

# 	ind = 1
# 	for (k in keysSorted):

				   
# 				    if (Object.keys(distribution).index(keysSorted[k]) > -1):
# 				        finalDistribution[keysSorted[k]] = distribution[keysSorted[k]]
# 				    else:
# 				        finalDistribution[keysSorted[k]] = 0
				

# 				    if (ind >= numTerms):
# 						break;
				    

# 				    ind = ind + 1


# 				console.log(finalDistribution)
# 				# return res.json(JSON.stringify(finalDistribution))
# 				res.setHeader("Access-Control-Allow-Origin", "*")
# 				res.setHeader('Content-Type', 'application/json')
# 				return res.json(finalDistribution)

'''
    //returns the distribution of counts in everything outside of submitted query. also takes in the number to return
    app.get("/othercountdistribution", function(req, res) {
	    var type;
            var inclusion;
            var exclusion;
	    var tmp;
	    var vals;
	    var numTerms;
	    var ind;
	    var other_inclusion = "all";
	           
	    if(!req.query.type || !req.query.num || !req.query.collectionName) {
                return res.send({"status": "error", "message": "missing parameters! [type] [num]"});

            } else {
                //initialize inclusion, exclusion, fields                                                                                                                                         
                if (req.query.inclusion) {
                    inclusion = req.query.inclusion;
                } else {
                    inclusion = "";
                }

                if (req.query.exclusion) {
                    exclusion = req.query.exclusion;
                } else {
                    exclusion = "";
                }

                type = req.query.type + String(",patient_id");
		numTerms = parseInt(req.query.num);

		findDocuments(db, umls_db, type, inclusion, "inclusion", req.query.collectioName, "false", function(docs) {
                        console.log(docs.length);
                        findDocuments(db, umls_db, type, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
                                console.log(docs2.length);

				findDocuments(db, umls_db, type, other_inclusion, "inclusion", req.query.collectionName, "false", function(docs3) {
				    console.log(docs3.length);

                                var docs2_ids = [];
				var docs_ids = [];


                                for (i = 0; i < docs2.length; i++) {
                                    docs2_ids[i] = String(docs2[i]._id);
                                }

				for (i = 0; i < docs.length; i++) {
                                    docs_ids[i] = String(docs[i]._id);
                                }

                                //console.log("Length of docs2_ids " + docs2_ids.length);                                                                                    
                                var count = 0;
                                finalDocs = [];
                                for (i = 0; i < docs3.length; i++) {
                                    // console.log(docs[i]._id);

				    if (docs_ids.indexOf(String(docs3[i]._id)) > -1) {
                                        //console.log("The above is in docs2!");
					if (docs2_ids.indexOf(String(docs3[i]._id)) > -1) {
					    finalDocs[count] = docs3[i];
                                            count = count + 1;
					} 

				    } else {

                                        //console.log("The above is not in docs2!");                                                                                           
					finalDocs[count] = docs3[i];
                                        count = count + 1;
                                    }
                                }

				count = 0;
                                countfinalDocs = []; //docs of diseases that fit inclusion/exclusion criteria. we get this to get the list of type values for the qualified query                     

				for (i = 0; i < docs.length; i++) {
                                    // console.log(docs[i]._id);                                                                                                                                     
				    if (docs2_ids.indexOf(String(docs[i]._id)) > -1) {
                                        //console.log("The above is in docs2!");                                                                                                                       
				    } else {
                                        //console.log("The above is not in docs2!");                                                                                                                
                                        countfinalDocs[count] = docs[i];
                                        count = count + 1;
                                    }
                                }



                                //finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 });                                                                          
				console.log("Final docs " + finalDocs.length);

				var distribution = {};
				var seen_patients = [];
                                //we compute the percentage breakdown of the types by element and return the result in a JSON blob
				for (i = 0; i < finalDocs.length; i++) {
				    tmp = finalDocs[i];
				    
				    if (seen_patients.indexOf(String(tmp["patient_id"])) == -1) {
                                        //add the unseen patient ID to the list of seen. We only want to count on unique patients not unique records                                                 
					seen_patients.push(tmp["patient_id"]);
				    
                                    for (var key in tmp) {
					if (key != "_id" && key != "patient_id") {
					    vals = tmp[key];
					            
					    if (typeof vals != "string" && typeof vals != "number") { 
						for (var v in vals) {
						    //console.log(vals[v]);

						    if (vals[v] in distribution) {
							val = distribution[vals[v]];
							val = val + 1;
							distribution[vals[v]] = val;

						    } else {
							distribution[vals[v]] = 1;
						    }
						}

					    }   else {

						vals = vals.split('_').join('');  //some physician entries have _. We get rid of them
						if (vals in distribution) {
                                                    val = distribution[vals];
                                                    val = val + 1;
                                                    distribution[vals] = val;

                                                } else {
                                                    distribution[vals] = 1;
                                                }
					    }
					}
				    }
				    }
                                }

				var finalDistribution = {};
				
				//compute the distribution for the selected query and sort the keys by descending order of counts. Needed for outputting for those keys the counts for rest of cohort
				var countdistribution = {};
				seen_patients = [];
                                                                              
                                for (i = 0; i < countfinalDocs.length; i++) {
                                    tmp = countfinalDocs[i];

				    if (seen_patients.indexOf(String(tmp["patient_id"])) == -1) {
                                        //add the unseen patient ID to the list of seen. We only want to count on unique patients not unique records                                    
					seen_patients.push(tmp["patient_id"]);


                                    for (var key in tmp) {
                                        if (key != "_id" && key != "patient_id") {
                                            vals = tmp[key];

                                            if (typeof vals != "string" && typeof vals != "number") {
                                                for (var v in vals) {
                                                    //console.log(vals[v]);                                                                                                                          

                                                    if (vals[v] in countdistribution) {
                                                        val = countdistribution[vals[v]];
                                                        val = val + 1;
                                                        countdistribution[vals[v]] = val;

                                                    } else {
                                                        countdistribution[vals[v]] = 1;
                                                    }
                                                }

                                            }   else {
						vals = vals.split('_').join('');  //some physician entries have _. We get rid of them                                                                
                                                if (vals in countdistribution) {
                                                    val = countdistribution[vals];
                                                    val = val + 1;
                                                    countdistribution[vals] = val;

                                                } else {
                                                    countdistribution[vals] = 1;
                                                }
                                            }
                                        }
                                    }
				    }
                                }

						    

				keysSorted = Object.keys(countdistribution).sort(function(a,b){return countdistribution[b]-countdistribution[a]});

				ind = 1;
				for (k in keysSorted) {

				   
				    if (Object.keys(distribution).indexOf(keysSorted[k]) > -1) {
				        finalDistribution[keysSorted[k]] = distribution[keysSorted[k]];
				    } else {
				        finalDistribution[keysSorted[k]] = 0;
				    }

				    if (ind >= numTerms) {
					break;
				    }

				    ind = ind + 1;

				}

				console.log(finalDistribution);
				//return res.json(JSON.stringify(finalDistribution));
				res.setHeader("Access-Control-Allow-Origin", "*");
				res.setHeader('Content-Type', 'application/json');
				return res.json(finalDistribution);
                            });

			});
                    });

            }



	});


'''

# def socialmedia(request):

#     	if (request.GET["inclusion"]):
#         	inclusion = request.GET["inclusion"]
        # else:
#             inclusion = ""

#         if (request.GET["exclusion"])) {
#             exclusion = request.GET["exclusion"]
#         else:
#             exclusion = ""

# 	fields = request.GET["fields"]
# 		# insertDocuments(db,function() {                                                                                                                                            
# 		# findDocuments(db, umls_db, fields, inclusion, "inclusion", "socialmedia", "false", function(docs) {
#         #                 console.log(docs.length);
#         #                 findDocuments(db, umls_db, fields, exclusion, "exclusion", "socialmedia", "false", function(docs2) {
#         #                         console.log(docs2.length);

#     docs2_ids = []
#     for i in range(docs2.length):
#         docs2_ids[i] = String(docs2[i]._id)
# 		console.log("Length of docs2_ids " + docs2_ids.length);                                                                      
           
# 	count = 0
#     finalDocs = []
# 	for i in range(docs.length):
#         console.log(docs[i]._id)                                                                                                                                  

#     if (docs2_ids.index(String(docs[i]._id)) > -1):
#         console.log("The above is in docs2!")                                                                                                                
# 	else:
#         console.log("The above is not in docs2!") 

# 	finalDocs[count] = docs[i]
#     count = count + 1
#     # finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 });                                                                        
# 				console.log("Final docs " + finalDocs.length)

#                 # we return docs - docs2                   
# 	res.setHeader("Access-Control-Allow-Origin", "*")
# 	res.setHeader('Content-Type', 'application/json')
# 	return res.json(finalDocs)

'''
    app.get("/socialmedia", function(req, res) {
            var fields;
            var inclusion;
            var exclusion;
	    
	    if(!req.query.fields) {
                return res.send({"status": "error", "message": "missing parameters! [field]"});

            } else {
                //initialize inclusion, exclusion, fields                                                                                                                                       
		if (req.query.inclusion) {
                    inclusion = req.query.inclusion;
                } else {
                    inclusion = "";
                }

                if (req.query.exclusion) {
                    exclusion = req.query.exclusion;
                } else {
                    exclusion = "";
                }

                fields = req.query.fields;
		// insertDocuments(db,function() {                                                                                                                                            
		findDocuments(db, umls_db, fields, inclusion, "inclusion", "socialmedia", "false", function(docs) {
                        console.log(docs.length);
                        findDocuments(db, umls_db, fields, exclusion, "exclusion", "socialmedia", "false", function(docs2) {
                                console.log(docs2.length);

                                docs2_ids = [];
                                for (i = 0; i < docs2.length; i++) {
                                    docs2_ids[i] = String(docs2[i]._id);
                                }

				//console.log("Length of docs2_ids " + docs2_ids.length);                                                                      
           
				var count = 0;
                                finalDocs = [];
                                for (i = 0; i < docs.length; i++) {
                                    // console.log(docs[i]._id);                                                                                                                                   

                                    if (docs2_ids.indexOf(String(docs[i]._id)) > -1) {
                                        //console.log("The above is in docs2!");                                                                                                                 

                                    } else {
                                        //console.log("The above is not in docs2!"); 
					finalDocs[count] = docs[i];
                                        count = count + 1;
                                    }
                                }


                                //finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 });                                                                        
				console.log("Final docs " + finalDocs.length);

                                //we return docs - docs2                   
				res.setHeader("Access-Control-Allow-Origin", "*");
                                res.setHeader('Content-Type', 'application/json');
				return res.json(finalDocs);
                            });
                    });

            }
        });
'''

# def ct(request):
# 		ct_id = request.GET["id"]
# 		fields = request.GET["fields"]

# 		findCT(db, ct_id, fields, function(docs)

	# res.setHeader("Access-Control-Allow-Origin", "*")
	# res.setHeader('Content-Type', 'application/json')
	# return res.json(docs))

# def tablequery(request):
# 		if request.GET["inclusion"]
# 		    inclusion = request.GET["inclusion"]
# 		    inclusion = ""

# 		if request.GET["exclusion"]
# 		    exclusion = request.GET["exclusion"]
# 		else
# 		    exclusion = ""
		
# 		if (request.GET["fields"] == "all"):
# 		    fields = "";

# 		else
# 		    fields = request.GET["fields"]
		
# 		# insertDocuments(db,function() {

# 		# findDocuments(db, umls_db, fields, inclusion, "inclusion", req.query.collectionName, "false", function(docs) {
# 		# 	console.log(docs.length)     
# 		# 	findDocuments(db, umls_db, fields, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
# 		# 		console.log(docs2.length)
				
# docs2_ids = []
# for i in range(docs2.length):
# 	docs2_ids[i] = String(docs2[i]._id)

# # console.log("Length of docs2_ids " + docs2_ids.length)

# 	var count = 0
# 	var finalDocs = []
# 	for i in range(docs.length):
# 	#console.log(docs[i]._id)
				        
# 	if (docs2_ids.indexOf(String(docs[i]._id)) > -1):
# 	# console.log("The above is in docs2!")
# 	# console.log("Omitting: " + String(docs[i].event_id))				  
# 	else:
# 	# console.log("The above is not in docs2!")
# 	# console.log("Including: " + String(docs[i].event_id))
# 		finalDocs[count] = docs[i]
#         count = count + 1
# 		# finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 })
# 				console.log("Final docs " + finalDocs.length)
# 				var docsToSend = []

# for i in range(finalDocs.length):
# tmp = finalDocs[i]
## var tmpOut = {}
#for (var key in tmp):
#	if (key != "_id"):
#   	vals = tmp[key]
# # console.log(vals)
# console.log(typeof vals)

# if (type vals != "string" and type vals != "number"):
# vals = vals.join(", ")
# tmpOut[key] = vals

#docsToSend[i] = tmpOut
				    
# 				# we return docs - docs2
# res.setHeader("Access-Control-Allow-Origin", "*")
# res.setHeader('Content-Type', 'application/json')
# return res.json(docsToSend)

# def getsuggestions(request):
	
# 	if(request.GET["typed"]:
#         return res.send("status": "error", "message": "missing parameters! [typed]")
# 	else:
#         var PythonShell = require('python-shell')
#         mode: 'text',
#         pythonPath: '//anaconda/bin/python'
#         pythonOptions: ['-u']
#         scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
#         //args: ["text", "100-01", "111", req.body.emr, "\n"]                                                                                                                           
# 		args: request.GET["typed"]
# 		# console.log(req.body.emr); 

# 		PythonShell.run('convert_input.py', options, function (err, results)
#     	if (err) throw err:
#     	# results is an array consisting of messages collected during execution                                                                                                                                                                                                                        
#         console.log('results: %j', results)

#     	res.setHeader("Access-Control-Allow-Origin", "*")
#         res.setHeader('Content-Type', 'application/json')
#         return res.json(results[0])

'''
    //returns the suggestions for queries given the typed words
    app.get("/getsuggestions", function(req, res) {

            if(!req.query.typed) {
                return res.send({"status": "error", "message": "missing parameters! [typed]"});

            } else {

                var PythonShell = require('python-shell');

                var options = {
                    mode: 'text',
                    pythonPath: '//anaconda/bin/python',
                    pythonOptions: ['-u'],
                    scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
                    //args: ["text", "100-01", "111", req.body.emr, "\n"]                                                                                                                           
		    args: [req.query.typed]
                };

                //console.log(req.body.emr); 

		PythonShell.run('convert_input.py', options, function (err, results) {
                        if (err) throw err;
                        // results is an array consisting of messages collected during execution                                                                                                                                                                                                                        
                        console.log('results: %j', results);

                        res.setHeader("Access-Control-Allow-Origin", "*");
                        res.setHeader('Content-Type', 'application/json');
                        return res.json(results[0]);
                    });
            }
        });
'''

