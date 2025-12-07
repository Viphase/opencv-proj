from cv2 import cvtColor, resize, COLOR_RGB2BGR, COLOR_BGR2RGB
from mediapipe import solutions
from numpy import fliplr

class MediaPipeFacade:
    def __init__(self):
        self.mp_hands = solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=4,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_pose = solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = solutions.drawing_utils

    def process_frame(self, frame, debug: bool = False):
        img = fliplr(frame)
        img = cvtColor(img, COLOR_BGR2RGB)
        img = resize(img, (1280, 720))

        results_hands = self.hands.process(img)
        results_pose = self.pose.process(img)

        if debug:
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            if results_pose.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    img, results_pose.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        return cvtColor(img, COLOR_RGB2BGR), results_hands, results_pose


    def close(self):
        self.hands.close()
        self.pose.close()
