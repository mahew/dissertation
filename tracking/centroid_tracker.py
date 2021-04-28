import numpy as np
from scipy.spatial import distance as dist
from collections import OrderedDict

# based from https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
class CentroidTracker():
    def __init__(self, max_disappeared=50):
        self.next_vehicle_id = 0
        self.vehicles = OrderedDict()
        self.vehicle_classes = {}
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared

    def register(self, class_id, centroid):
        self.vehicles[self.next_vehicle_id] = centroid
        self.vehicle_classes[self.next_vehicle_id] = class_id
        self.disappeared[self.next_vehicle_id] = 0
        self.next_vehicle_id += 1

    def deregister(self, vehicle_id):
        del self.vehicles[vehicle_id]
        del self.disappeared[vehicle_id]

    def update(self, rects):
        if len(rects) == 0:
            for vehicle_id in list(self.disappeared.keys()):
                self.disappeared[vehicle_id] += 1
                
                if self.disappeared[vehicle_id] > self.max_disappeared:
                    self.deregister(vehicle_id)

            return self.vehicles, self.vehicle_classes

        # initialize arrays
        input_centroids = np.zeros((len(rects), 2), dtype="int")
        labels = np.zeros((len(rects)), dtype="int")

        # for each bound from classification
        for (i, (class_id, start_x, start_y, end_x, end_y)) in enumerate(rects):
            # centroid points
            cx = int((start_x + end_x) / 2.0)
            cy = int((start_y + end_y) / 2.0)
            # add centroid to input array 
            # add label to labels array
            input_centroids[i] = (cx, cy)
            labels[i] = class_id

        # used when no vehicles being tracked
        if len(self.vehicles) == 0:
            for i in range(0, len(input_centroids)):
                self.register(labels[i], input_centroids[i])

        # vehicles are being tracked, try match centroids with previous points
        else:
            vehicle_ids = list(self.vehicles.keys())
            vehicle_centroids = list(self.vehicles.values())

            # distance between pairs of object centroids and input centroids
            D = dist.cdist(np.array(vehicle_centroids), input_centroids)
            # find smallest value in each row and sort row indexes on minimum value
            # finding the smallest value in each column from sorted rows
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                # get the vehicle id, set centroid, reset dis count
                vehicle_id = vehicle_ids[row]
                self.vehicles[vehicle_id] = input_centroids[col]
                self.disappeared[vehicle_id] = 0
                # add vehicle points to used sets
                used_rows.add(row)
                used_cols.add(col)

            # get unused vehicle centroids
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            # tracked centroids equal or greater than input centroids
            # check if any vehicles disappeared
            if D.shape[0] >= D.shape[1]:
                for row in unused_rows:
                    # increment dis count
                    vehicle_id = vehicle_ids[row]
                    self.disappeared[vehicle_id] += 1
                    # check max frames disappeard for vehicle
                    if self.disappeared[vehicle_id] > self.max_disappeared:
                        self.deregister(vehicle_id)

            # otherwise, register the centroid and label as new vehicle
            else:
                for col in unused_cols:
                    self.register(labels[col], input_centroids[col])
                    
        # return the set of trackable vehicles
        return self.vehicles, self.vehicle_classes