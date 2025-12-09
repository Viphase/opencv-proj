import numpy as np
from cv2 import (VideoCapture, minEnclosingCircle, putText, imshow,
waitKey, destroyAllWindows, FONT_HERSHEY_SIMPLEX, LINE_AA)
from math import acos, degrees
from utils.tracking import MediaPipeFacade
from utils.line import Vector


def is_pistol(results, frame) -> bool:
    if results is None or not results.hand_landmarks:
        return False
    
        
    lm = results.hand_landmarks[0]

    v1  = Vector(lm[0].x, lm[0].y, lm[20].x, lm[20].y)
    v2 = Vector(lm[0].x, lm[0].y, lm[18].x, lm[18].y)
    v3 = Vector(lm[0].x, lm[0].y, lm[12].x, lm[12].y)
    v4 = Vector(lm[0].x, lm[0].y, lm[10].x, lm[10].y)
    v5 = Vector(lm[0].x, lm[0].y, lm[16].x, lm[16].y)
    v6 = Vector(lm[0].x, lm[0].y, lm[14].x, lm[14].y) 
    v7 = Vector(lm[12].x, lm[12].y, lm[8].x, lm[8].y) 
    v8 = Vector(lm[10].x, lm[10].y, lm[8].x, lm[8].y) 
    v9 = Vector(lm[4].x, lm[4].y, lm[5].x, lm[5].y) 
    v10 = Vector(lm[4].x, lm[4].y, lm[9].x, lm[9].y) 

    x_l = frame.shape[1]
    y_l = frame.shape[0]


    v7 = Vector(lm[1].x * x_l, lm[1].y * y_l, lm[8].x * x_l, lm[8].y * y_l) 
    v8 = Vector(lm[1].x * x_l, lm[1].y * y_l, lm[3].x * x_l, lm[3].y * y_l) 

    if v1.dist() - v2.dist() < 0 and v3.dist() - v4.dist() < 0 and v5.dist() - v6.dist() < 0 and v7.dist() - v8.dist() > 0 and v10.dist() - v9.dist() > 0:
        return True
    else:
        return False
    


def main():
    cap = VideoCapture(0)
    mp_facade = MediaPipeFacade()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, hands, pose = mp_facade.process_frame(frame)

        if is_pistol(hands, frame):
            text = "GUN"
            color = (0, 255, 0)
        else:
            text = "NO GUN"
            color = (0, 0, 255)

        putText(frame, text, (50, 50), FONT_HERSHEY_SIMPLEX, 1, color, 2, LINE_AA)
        imshow("testik", frame)

        key = waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            mp_facade.close()
            cap.release()
            destroyAllWindows()
            break


if __name__ == "__main__":
    main()
