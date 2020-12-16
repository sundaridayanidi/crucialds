import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""                                                                                                                           
In this script we take an input EMR and structure and store into patients.rest (rest2 for testing)                            
"""

from pymongo import MongoClient


#deletes all records for given patient ID
def delete(db, event_id, collectionName):
	event_id = event_id 
	result = db[collectionName].delete_many({"event_id" : event_id})

	return result.deleted_count


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Run as python delete.py [eventID] [collection]"
        sys.exit(-1)


    client = MongoClient()
    db = client.patients
    event_id = sys.argv[1]
    collectionName = sys.argv[2]

    count = delete(db, event_id, collectionName)

    print count
