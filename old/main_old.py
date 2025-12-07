from numpy import array, int32
from cv2 import (VideoCapture, minEnclosingCircle, putText, imshow, 
waitKey, destroyAllWindows, FONT_HERSHEY_SIMPLEX, LINE_AA)
from math import acos, degrees
from old.utils_old.tracking_old import MediaPipeFacade
from utils.geometry import Vector


def finger_dist(first, second, results) -> float:
    if results is None or results.multi_hand_landmarks is None or len(results.multi_hand_landmarks) == 0:
        return 0
    
    x1, y1 = results.multi_hand_landmarks[0].landmark[first].x, results.multi_hand_landmarks[0].landmark[first].y
    x2, y2 = results.multi_hand_landmarks[0].landmark[second].x, results.multi_hand_landmarks[0].landmark[second].y
    return ((x1 - x2)**2 + (y1 - y2) **2)**.5


def is_pistol(results) -> bool:
    if results is None or results.multi_hand_landmarks is None or len(results.multi_hand_landmarks) == 0:
        return False

    open = 0
    closed = 0
    
    for i in [1, 5, 9, 13, 17]:
        prev = None
        for j in range(i, i+3):
            if j + 1 > 20:
                break
            current = Vector(results.multi_hand_landmarks[0].landmark[j+1].x - 
                            results.multi_hand_landmarks[0].landmark[j].x, 
                            results.multi_hand_landmarks[0].landmark[j+1].y - 
                            results.multi_hand_landmarks[0].landmark[j].y)
            if prev is not None:
                angle = degrees(acos((current * prev) / (current.dist() * prev.dist())))
                if 0 <= angle <= 45:
                    open += 1
                else:
                    closed += 1
            prev = current
    return open >= 6 and closed >= 3

    # return (finger_dist(4, 8, results) > 0.08 
    #         and finger_dist(12, 0, results) < 0.3  
    #         and finger_dist(16, 0, results) < 0.3 
    #         and finger_dist(20, 0, results) < 0.3)   --- deprecated
    

def is_fist(results, shape) -> bool:
    if results is None or results.multi_hand_landmarks is None or len(results.multi_hand_landmarks) == 0:
        return False
    
    points = []
    for mark in results.multi_hand_landmarks[0].landmark:
        points.append([mark.x * shape[1], mark.y * shape[0]])
    points = array(points, dtype=int32)

    x1, y1 = results.multi_hand_landmarks[0].landmark[0].x * shape[1], results.multi_hand_landmarks[0].landmark[0].y * shape[0]
    x2, y2 = results.multi_hand_landmarks[0].landmark[5].x * shape[1], results.multi_hand_landmarks[0].landmark[5].y * shape[0]
   
    ws = ((x1 - x2)**2 + (y1 - y2) **2)**.5
    _, r = minEnclosingCircle(points)
    
    return (2 * r / ws) > 1.6


def main():
    cap = VideoCapture(0)
    mp_facade = MediaPipeFacade()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, hands, pose = mp_facade.process_frame(frame, debug=True)

        if is_pistol(hands):
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