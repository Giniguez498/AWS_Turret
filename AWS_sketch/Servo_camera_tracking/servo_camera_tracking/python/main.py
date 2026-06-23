from arduino.app_utils import App
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_bricks.web_ui import WebUI
from arduino.app_utils.bridge import Bridge
import time

#Initialize the UI on port 7000
ui = WebUI(port=7000)

#Initialize the detector (it automatically starts the video stream on 4912)
detector = VideoObjectDetection(confidence=0.5)

def on_detections(detections: dict):
    #Check if "person" is in the dictionary AND make sure the list isn't empty
    if "person" in detections and len(detections["person"]) > 0:
        
        #Grab the data for the FIRST person it sees
        first_person = detections["person"][0]
        
        #Extract the [x_min, y_min, x_max, y_max] list
        coords = first_person['bounding_box_xyxy']
        
        x_min = coords[0] # The Left Edge
        x_max = coords[2] # The Right Edge
        
        #Calculate Dead Center (distance/scaling issue)
        center_x = (x_min + x_max) / 2
        
        print(f"Target locked at X: {int(center_x)}")
        
        #Send to C++ sketch (Using the .call method)
        Bridge.call("setTarget", int(center_x))
        
        #Send data to WebUI
        message = {
            "content": "person",
            "confidence": first_person['confidence'], 
            "timestamp": int(time.time() * 1000)
        }
        ui.send_message("detection", message)
        
    else:
        #SCAN MODE: Nobody is in frame, tell MCU to spin servo.
        Bridge.call("setTarget", 0)

detector.on_detect_all(on_detections)

#Start the servers
ui.start()
App.run()