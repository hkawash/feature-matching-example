# coding: utf-8
#
# Computer Vision (week 3,4): Example of feature matching & homography
#   Hiroaki Kawashima <kawashima@i.kyoto-u.ac.jp>
#
#   Ref: https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_feature_homography/py_feature_homography.html
#

import numpy as np
import cv2

class ObjectDetector:
    """ Object detector for VideoCapture using feature matching """

    def __init__(self):
        # Feature-point detector
        self.feature_detector = cv2.AKAZE_create() # Use AKAZE
        #self.detector = cv2.ORB_create() # Use ORB

        # VideoCapture setting
        self.vidcap = cv2.VideoCapture(0)
        self.vidcap.set(3, 640) # width
        self.vidcap.set(4, 480) # height
        self.vidcap.set(5, 15)  # frame rate

        # ROI (Region-Of-Interest) to register a target object
        self.sub_topleft = [100, 220] # [0, 0] # [y,x]
        self.sub_width = 200 #640
        self.sub_height = 200 #480
        self.sub_bottomright = [self.sub_topleft[0] + self.sub_height - 1,\
                                self.sub_topleft[1] + self.sub_width - 1]
        self.rect_color = (0, 255, 0) # green
        self.rect_thickness = 3
        self.rect_tl_outer_xy = (self.sub_topleft[1] - self.rect_thickness,\
                                 self.sub_topleft[0] - self.rect_thickness)
        self.rect_br_outer_xy = (self.sub_bottomright[1] + self.rect_thickness,\
                                 self.sub_bottomright[0] + self.rect_thickness)

        self.ratio = 0.6  # Threshold for the distance of feature (descriptor) vectors
        self.registered = False
        self.min_match_count = 5

    def register(self):
        """ Register target object """

        print("Hold a target object close to the camera.")
        print(" (*) Make sure the green rectangle does not contain any background part.")
        print("Then, press 'r' to register the object.\n")

        while self.vidcap.isOpened():
            ret, frame = self.vidcap.read()

            cv2.rectangle(frame, self.rect_tl_outer_xy, self.rect_br_outer_xy,\
                          self.rect_color, self.rect_thickness)
            cv2.imshow("Registration (press 'r' to register)", frame)

            if cv2.waitKey(1) & 0xFF == ord('r'):
                subimg = frame[self.sub_topleft[0]:(self.sub_topleft[0] + self.sub_height),
                               self.sub_topleft[1]:(self.sub_topleft[1] + self.sub_width)]
                self.kp0, self.des0 = self.feature_detector.detectAndCompute(subimg, None)
                self.queryimg = subimg
                self.registered = True
                break

    def detect(self):
        """ Find object using feature points """

        if not self.registered:
            print("Call 'register()' first.")
            return

        print("Start detection...")
        print("Press 'q' to quit.\n")

        bf = cv2.BFMatcher()  # Prepare a Blute-Force (BF) matcher

        while self.vidcap.isOpened():
            ret, frame = self.vidcap.read()

            # Keypoint (kp) detection and calculate descriptors (des)
            kp, des = self.feature_detector.detectAndCompute(frame, None)

            # Apply blute-force knn matching between keypoints
            matches = bf.knnMatch(self.des0, des, k=2)

            # Adopt only good feature matches
            good = [[m] for m, n in matches if m.distance < self.ratio * n.distance]

            # Find Homography
            if len(good) > self.min_match_count:
                src_pts = np.float32([self.kp0[m[0].queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp[m[0].trainIdx].pt for m in good]).reshape(-1, 1, 2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                h, w, c = self.queryimg.shape  # Assume color camera
                pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)

                frame = cv2.polylines(frame, [np.int32(dst)], True, (0, 255, 0), 2, cv2.LINE_AA)

            # Visualize the matches
            draw_params = dict(flags=2)
            #draw_params = dict(matchColor=(0, 255, 0), singlePointColor=(0, 0, 255), flags=0)
            img = cv2.drawMatchesKnn(self.queryimg, self.kp0, frame, kp, good, None, **draw_params)
            cv2.imshow("Detection (press 'q' to quit)", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def close(self):
        """ Release VideoCapture and destroy windows """
        self.vidcap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    obj_detector = ObjectDetector()
    obj_detector.register()
    obj_detector.detect()
    obj_detector.close()
