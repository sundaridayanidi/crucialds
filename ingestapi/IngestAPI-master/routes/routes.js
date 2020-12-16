var fs = require('fs');
var path = require( 'path' );
var process = require( "process" );

var appRouter = function(app, db, umls_db, assert, len) {

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



    app.get("/distribution", function(req, res) {
	    var type;
            var inclusion;
            var exclusion;
	    var tmp;
	    var vals;
	   
	    if(!req.query.type || !req.query.collectionName) {
                return res.send({"status": "error", "message": "missing parameters! [type]"});

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

                type = req.query.type;
 

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

				distribution = {};
                                //we compute the percentage breakdown of the types by element and return the result in a JSON blob
				for (i = 0; i < finalDocs.length; i++) {
				    tmp = finalDocs[i];
                                    for (var key in tmp) {
					if (key != "_id") {
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


				var num_patients = finalDocs.length;
				var finalDistribution = {};
				//var total  = 0;

				for (var i in distribution) {
				    val = distribution[i];
				    val = (val * 1.0)/num_patients;
				    distribution[i] = val;
				    //total = total + val;
				}
				
				//console.log(distribution);
				//console.log("The sum of the percentages is " + String(total));

				keysSorted = Object.keys(distribution).sort(function(a,b){return distribution[b]-distribution[a]});

				var ind = 1;
				for (k in keysSorted) {
				    finalDistribution[keysSorted[k]] = parseFloat(parseFloat(Math.round(distribution[keysSorted[k]] * 100) / 100).toFixed(2));

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



    //given the ct id and fields, returns the elements
    app.get("/ct", function(req, res) {
	    var fields;
	    var ct_id;

	    if(!req.query.fields || !req.query.id) {
                return res.send({"status": "error", "message": "missing parameters! [id] [field]"});

            } else {
		ct_id = req.query.id;
		fields = req.query.fields;

		findCT(db, ct_id, fields, function(docs) {
			res.setHeader("Access-Control-Allow-Origin", "*");
			res.setHeader('Content-Type', 'application/json');
			return res.json(docs);

		    })
	    }
	
	});


    //same as query but if there is a list, makes the list a string
    app.get("/tablequery", function(req, res) {
	    var fields;
	    var inclusion;
	    var exclusion;
	     
	    if(!req.query.fields || !req.query.collectionName) {
		return res.send({"status": "error", "message": "missing parameters! [field] [collection] [username]"});

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
		

		if (req.query.fields == "all") {
		    fields = "";

		} else {
		    fields = req.query.fields;
		}
		// insertDocuments(db,function() {

		findDocuments(db, umls_db, fields, inclusion, "inclusion", req.query.collectionName, "false", function(docs) {
			console.log(docs.length);       
			findDocuments(db, umls_db, fields, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
				console.log(docs2.length);
				
				docs2_ids = [];
				for (i = 0; i < docs2.length; i++) {
				    docs2_ids[i] = String(docs2[i]._id);
				}

				//console.log("Length of docs2_ids " + docs2_ids.length);

				var count = 0;
				var finalDocs = [];
				for (i = 0; i < docs.length; i++) {
				    // console.log(docs[i]._id);
				        
				    if (docs2_ids.indexOf(String(docs[i]._id)) > -1) {
					//console.log("The above is in docs2!");
					//console.log("Omitting: " + String(docs[i].event_id));
					  
				    } else {
					//console.log("The above is not in docs2!");
					//console.log("Including: " + String(docs[i].event_id));
					finalDocs[count] = docs[i];
                                        count = count + 1;
				    }
				}


				//finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 });
				console.log("Final docs " + finalDocs.length);
				var docsToSend = [];

				for (i = 0; i < finalDocs.length; i++) {
                                    tmp = finalDocs[i];
				    var tmpOut = {};
                                    for (var key in tmp) {
                                        if (key != "_id") {
                                            vals = tmp[key];
					    console.log(vals);
					    console.log(typeof vals)

                                            if (typeof vals != "string" && typeof vals != "number") {
						vals = vals.join(", ");
					    }

					    tmpOut[key] = vals;
					}
				    }

				    docsToSend[i] = tmpOut;
				}
				    
				//we return docs - docs2
				res.setHeader("Access-Control-Allow-Origin", "*");
                res.setHeader('Content-Type', 'application/json');
				return res.json(docsToSend);
			    });
		    }); 

	    }
	});


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


    //returns the graph image corresponding to the keyword and emr. Once the images are loaded into the DB change this to query the DB and do the search here
    app.get("/patientsearch", function(req, res) {

	    if(!req.query.keyword || !req.query.patient_id) {
                return res.send({"status": "error", "message": "missing parameters! [keyword] [patient id]"});

            } else {
		
		var PythonShell = require('python-shell');

                var options = {
                    mode: 'text',
                    pythonPath: '//anaconda/bin/python',
                    pythonOptions: ['-u'],
                    scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
                    //args: ["text", "100-01", "111", req.body.emr, "\n"]                                                                                                                                
                    args: [req.query.keyword, req.query.patient_id]
                };

                //console.log(req.body.emr);                                                                                                                                                             

                PythonShell.run('keyword_search.py', options, function (err, results) {
                        if (err) throw err;
                        // results is an array consisting of messages collected during execution                                                                                                         
                        console.log('results: %j', results);

			res.setHeader("Access-Control-Allow-Origin", "*");
			res.setHeader('Content-Type', 'application/json');
			return res.sendFile(results[0]);
                    });
            }

		
	

	});


    //returns the community image corresponding to the type and emr. Once the images are loaded into the DB change this to query the DB and do the search here
    app.get("/patientsimilarity", function(req, res) {

	    if(!req.query.type || !req.query.patient_id) {
                return res.send({"status": "error", "message": "missing parameters! [type] [patient id]"});

            } else {
		
		var PythonShell = require('python-shell');

                var options = {
                    mode: 'text',
                    pythonPath: '//anaconda/bin/python',
                    pythonOptions: ['-u'],
                    scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
                    //args: ["text", "100-01", "111", req.body.emr, "\n"]                                                                                                                                
                    args: [req.query.type, req.query.patient_id]
                };

                //console.log(req.body.emr);                                                                                                                                                             

                PythonShell.run('patient_similarity.py', options, function (err, results) {
                        if (err) throw err;
                        // results is an array consisting of messages collected during execution                                                                                                         
                        console.log('results: %j', results);

			res.setHeader("Access-Control-Allow-Origin", "*");
			res.setHeader('Content-Type', 'application/json');
			return res.sendFile(results[0]);
                    });
            }

	    
	    

	});

    
    //returns the type community image corresponding to the type and emr. Once the images are loaded into the DB change this to query the DB and do the search here
    app.get("/patientsimilaritytype", function(req, res) {

	    if(!req.query.type || !req.query.patient_id) {
                return res.send({"status": "error", "message": "missing parameters! [type] [patient id]"});

            } else {
		
		var PythonShell = require('python-shell');

                var options = {
                    mode: 'text',
                    pythonPath: '//anaconda/bin/python',
                    pythonOptions: ['-u'],
                    scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
                    //args: ["text", "100-01", "111", req.body.emr, "\n"]                                                                                                                                
                    args: [req.query.type, req.query.patient_id]
                };

                //console.log(req.body.emr);                                                                                                                                                             

                PythonShell.run('patient_similarity.py', options, function (err, results) {
                        if (err) throw err;
                        // results is an array consisting of messages collected during execution                                                                                                         
                        console.log('results: %j', results);

			res.setHeader("Access-Control-Allow-Origin", "*");
			res.setHeader('Content-Type', 'application/json');
			return res.sendFile(results[1]);
                    });
            }

	        
	        

	});


    //returns the graph text corresponding to the keyword and emr. Once the images are loaded into the DB change this to query the DB and do the search here
    app.get("/patientsearchtext", function(req, res) {

	    if(!req.query.keyword || !req.query.patient_id) {
                return res.send({"status": "error", "message": "missing parameters! [keyword] [patient id]"});

            } else {
		
		var PythonShell = require('python-shell');

                var options = {
                    mode: 'text',
                    pythonPath: '//anaconda/bin/python',
                    pythonOptions: ['-u'],
                    scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
                    //args: ["text", "100-01", "111", req.body.emr, "\n"]                                                                                                                                
                    args: [req.query.keyword, req.query.patient_id]
                };

                //console.log(req.body.emr);                                                                                                                                                             

                PythonShell.run('keyword_search.py', options, function (err, results) {
                        if (err) throw err;
                        // results is an array consisting of messages collected during execution                                                                                                         
                        console.log('results: %j', results);

			res.setHeader("Access-Control-Allow-Origin", "*");
			res.setHeader('Content-Type', 'application/json');
			return res.sendFile(results[1]);
                    });
            }

	    
	    

	});


    //returns the global view given the patient ID. aggregates all the types 
    app.get("/patientview", function(req, res) {
	    var fields;
	    var inclusion;
	    var exclusion;
	         
	    if(!req.query.inclusion || !req.query.collectionName) {
		return res.send({"status": "error", "message": "missing parameters! [inclusion] [collection]"});

	    } else {
		//initialize inclusion, exclusion, fields
		if (req.query.inclusion) {
		    inclusion = req.query.inclusion;
		} 

		if (req.query.exclusion) {
		    exclusion = req.query.exclusion;
		} else {
		    exclusion = "";
		}
		

		fields = "";
		// insertDocuments(db,function() {

		findDocuments(db, umls_db, fields, inclusion, "inclusion", req.query.collectionName, "false", function(docs) {
			console.log(docs.length);       
			findDocuments(db, umls_db, fields, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
				console.log(docs2.length);
				
				docs2_ids = [];
				for (i = 0; i < docs2.length; i++) {
				    docs2_ids[i] = String(docs2[i]._id);
				}

				//console.log("Length of docs2_ids " + docs2_ids.length);

				var count = 0;
				var finalDocs = [];
				for (i = 0; i < docs.length; i++) {
				    //console.log(docs[i]._id);
				            
				    if (docs2_ids.indexOf(String(docs[i]._id)) > -1) {
					//console.log("The above is in docs2!");
					  
				    } else {
					//console.log("The above is not in docs2!"); 
					finalDocs[count] = docs[i];
                                        count = count + 1;
				    }
				}


				//finalDocs = docs.filter(function(x) { return docs2.indexOf(x) < 0 });
				//console.log("Final docs " + finalDocs.length);
				var docsToSend = {};

				for (i = 0; i < finalDocs.length; i++) {
                                    tmp = finalDocs[i];
				    //console.log(tmp);
                                    for (var key in tmp) {

                                        if (key != "_id" && key.indexOf(":") <= -1 && key.indexOf("Line") <= -1 && key.indexOf("body") <= -1) {
                                            vals = tmp[key];

					    console.log(key);

                                            if (typeof vals != "string" && typeof vals != "number" && vals != null) {
						vals = vals.join(", ");
					    }

					    if (key in docsToSend) {
						val = docsToSend[key];
						val = val + ", " + String(vals);
						docsToSend[key] = val;

					    } else {
						console.log(String(vals));
						docsToSend[key] = String(vals);
					    }

					}
				    }

				}

				//uniques the elements for each type
				var uniquedocsToSend = {};

				for (var key in docsToSend) {
				    val = docsToSend[key];
				    val = val.split(",");
				    new_val = [];

				    for (i = 0; i < val.length; i++) {
					element = val[i].trim();
					if (new_val.indexOf(element) <= -1) {
					    new_val.push(element);
					}
				    }

				    new_val = new_val.join(", ");
				    uniquedocsToSend[key] = new_val;
				}

				console.log("uniquedocsToSend length " + uniquedocsToSend.length);
				    
				//we return docs - docs2
				res.setHeader("Access-Control-Allow-Origin", "*");
                                res.setHeader('Content-Type', 'application/json');
				return res.json(uniquedocsToSend);
			    });
		    }); 

	    }
	});

    
    app.get("/query", function(req, res) {
	    var fields;
	    var inclusion;
	    var exclusion;
	 
	    if(!req.query.fields || !req.query.collectionName) {
		return res.send({"status": "error", "message": "missing parameters! [field] [collection]"});

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
		

		if (req.query.fields == "all") {
		    fields = "";

		} else {
		fields = req.query.fields;
		}
		    // insertDocuments(db,function() {

		findDocuments(db, umls_db, fields, inclusion, "inclusion", req.query.collectionName, "false", function(docs) {
			//console.log("IN FIND DOCUMENTS FOR QUERY: " + docs.length);       
			findDocuments(db, umls_db, fields, exclusion, "exclusion", req.query.collectionName, "false", function(docs2) {
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
    
}

var insertDocuments = function(db, fields, callback) {
	// Get the documents collection
	var collection = db.collection('documents');
	// Insert some documents
	collection.insertMany([
			       {a : 1}, {a : 2}, {a : 3}
			       ], function(err, result) {
				  assert.equal(err, null);
				  assert.equal(3, result.result.n);
				  assert.equal(3, result.ops.length);
				  console.log("Inserted 3 documents into the collection inside routes.js!");
				  callback(result);
			      });
}


//couldnt get this method to work in javascript
var constructQuery = function(fields, inclusion, query_type, umls_db, callback) {
    //construct query
    fields = fields.split('_');
    inclusion = inclusion.split('_');
    var new_fields = ""; 
    var new_inclusion = "";
    var query =  'collection.find({';
    
    for (f in fields) {
	if (fields[f].indexOf("id") > -1) {
	    new_fields = new_fields + "_" + fields[f];
	} else {
	    new_fields = new_fields + " " + fields[f];
	}
    }

    for (f in inclusion) {
        if (inclusion[f].indexOf("id") > -1) {
            new_inclusion = new_inclusion + "_" + inclusion[f];
        } else {
            new_inclusion = new_inclusion + " " + inclusion[f];
        }
    }

    fields = new_fields.substring(1, new_fields.length);
    inclusion = new_inclusion.substring(1, new_inclusion.length);

    fields = fields.split(",");
    //inclusion = inclusion.split('_').join(' ');

    //this keeps {} as the inclusion for mongo query returning all the fields
    if (inclusion != "all") {

    inclusion = inclusion.split(",");
    var boolean_operator;

    if (query_type == "inclusion") {
	boolean_operator = '"$and": [';

    } else {
	boolean_operator = '"$or": [';
    }

    if (inclusion.length > 0) {
	query = query + boolean_operator;
    } else {
	query = query + "None: None";
    }

    }
    //call the loopInclusion here
    loopInclusion(umls_db, inclusion, query, function(ret_query) {
	    if (inclusion.length > 0 && inclusion != "all") {
		query = ret_query.substring(0, ret_query.length - 1);
		query = query + ']},';
	    } else {
		query = query + '},'
	    }

	    query = query + '{';

	    if (fields != "") {
		//query = query + '"_id": 0, ';                                                                                                                                                       
		//populate fields                                                                                                                                                                     
		for (i = 0; i < fields.length; i++) {
		    query = query + '"' + fields[i] + '": 1,';
		}

		query = query.substring(0, query.length - 1);
	    }



	    query = query + '})';


	    query = query + '.toArray(function(err, docs) {\n';
	    //assert.equal(err, null);\                                                                                                                                                                          
	    query = query + 'console.log("Found the following records in routes.js!");\n';
	    query = query + 'callback(docs);\n';
	    query = query + '});';

	    console.log(query);
	    callback(query);

	});

 }



var x = 0;
var loopInclusion = function(umls_db, inclusion, query, callback) {
    var term = inclusion[x];
 
    if (term.indexOf(":") > -1) {
    	term = term.split(":");
	term = term[1];
    }	

    //look up synonymous terms here                                                                                                                                                          
    findSynonyms(umls_db, term, function(synonyms) {

	var arg = inclusion[x];

	    if (arg.indexOf(">") > -1) {
		arg = arg.split(">");

		if (arg[0].indexOf("date") > -1) {
		    query = query + '{"' + arg[0] + '": {"$gt": new Date("' + arg[1] + '")}},';

		} else {
		    query = query + '{"' + arg[0] + '": {"$gt": ' + arg[1] + '}},';
		}

	    } else if (arg.indexOf("<") > -1) {
		arg = arg.split("<");

		if (arg[0].indexOf("date") > -1) {
		    query = query + '{"' + arg[0] + '": {"$lt": new Date("' + arg[1] + '")}},';

		} else {
		    query = query + '{"' + arg[0] + '": {"$lt": ' + arg[1] + '}},';
		}

	    } else {
		arg = arg.split(":");

		if (arg[0].indexOf("date") > -1) {
		    query = query + '{"' + arg[0] + '": new Date("' + arg[1] + '")},';

		} else {
		    //query = query + '{"' + arg[0] + '": "' + arg[1] + '"},';   
		    //console.log("The length of synonyms is " + Object.keys(synonyms).length);                                                                                                          
		    if (Object.keys(synonyms).length > 0) {
			query = query + '{"$or": [{"' + arg[0] + '": "' + arg[1] + '"},';
			for (type in synonyms) {
			    //console.log("The type is " + type);                                                                                                                                      
			    //console.log("The synonym is " + synonyms[type]);                                                                                                                         
			    query = query + '{"' + type + '": "' + synonyms[type] + '"},';
			}

		   query = query.substring(0, query.length - 1);
		   query = query + ']},';
		   console.log("The query is " + query);                                                                                                                                          

		    } else {
			query = query + '{"' + arg[0] + '": "' + arg[1] + '"},';
		    }
		}
	    }
	


	    // set x to next item
	    x++;

	    // any more items in array? continue loop
	    if(x < inclusion.length) {
		loopInclusion(inclusion);   
	    }

	    callback(query);
	});


}

 var findTerms = function(db, cui, collection, callback) {
      var cursor = collection.find({"CUI": cui}, {"TERM": 1});
      var terms = [];
	cursor.each(function(err, doc) {
	    if (err)
	        callback(err);

	    if (doc) {
		//console.log('Fetched:', doc.TERM);
		terms.push(doc.TERM);
	    } else {
	        // at the end of cursor, return the data through callback                                                                                                                              
	        callback(null, terms);
	    }
	});

	}

 var findCUIs = function(db, term, collection, callback) {
      var cursor = collection.find({"TERM": term}, {"CUI": 1});
      var cuis = [];
      cursor.each(function(err, doc) {
	      if (err)
		  callback(err);

	      if (doc) {
		  //console.log('Fetched:', doc.CUI);
		  cuis.push(doc.CUI);
	      } else {
		  // at the end of cursor, return the data through callback 
		  callback(null, cuis);
	      }
	  });

  }

  var findTypes = function(db, cui, collection, callback) {
      var cursor = collection.find({"CUI": cui}, {"TYPE": 1});
      var types = [];
      cursor.each(function(err, doc) {
	  if (err)
	      callback(err);

	  if (doc) {
	      //console.log('Fetched:', doc.TYPE);
	      types.push(doc.TYPE);
	  } else {
	      // at the end of cursor, return the data through callback                                                                                                                              
	      callback(null, types);
	  }
      });

      }


  var findSynonyms = function(umls_db, term, callback) {
      var collection = umls_db.collection('lower_mrconso');
      var mrsty_collection = umls_db.collection('lower_mrsty');
      var synonyms = {};
      var type = "";

      findCUIs(umls_db, term, collection, function(err, cuis) {
          if (err)
	      throw err;

	  //console.log("The length of the cuis: " + cuis.length);

	  for (cui in cuis) {
	      findTypes(umls_db, cuis[cui], mrsty_collection, function(err, types) {
		  if (err)
		      throw err;

		  type = types[0];
		  
		  findTerms(umls_db, cuis[cui], collection, function(err, terms) {
		      if (err)
		          throw err;

		      for (i = 0; i < terms.length; i++) {
			  synonyms[type] = terms[i];
			  //console.log("The synonym contains " + type + ": " + terms[i]);
		      }

		      //console.log("The length of synonyms inside the findSynonyms method is " + Object.keys(synonyms).length);
          	      callback(synonyms);

		  });

	      });
	  }

	  //console.log("The length of synonyms inside the findSynonyms method is " + Object.keys(synonyms).length);
          //callback(synonyms);
	  
	  });

	//callback(synonyms);

  }

  //CREATE A NEW FUNCTION HERE FOR CALLING rest.ct STUFF
      var findCT = function(db, ct_id, fields, callback) {
	  var collection = db.collection('ct');
	  var query = 'collection.find(';
	  fields = fields.split('_');
	  var new_fields = "";

	  if (ct_id == "all") {
	      var query =  query + '{"patient_ids": {"$exists": true}}, {';
	  } else {
	      var query =  query + '{"id": "' + ct_id + '"}, {';
	  }

	  for (f in fields) {
	      if (fields[f].indexOf("id") > -1 || fields[f].indexOf("date") > -1 || fields[f].indexOf("converted")) {
		  new_fields = new_fields + "_" + fields[f];
	      } else {
		  new_fields = new_fields + " " + fields[f];
	      }
	  }

	  fields = new_fields.substring(1, new_fields.length);

	  fields = fields.split(",");

	  if (fields != "") {
	      //query = query + '"_id": 0, ';                                                                                                                                                          
	      //populate fields                                                                                                                                                                        
	      for (i = 0; i < fields.length; i++) {
		  query = query + '"' + fields[i] + '": 1,';
	      }

	      query = query.substring(0, query.length - 1);
	  }
	  
	  query = query + '})';
	  query = query + '.toArray(function(err, docs) {callback(docs);});';
	  console.log(query);
	  eval(query);

      }


    //replace this with findDocuments -- difference is we read in output from stdout and load into JSON object then return callback object
    var findEncryptedDocuments = function(db, umls_db, fields, inclusion, query_type, dbType, populate_fields_by_synonym, callback) {
    	if (dbType == "socialmedia") {
			var collection = db.collection('ra');
	 	} else if (dbType == "viedoc") {
			var collection = db.collection('viedoc');
	 	} else if (dbType == "clinical_studio") {
			var collection = db.collection('clinical_studio');
	 	} else {
	    	var collection = db.collection('rest2');

	 	}

	 	var PythonShell = require('python-shell');

	 	var options = {
	     	mode: 'text',
	     	pythonPath: '//anaconda/bin/python',
	     	pythonOptions: ['-u'],
	     	scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
	     	//args: ["text", "100-01", "111", req.body.emr, "\n"]                                                                                                               
	     	args: [fields, inclusion, query_type, populate_fields_by_synonym]
	 	};

	 	//console.log(req.body.emr);                                                                                                                                              
	 	PythonShell.run('construct_query.py', options, function (err, query) {
		 	if (err) throw err;
		 	// results is an array consisting of messages collected during execution                                                                                                  
		 	console.log('query: %j', query[0]);
		 	eval(query[0]);		 
		});


    }
     
    var findDocuments = function(db, umls_db, fields, inclusion, query_type, dbType, populate_fields_by_synonym, callback) {
	// Get the documents collection

	 if (dbType == "socialmedia") {
		var collection = db.collection('ra');
	 } else if (dbType == "viedoc") {
		var collection = db.collection('viedoc');
	 } else if (dbType == "clinical_studio") {
		var collection = db.collection('clinical_studio');
	 } else {
	    var collection = db.collection('rest2');

	 }	

	 /*
	 //var query = constructQuery(fields, inclusion, query_type, umls_db);
	 constructQuery(fields, inclusion, query_type, umls_db, function(query) {
            eval(query);
	});
	 */

	//console.log("Inclusion: " + inclusion);
	 //we call the construct_query script in python instead since its faster and the JS method doesnt work
	 var PythonShell = require('python-shell');

	 var options = {
	     mode: 'text',
	     pythonPath: '//anaconda/bin/python',
	     pythonOptions: ['-u'],
	     scriptPath: '/Users/gangopad/Company/REST/ApysAPI',
	     //args: ["text", "100-01", "111", req.body.emr, "\n"]                                                                                                               
	     args: [fields, inclusion, query_type, populate_fields_by_synonym]
	 };

	 //console.log(req.body.emr);                                                                                                                                              
	 PythonShell.run('construct_query.py', options, function (err, query) {
		 if (err) throw err;
		 // results is an array consisting of messages collected during execution                                                                                                  
		 console.log('query: %j', query[0]);
		 eval(query[0]);		 
	});


	/*
	if (exclusion.length > 0) {
	    var query = constructQuery(fields, exclusion, "docs2");
	    var docs2 = eval(query);
	    var res = [];

		for (i = 0; i < docs2.length; i++) {
		    if (docs.indexOf(docs2[i]) <= -1) {
			res.push(docs2[i]);
		    }
		}

	    callback(res);

	} else {
	    callback(docs);
	}
	*/

	/*
	// Find some documents
	collection.find({"Disease or Syndrome": "obesity"}, {query}).toArray(function(err, docs) {
		//assert.equal(err, null);
		console.log("Found the following records in routes.js!");
		//console.log(docs);
		callback(docs);
	    });
	
	*/
    }

 
module.exports = appRouter;
