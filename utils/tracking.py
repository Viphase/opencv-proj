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
        - frame
        - tracked people list
        '''

        img = fliplr(frame)
        img = cvtColor(img, COLOR_BGR2RGB)
        img = resize(img, (640, 360))

        mp_image = Image(image_format=ImageFormat.SRGB, data=img)
        results_hands = self.hands.detect(mp_image)
        results_pose = self.pose.detect(mp_image)
        tracked = []

        if results_pose.pose_landmarks:
            n = len(results_pose.pose_landmarks)
            if n > 2:
                print(f"Detected {n} people, only 2")
            
            for i, _ in enumerate(results_pose.pose_landmarks[:2]):
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
                    img = line(img, (pose.collider.A.x, pose.collider.A.y), (pose.collider.B.x, pose.collider.B.y), (255,255,0), 2)
        return cvtColor(img, COLOR_RGB2BGR), tracked


class Human:
    def __init__(self, hands_results, pose_results, img_shape, i):
        self.pose = pose_results.pose_landmarks[i]
        self.img_shape = img_shape
        self.left_hand = hands_results.handedness[i][0]
        self.right_hand = None

    # def __assign_hands(self, hands_results):
    #     for hand in hands_results.hand_landmarks:
    #         wx, wy = hand[0].x, hand[0].y
    #         rx, ry = self.pose[11].x, self.pose[11].y # это плечи
    #         lx, ly = self.pose[12].x, self.pose[12].y

    #         right = (wx - rx) ** 2 + (wy - ry) ** 2
    #         left = (wx - lx) ** 2 + (wy - ly) ** 2
    #         if right < left:
    #             self.right_hand = hand
    #         else:
                
    #             self.left_hand = hand

    @property
    def collider(self):
        nose = self.pose[0]
        neck = self.pose[1]
        k1 = self.pose[31]
        k2 = self.pose[32]

        head_x = int(nose.x * self.img_shape[1])
        head_y = int(nose.y * self.img_shape[0] - 4 * (nose.y * self.img_shape[0] - neck.y * self.img_shape[0]))
        knees_x = int((k1.x + k2.x) * 0.5 * self.img_shape[1])
        knees_y = int((k1.y + k2.y) * 0.5 * self.img_shape[0])

        return Segment(head_x, head_y, knees_x, knees_y)
    
    @property
    def bullet(self):
        if self.left_hand:
            elbow = self.pose[13]
        else:
            elbow = self.pose[14]

        if self.left_hand:
            hand = self.pose[15]
        else:
            hand = self.pose[16]

        self.elbow_x = int(elbow.x * self.img_shape[1])
        self.elbow_y = int(elbow.y * self.img_shape[0])
        self.hand_x = int(hand.x * self.img_shape[1])
        self.hand_y = int(hand.y * self.img_shape[0])

        return Line(self.elbow_x, self.elbow_y, self.hand_x, self.hand_y)
