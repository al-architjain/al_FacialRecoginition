'''
    How to Run:
    python recogniseImage.py --encodingsfile encodings.pickle --image examples/example_01.png
'''

#Import Packages
import dlib
import argparse
import cv2
import face_recognition
import pickle

#Arguments Importing
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodingsfile", required=True, help="path to serialized db of facial encodings")
ap.add_argument("-i", "--image", required=True, help="path to input image")
# ap.add_argument("-d", "--detection-method", type=str, default="cnn", help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

#The Image Recognision class
class recogniseImage():

    def __init__(self):
        print("[INFO] Initializing variables and loading encodings....")

        #Read Image
        self.image_bgr = cv2.imread(args["image"])
        self.image_rgb = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2RGB)

        #Loading pre-trained encoded data
        self.known_data = pickle.loads(open(args["encodingsfile"], "rb").read())
        self.known_name_counts = {}
        for iname in self.known_data["names"]:
            self.known_name_counts[iname] = self.known_name_counts.get(iname, 0) + 1

        # for iname in self.known_name_counts:
        #    print(iname + str(self.known_name_counts[iname]))

    def xtractFeatures(self):
        # Extracting features
        print("[INFO] recognizing faces in given image...")
        self.locations = face_recognition.face_locations(self.image_rgb, model='hog')  # (model=args["detection_method"])
        self.landmarks = face_recognition.face_landmarks(self.image_rgb)
        self.encodings = face_recognition.face_encodings(self.image_rgb, self.locations)


    def compareEncodings(self):
        print("[INFO] Starting Comparision......")
        # Looping over dataset
        names = []
        for encoding in self.encodings:
            matches = face_recognition.compare_faces(self.known_data["encodings"], encoding)
            name = "Unknown"

            # check to see if we have found a match
            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]

                counts = {}
                for i in matchedIdxs:
                    iname = self.known_data["names"][i]
                    counts[iname] = counts.get(iname, 0) + 1

                countsperc = {}
                for iname in counts:
                    mcount = self.known_name_counts[iname]
                    ccount = counts[iname]
                    countsperc[iname] = (ccount*100)/mcount


                maxname = max(countsperc, key=countsperc.get)

                if countsperc[maxname]>=50:
                    name = maxname + str(countsperc[maxname]) + "%"

            # update the list of names
            names.append(name)

        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(self.locations, names):
            # draw the predicted face name on the image
            cv2.rectangle(self.image_bgr, (left, top), (right, bottom + 35), (51,51, 255 ), 2)
            cv2.rectangle(self.image_bgr, (left, bottom), (right, bottom + 35), (51, 51, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(self.image_bgr, name, (left + 2, bottom + 30), font, 0.85, (255, 255, 255), 1)

    def displayResult(self):
        print("{INFO] Displaying Result....")
        #Display Output
        image = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2RGB)
        win = dlib.image_window()
        win.set_image(image)
        dlib.hit_enter_to_continue()


def Main():
    robj = recogniseImage()
    robj.xtractFeatures()
    robj.compareEncodings()
    robj.displayResult()


if __name__=='__main__':
    Main()
