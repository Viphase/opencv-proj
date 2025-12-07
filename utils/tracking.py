from cv2 import cvtColor, resize, COLOR_RGB2BGR, COLOR_BGR2RGB
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat
from mediapipe.tasks import python as mp_tasks
from numpy import fliplr


class MediaPipeFacade:
    def __init__(self):
        base_options_hands = mp_tasks.BaseOptions(
            model_asset_path="./models/hand_landmarker.task"
        )

        base_options_pose = mp_tasks.BaseOptions(
            model_asset_path="./models/pose_landmarker.task"
        )

        self.hands = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=base_options_hands,
                num_hands=4,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5
            )
        )

        self.pose = vision.PoseLandmarker.create_from_options(
            vision.PoseLandmarkerOptions(
                base_options=base_options_pose,
                num_poses=4,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5
            )
        )

        self.mp_drawing = None

    def process_frame(self, frame, debug: bool = False):
        img = fliplr(frame)
        img = cvtColor(img, COLOR_BGR2RGB)
        img = resize(img, (1920, 1080))

        mp_image = Image(image_format=ImageFormat.SRGB, data=img)

        results_hands = self.hands.detect(mp_image)
        results_pose = self.pose.detect(mp_image)

        if debug:
            if results_hands.hand_landmarks:
                for hand in results_hands.hand_landmarks:
                    for lm in hand:
                        px = int(lm.x * img.shape[1])
                        py = int(lm.y * img.shape[0])
                        img[py-2:py+2, px-2:px+2] = [255, 0, 0]

            if results_pose.pose_landmarks:
                for pose in results_pose.pose_landmarks:
                    for lm in pose:
                        px = int(lm.x * img.shape[1])
                        py = int(lm.y * img.shape[0])
                        img[py-2:py+2, px-2:px+2] = [0, 255, 0]

        return cvtColor(img, COLOR_RGB2BGR), results_hands, results_pose
