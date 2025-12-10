from numpy import array, int32
from cv2 import (VideoCapture, minEnclosingCircle, putText, imshow,
waitKey, destroyAllWindows, FONT_HERSHEY_SIMPLEX, LINE_AA)
from math import acos, degrees
from utils.tracking import MediaPipeFacade
from utils.geometry import Vector, crossRS


def finger_dist(first, second, results) -> float:
    if results is None or not results.hand_landmarks:
        return 0  

    lm = results.hand_landmarks[0]
    x1, y1 = lm[first].x, lm[first].y
    x2, y2 = lm[second].x, lm[second].y
    return ((x1 - x2)**2 + (y1 - y2)**2)**.5


def is_pistol(hand) -> bool:
    open = 0
    closed = 0

    for i in [1, 5, 9, 13, 17]:
        prev = None
        for j in range(i, i+3):
            if j + 1 > 20:
                break
            current = Vector(
                hand[j+1].x - hand[j].x,
                hand[j+1].y - hand[j].y
            )
            if prev is not None:
                angle = degrees(acos((current * prev) / (current.dist() * prev.dist())))
                if 0 <= angle <= 20:
                    open += 1
                else:
                    closed += 1
            prev = current
    return open >= 6 and closed >= 2


def shot(human1, human2):
    cross1 = crossRS(human1.bullet, human2.collider)
    cross2 = crossRS(human2.bullet, human1.collider)
    if cross1 is not None:
        return (human1, cross1.x, cross1.y)
    elif cross2 is not None:
        return (human2, cross2.x, cross2.y)
    else:
        return None

def is_fist(hands, shape) -> bool:
    if hands is None or not hands.hand_landmarks:
        return False

    lm = hands.hand_landmarks[0]
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

        frame, tracked = mp_facade.process_frame(frame, debug=True)
        labels = []

        for i, human in enumerate(tracked):
            if human.right_hand is not None and is_pistol(human.right_hand):
                text = f"Player {i+1} Right Hand: GUN"
                color = (0, 255, 0)
            else:
                text = f"Player {i+1} Right Hand: NO GUN"
                color = (0, 0, 255)
            labels.append((text, color))

        y = 50
        for text, color in labels:
            putText(frame, text, (50, y), FONT_HERSHEY_SIMPLEX, 0.8, color, 2, LINE_AA)
            y += 40
        imshow("kartinka", frame)
        key = waitKey(1)
        if key == ord('q'):
            cap.release()
            destroyAllWindows()
            break


if __name__ == "__main__":
    main()
