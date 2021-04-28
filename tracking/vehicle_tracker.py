import datetime
import numpy as np
import imutils
import dlib
import cv2
import csv
from api import api_connection
from centroid_tracker import CentroidTracker
from vehicle import TrackableVehicle, LabelledTracker
from classifier import yolov4, CONFIDENCE_THRESHOLD, NMS_THRESHOLD
from fps import FPS

class TrackingSettings():
    def __init__(self, video_input="../data/test-clip.mp4", max_disappeared: int = 15, skip_frames: int = 10,
                             y_roi: int = 0, max_width: int = 500, verbose: bool = True, testing: bool = False):

        self.video_input = video_input
        self.max_disappeared = max_disappeared
        self.skip_frames = skip_frames
        self.y_roi = y_roi
        self.max_width = max_width
        self.verbose = verbose
        self.testing = testing
        # allowing just person, bicycle, car, motorcycle, bus 5 and truck
        self.trackable_classes = [0, 1, 2, 3, 7]
    
    def __repr__(self):
        return "video_input: {}, max_disappeared: {}, skip_frames: {}, y_roi: {}, max_width: {}".format(self.video_input, self.max_disappeared, self.skip_frames, self.y_roi, self.max_width)
    
    def save(self, path):
        with open(path, mode='w', newline='') as csv_file:
            fieldnames = ['video_source', 'max_disappeared', 'skip_frames', 'y_roi', 'max_width', 'verbose']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'video_source': self.video_input, 'max_disappeared': self.max_disappeared, 
            'skip_frames': self.skip_frames, 'y_roi': self.y_roi, 'max_width': self.max_width, 'verbose': self.verbose})
        
class VehicleTracker():
    def __init__(self, settings: TrackingSettings = None):
        if settings is None:
            self.settings = TrackingSettings()
        else:
            self.settings = settings

        self.logger = api_connection(self.settings.verbose)
        self.video_stream = cv2.VideoCapture(self.settings.video_input)
        self.centroid_tracker = CentroidTracker(max_disappeared=self.settings.max_disappeared)
        self.classifier = yolov4()
        self.total_frames_processed = 0
        self.video_width = None
        self.video_height = None
        self.crl_trackers = []
        self.tracked_vehicles = {}

    def track(self):
        self.fps = FPS().start()
        while True:
            frame = self.video_stream.read()
            frame = frame[1] if self.settings.video_input else frame
            # check if frame is empty
            if frame is None:
                break

            frame, rgb_frame = self.__process_frame(frame)

            bounding_boxes = [] # box rectangles from YOLO or tracker
            # DETECTION STAGE (YOLOv4)
            if self.total_frames_processed % self.settings.skip_frames == 0:
                self.__detect_vehicles(frame, rgb_frame)
            # TRACKING STAGE (dlib)
            else:
                self.__update_tracked_rectangles(rgb_frame, bounding_boxes)

            # use the centroid tracker to associate the old centroids with new object centroids
            vehicles, class_ids = self.centroid_tracker.update(bounding_boxes)
            self.__check_centroids(vehicles, class_ids, frame)
          
            # display frame if verbose
            if(self.settings.verbose == True):
                waitkey_pressed = self.__display_frame(frame)
                if waitkey_pressed == True:
                    break

            # increment the total number of frames processed
            self.total_frames_processed += 1
            self.fps.update()

        # stop fps, release video and cv2 windows
        self.fps.stop()
        self.video_stream.release()
        cv2.destroyAllWindows()
        self.logger.close()

        # return session id for testing and fps information
        return self.logger.session_id, self.tracked_vehicles, self.fps.elapsed(), self.fps.fps()

    def __process_frame(self, frame):
        # resize frame
        frame = imutils.resize(frame, width=self.settings.max_width)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # set frame width and height
        if self.video_width is None or self.video_height is None:
            (self.video_height, self.video_width) = frame.shape[:2]

        return frame, rgb_frame

    def __detect_vehicles(self, frame, rgb_frame) -> None:
        self.crl_trackers = [] # reset trackers
        # set region of interest (cut frame @ y value)
        roi = frame[self.settings.y_roi: self.video_height]
        classes, scores, boxes = self.classifier.model.detect(roi, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        for (classid, score, box) in zip(classes, scores, boxes):
            if classid not in self.settings.trackable_classes:
                continue
            left = box[0]
            top = box[1] + self.settings.y_roi
            right = box[0] + box[2]
            bottom = box[1] + box[3] + self.settings.y_roi

            # construct a dlib rectangle and tracker
            tracker = dlib.correlation_tracker()
            rect = dlib.rectangle(left, top, right, bottom) 
            tracker.start_track(rgb_frame, rect)
            
            # create labelled tracker 
            labelled_tracker = LabelledTracker(classid, tracker)
            self.crl_trackers.append(labelled_tracker)
        
    def __update_tracked_rectangles(self, rgb_frame, bounding_boxes) -> None:
        for tracker in self.crl_trackers:
            # update the tracker, get updated position
            tracker.crl_tracker.update(rgb_frame)
            new_position = tracker.crl_tracker.get_position()
            
            # add new tracked box
            left = int(new_position.left())
            top = int(new_position.top())
            right = int(new_position.right())
            bottom = int(new_position.bottom())
            bounding_boxes.append((tracker.vehicle_class, left, top, right, bottom))

    def __check_centroids(self, vehicles, class_ids, frame):
        # loop over the tracked objects
        for (vehicle_id, centroid) in vehicles.items():
            # check to see if a trackable object exists for vehicle_id
            vehicle = self.tracked_vehicles.get(vehicle_id, None)
            # if there is no existing trackable object, create one
            if vehicle is None:
                class_name = self.classifier.class_names[class_ids[vehicle_id]]
                vehicle = TrackableVehicle(vehicle_id, class_name, centroid)
            # otherwise, there is a trackable object
            else:
                # check differences in centroid points and distances
                y = [c[1] for c in vehicle.centroids]
                direction = centroid[1] - np.mean(y)
                vehicle.centroids.append(centroid)
                # check to see if the object has been counted or not
                if vehicle.counted == False:
                    self.__update_vehicle_direction(vehicle, direction, centroid)

            # store the trackable object in dictionary
            self.tracked_vehicles[vehicle_id] = vehicle

            if(self.settings.verbose == True):
                self.__draw_vehicle_on_frame(frame, vehicle_id, self.classifier.class_names[class_ids[vehicle_id]], centroid)

    def __update_vehicle_direction(self, vehicle, direction, centroid):
        # direction is negative and above mid line
        if direction < 0 and centroid[1] < self.video_height // 2:
            vehicle.direction = "up"
            vehicle.counted = datetime.datetime.now(datetime.timezone.utc)
            self.logger.insert_vehicle(vehicle)
            # direction is positive and above mid line
        elif direction > 0 and centroid[1] > self.video_height // 2:
            vehicle.direction = "down"
            vehicle.counted = datetime.datetime.now(datetime.timezone.utc)
            self.logger.insert_vehicle(vehicle)
        if vehicle.direction != None and self.settings.testing == True:
            self.fps.pause()
            check_correct = input(str(vehicle) + "crossed [Correct (y) or False(n)]")
            if check_correct == 'n':
                vehicle.correct = False
            else:
                vehicle.correct = True
            self.fps.resume()


    def __draw_vehicle_on_frame(self, frame, vehicle_id, label, centroid) -> None:
        text = "ID {} {}".format(vehicle_id, label)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    def __display_frame(self, frame):
        cv2.line(frame, (0, self.video_height // 2), (self.video_width, self.video_height // 2), (0, 255, 255), 2)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"): 
            return True
        else:
            return False