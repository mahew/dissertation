import sys
import argparse
from vehicle_tracker import VehicleTracker, TrackingSettings
from tests_constants import SOURCE, PERSON_CLASS, BUS_CLASS, BICYCLE_CLASS, CAR_CLASS, CAR_COUNT_ACTUAL, TRUCK_CLASS, TRUCK_COUNT_ACTUAL, MTRBIKE_CLASS, MTRBIKE_COUNT_ACTUAL, TOTAL_COUNT

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Tracking Settings for Matthew Ball\'s tracking project')
        parser.add_argument('--input', type=str, default="../data/test-clip.mp4", help='The input video or stream of traffic images')
        parser.add_argument('--roi', type=int, default=90, help='Region of Interest Value (Y Cut Off)')
        parser.add_argument('--skip', type=int, default=15, help='Number of skip frames')
        parser.add_argument('--maxw', type=int, default=800, help='Max Width Value used to resize input frame')
        parser.add_argument('--verbose', type=bool, default=True, help='Verbose option, used to show the input frame, will increase performance when disabled')
        parser.add_argument('--testing', type=bool, default=False, help='Manual Testing Option, only works with default input video, enables Verbose mode')
        
        args = parser.parse_args()
        if args.testing == True:
            args.verbose = True
            args.input = "../data/test-clip.mp4"

        settings = TrackingSettings(video_input = args.input, y_roi = args.roi, 
            skip_frames = args.skip, max_width = args.maxw, verbose=args.verbose, testing=args.testing)
        tracker = VehicleTracker(settings) 
        
        session_id, tracked_vehicles, elapsed_time, average_fps = tracker.track()
        print("Settings: " + str(settings))
        print("Elapsed Time: {}, FPS: {}".format(elapsed_time, average_fps))

        if args.testing == True:
            total_detected_count = len(tracked_vehicles)
            total_correct_count = 0
            total_false_count = 0
            missed_vehicles = 0

            correct_vehicles_classes = []
            false_vehicles_classes = []
            for v in list(tracked_vehicles.values()):
                if v.correct == True:
                    total_correct_count += 1
                    correct_vehicles_classes.append(v.class_name)
                else:
                    total_false_count += 1
                    false_vehicles_classes.append(v.class_name)

            false_rate = (total_false_count / total_detected_count) * 100
            a = (total_correct_count / TOTAL_COUNT) * 100

            missed_vehicles += (CAR_COUNT_ACTUAL - correct_vehicles_classes.count(CAR_CLASS))
            missed_vehicles += (TRUCK_COUNT_ACTUAL - correct_vehicles_classes.count(TRUCK_CLASS))
            missed_vehicles += (MTRBIKE_COUNT_ACTUAL - correct_vehicles_classes.count(MTRBIKE_CLASS))
            missed_rate = (missed_vehicles / total_detected_count) * 100
            print("Ground Truth: {}, Total Count: {}, Correct: {}, False: {}, FalseRate: {}, Missed: {}, MissedRate: {}, A: {}".format(TOTAL_COUNT, total_detected_count, total_correct_count, total_false_count, false_rate, missed_vehicles, missed_rate, a))
        
        sys.exit()
    except Exception as e:
        print(e)
    sys.exit()