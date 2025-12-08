from mediapipe.tasks.python import vision
from mediapipe.tasks import python as mp
from mediapipe import Image, ImageFormat
from cv2 import line, circle, cvtColor, resize, COLOR_RGB2BGR, COLOR_BGR2RGB
from numpy import fliplr
from utils.geometry import Segment, Line


class MediaPipeFacade:
    def __init__(self):
        base_options_hands = mp.BaseOptions(
            model_asset_path="./models/hand_landmarker.task"
        )

        base_options_pose = mp.BaseOptions(
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
                num_poses=2,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5
            )
        )


    def process_frame(self, frame, debug: bool = False):
        '''
        ## Returns: 
        - results_hands
        - results_pose
        - frame
        - tracked people list
        '''

        img = fliplr(frame)
        img = cvtColor(img, COLOR_BGR2RGB)
        img = resize(img, (640, 360))

        mp_image = Image(image_format=ImageFormat.SRGB, data=img)
        results_hands = self.hands.detect(mp_image)
        results_pose = self.pose.detect(mp_image)
        
        if results_pose.pose_landmarks:
            n = len(results_pose.pose_landmarks)
            if n > 2:
                print(f"Detected {n} people, only 2")

        tracked = []
        if results_pose.pose_landmarks:
            for i, pose_lm in enumerate(results_pose.pose_landmarks[:2]):
                tracked.append(Human(results_hands, results_pose, img.shape, i))

        if debug:
            if results_hands.hand_landmarks:
                for hand in results_hands.hand_landmarks[:4]:
                    for lm in hand:
                        px = int(lm.x * img.shape[1])
                        py = int(lm.y * img.shape[0])
                        circle(img, (px, py), 3, (255, 0, 0), -1)

            if results_pose.pose_landmarks:
                for pose in results_pose.pose_landmarks[:2]:
                    for lm in pose:
                        px = int(lm.x * img.shape[1])
                        py = int(lm.y * img.shape[0])
                        circle(img, (px, py), 3, (0, 255, 0), -1)
                for pose in tracked[:2]:
                    img = line(img, pose.head(), pose.knees(), (255,255,0), 2)
        return results_hands, results_pose, cvtColor(img, COLOR_RGB2BGR), tracked


class Human:
    def __init__(self, hands_results, pose_results, img_shape, i):
        self.pose = pose_results.pose_landmarks[i]
        if hands_results is None or not hands_results.hand_landmarks:
            self.hands = None
        else:
            self.hands = hands_results.hand_landmarks

        self.img_shape = img_shape
        self.collider = Segment(*self.head(), *self.knees())

    def head(self):
        nose_x, nose_y = self.pose[0].x * self.img_shape[1], self.pose[0].y * self.img_shape[0]
        neck_x, neck_y = self.pose[1].x * self.img_shape[1], self.pose[1].y * self.img_shape[0]
        x = int(nose_x)
        y = int(nose_y - 4 * (nose_y - neck_y))
        return x, y

    def knees(self):
        lm_l = self.pose[31]
        lm_r = self.pose[32]
        return int((lm_l.x + lm_r.x) / 2 * self.img_shape[1]), int((lm_l.y + lm_r.y) / 2 * self.img_shape[0])

