class TrackableVehicle():
    def __init__(self, id, label, centroid):
        self.object_id = id
        self.centroids = [centroid]
        self.class_name = label
        self.direction = None
        self.counted = False
        self.correct = None

    def __repr__(self):
        return "ID: {}, Class: {} Direction: {}, Time Counted: {}".format(self.object_id, self.class_name, self.direction, self.counted)

class LabelledTracker():
    def __init__(self, label, tracker):
        self.vehicle_class = label
        self.crl_tracker = tracker