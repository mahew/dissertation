import pymongo
import datetime
import os
from device import iot_device
from bson.objectid import ObjectId

class api_connection():
    logged_count = 0
    connection_string = os.environ.get("POETRY_CONN_STRING")
    if connection_string == None:
        raise ValueError("No valid connection string present, set connection string in POETRY_CONN_STRING")
    client = pymongo.MongoClient(connection_string + "?retryWrites=true&w=majority")
    db = client.development
    vehicles = []

    def __init__(self, verbose):
        self.verbose = verbose
        self.verbose = True
        self.device = iot_device()
        self.device_id = str(self.device.mac_address)
        
        device = self.db.devices.find_one({"_id": self.device_id})

        if device == None:
            print("Device was not found, please set up this device.")
            device_name = input("Device Name: ")
            location_string = input("Location: ")
            device = {
                "_id": str(self.device.mac_address),
                "deviceName": device_name,
                "location": location_string,
                "lastUpdated": datetime.datetime.now(datetime.timezone.utc)
            }
            
            self.db.devices.insert_one(device)

        time_started = datetime.datetime.now(datetime.timezone.utc)
        self.session = {"deviceId": self.device_id, "timeStarted": time_started}
        self.session_id = self.db.deviceSessions.insert_one(self.session).inserted_id

        print("Session #", self.session_id, " Started: ", time_started)

    def insert_vehicle(self, vehicle):
        self.db.vehicles.insert({"sessionId": ObjectId(self.session_id), "vehicleType": vehicle.class_name, 
            "direction": vehicle.direction, "timeCrossed": vehicle.counted}, w=0)

    def close(self):
        time_ended = datetime.datetime.now(datetime.timezone.utc)
        self.db.deviceSessions.update_one({'_id': ObjectId(self.session_id)}, {"$set": {"timeEnded": time_ended}})
        
        if self.verbose == True:
            total_up = self.db.vehicles.count_documents(
                { "$and": [ { "direction":  "up" }, {"sessionId": self.session_id} ] }
            )

            total_down = self.db.vehicles.count_documents(
                { "$and": [ { "direction":  "down" }, {"sessionId": self.session_id} ] }
            ) 

            print("Session #", self.session_id, " UP: ", total_up, " DOWN: ", total_down , " Ended: ", time_ended)







