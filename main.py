from cv2 import (VideoCapture, putText, imshow,
waitKey, destroyAllWindows, FONT_HERSHEY_SIMPLEX, LINE_AA)
from utils.tracking import MediaPipeFacade
from game_tracking import *
from utils.tracking import Human
from utils.line import Segment, crossRS


def main():
    cap = VideoCapture(0)
    mp_facade = MediaPipeFacade()

    first_player = Human(None, None, (640, 360)) # hands_results pose_results image_shape
    second_player = Human(None, None, (640, 360))# hands_results pose_results image_shape

    frame_number = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, hands_results, pose_results = mp_facade.process_frame(frame, debug=False )
        labels = []

        if pose_results[0] is not None:
            first_player.left_hand = hands_results[0]
            first_player.right_hand = hands_results[0]
            

            first_player.pose = pose_results[0].pose_landmarks[0] if len(pose_results[0].pose_landmarks) else None
            first_player.shape = frame.shape

        if pose_results[1] is not None:
            second_player.left_hand = hands_results[1]
            second_player.right_hand = hands_results[1]
            second_player.pose = pose_results[1].pose_landmarks[0] if pose_results is not None or len(pose_results[1].pose_landmarks) else None
            second_player.img_shape = frame.shape

        if first_player.pose is not None and second_player.pose is not None:
            result_of_round = round(first_player, second_player, frame.shape)
            if result_of_round is not None:
                for data in result_of_round:
                    labels.append((data, (0, 0, 255)))

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
