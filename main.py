from numpy import array, int32
from cv2 import (VideoCapture, minEnclosingCircle, putText, imshow,
waitKey, destroyAllWindows, FONT_HERSHEY_SIMPLEX, LINE_AA)
from math import acos, degrees
from utils.tracking import MediaPipeFacade
from utils.geometry import Vector


def finger_dist(first, second, results) -> float:
    if results is None or not results.hand_landmarks:
        return 0  

    lm = results.hand_landmarks[0]
    x1, y1 = lm[first].x, lm[first].y
    x2, y2 = lm[second].x, lm[second].y
    return ((x1 - x2)**2 + (y1 - y2)**2)**.5


def is_pistol(results) -> bool:
    if results is None or not results.hand_landmarks:
        return False

    lm = results.hand_landmarks[0]
    open = 0
    closed = 0

    for i in [1, 5, 9, 13, 17]:
        prev = None
        for j in range(i, i+3):
            if j + 1 > 20:
                break
            current = Vector(
                lm[j+1].x - lm[j].x,
                lm[j+1].y - lm[j].y
            )
            if prev is not None:
                angle = degrees(acos((current * prev) / (current.dist() * prev.dist())))
                if 0 <= angle <= 20:
                    open += 1
                else:
                    closed += 1
            prev = current
    return open >= 6 and closed >= 2


def shot(results) -> bool:
    ...


def is_fist(results, shape) -> bool:
    if results is None or not results.hand_landmarks:
        return False

    lm = results.hand_landmarks[0]
    points = []

    for mark in lm:
        points.append([mark.x * shape[1], mark.y * shape[0]])
    points = array(points, dtype=int32)

    x1, y1 = lm[0].x * shape[1], lm[0].y * shape[0]
    x2, y2 = lm[5].x * shape[1], lm[5].y * shape[0]

    ws = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5
    _, r = minEnclosingCircle(points)
    return (2 * r / ws) > 1.6


def main():
    cap = VideoCapture(0)
    mp_facade = MediaPipeFacade()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hands, pose, frame, tracked = mp_facade.process_frame(frame, debug=True)

        if is_pistol(hands):
            text = "GUN"
            color = (0, 255, 0)
        else:
            text = "NO GUN"
            color = (0, 0, 255)

        putText(frame, text, (50, 50), FONT_HERSHEY_SIMPLEX, 1, color, 2, LINE_AA)
        imshow("testik", frame)

        key = waitKey(1)
        if key == ord('q'):
            cap.release()
            destroyAllWindows()
            break


if __name__ == "__main__":
    main()
