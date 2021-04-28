import cv2

# dnn constants
CONFIDENCE_THRESHOLD = 0.3
NMS_THRESHOLD = 0.4
WEIGHTS_URL = "https://github-releases.githubusercontent.com/75388965/228a9c00-3ea4-11eb-8e80-28d71569f56c?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20210405%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210405T124512Z&X-Amz-Expires=300&X-Amz-Signature=00ab9b626bf88d9e8fb80f78a1e5220a3370a7997d78ef7e243ea0a26f4bf5b3&X-Amz-SignedHeaders=host&actor_id=34048460&key_id=0&repo_id=75388965&response-content-disposition=attachment%3B%20filename%3Dyolov4-tiny.weights&response-content-type=application%2Foctet-stream"

class yolov4:
    class_names = []
    model = None

    def __init__(self):
        # dnn
        with open("../data/classes.txt", "r") as f:
            self.class_names = [cname.strip() for cname in f.readlines()]

        net = cv2.dnn.readNet("../data/yolov4-tiny.weights", "../data/yolov4-tiny.cfg")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
        self.model = cv2.dnn_DetectionModel(net)
        self.model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)