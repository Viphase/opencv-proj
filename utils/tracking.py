from mediapipe.tasks.python import vision
from mediapipe.tasks import python as mp
from mediapipe import Image, ImageFormat
from cv2 import line, circle, cvtColor, resize, COLOR_RGB2BGR, COLOR_BGR2RGB
from numpy import fliplr, hstack
from utils.line import Segment, Ray

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 320

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

        img = cvtColor(frame, COLOR_BGR2RGB)
        img = resize(img, (480, 340))


        first_half = img[:, : img.shape[1] // 2, :].copy()
        second_half = img[:, img.shape[1] // 2 :, :].copy()
        mp_first_half = Image(image_format=ImageFormat.SRGB, data=first_half)
        results_hands_first = self.hands.detect(mp_first_half)
        results_pose_first = self.pose.detect(mp_first_half)

        if results_pose_first.pose_landmarks:
            n = len(results_pose_first.pose_landmarks)
            if n > 2:
                print(f"В левой части поля должен находится только один человек")
            if n < 1:
                print("Игрок должен встать в левую часть поля")
        else:
            results_pose_first = None
            results_hands_first = None

        mp_second_half = Image(image_format=ImageFormat.SRGB, data=second_half)
        results_hands_second = self.hands.detect(mp_second_half)
        results_pose_second = self.pose.detect(mp_second_half)

        if results_pose_second.pose_landmarks:
            n = len(results_pose_second.pose_landmarks)
            if n > 2:
                print(f"В левой части поля должен находится только один человек")
            if n < 1:
                print("Игрок должен встать в левую часть поля")
        else:
            results_pose_second = None
            results_hands_second = None
        if debug:
            img = debugf(img, first_half.shape, results_hands_first, results_pose_first, results_hands_second,results_pose_second)
        return img, (results_hands_first,results_hands_second), (results_pose_first, results_pose_second)

def debugf(img,half_image_shape,hands_left,pose_left,hands_right,pose_right):
    h, w, _ = half_image_shape
    x_offset = w  

    if hands_left and hands_left.hand_landmarks:
        for hand in hands_left.hand_landmarks[:4]:
            for lm in hand:
                px = int(lm.x * w)
                py = int(lm.y * h)
                circle(img, (px, py), 3, (255, 0, 0), -1)

    if pose_left and pose_left.pose_landmarks:
        for pose in pose_left.pose_landmarks[:2]:
            for lm in pose:
                px = int(lm.x * w)
                py = int(lm.y * h)
                circle(img, (px, py), 3, (0, 255, 0), -1)

    if hands_right and hands_right.hand_landmarks:
        for hand in hands_right.hand_landmarks[:4]:
            for lm in hand:
                px = int(lm.x * w) + x_offset
                py = int(lm.y * h)
                circle(img, (px, py), 3, (255, 0, 0), -1)

    if pose_right and pose_right.pose_landmarks:
        for pose in pose_right.pose_landmarks[:2]:
            for lm in pose:
                px = int(lm.x * w) + x_offset
                py = int(lm.y * h)
                circle(img, (px, py), 3, (0, 255, 0), -1)

    return cvtColor(img, COLOR_RGB2BGR)


class Human:
    def __init__(self, hands_results, pose_results, img_shape):
        self.pose = pose_results # pose detector
        self.img_shape = img_shape # image size

        self.left_hand = hands_results # left hand landmarks
        self.right_hand = hands_results # right hand landmarks

        self.hp = 3 # current player hp
        self.won = 0 # how many rounds player won
        self.state = None # can have Gun or Shild or Nothing state

    @property
    def left_hand(self):
        return self._left_hand
    
    @left_hand.setter
    def left_hand(self, hands_results):
        if hands_results is not None:
            for i, hand in enumerate(hands_results.hand_landmarks):
                hand_type = hands_results.handedness[i][0].category_name
                if hand_type == "Left":
                    self._left_hand = hand
        else:
            self._left_hand = None

    @property
    def right_hand(self):
        return self._right_hand
    
    @right_hand.setter
    def right_hand(self, hands_results):
        if hands_results is not None:
            for i, hand in enumerate(hands_results.hand_landmarks):
                hand_type = hands_results.handedness[i][0].category_name
                if hand_type == "Right":
                    self._right_hand = hand
        else:
            self._right_hand = None

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

        return Segment((head_x, head_y), (knees_x, knees_y))
    
    @property
    def bullet(self):
        if self.pose is not None:
            try:
                start = (self.pose[14].x * SCREEN_WIDTH, self.pose[14].y * SCREEN_HEIGHT)
                end = (self.pose[16].x * SCREEN_WIDTH, self.pose[16].y * SCREEN_HEIGHT)
                return Ray(start=start, point=end)
            except:
                return None
        else:
            return None
        
    @property
    def shield(self):
        if self.pose is not None:
            try:
                return Segment(self.pose[16].x * SCREEN_WIDTH, self.pose[16].y * SCREEN_HEIGHT + 50, self.pose[16].x * SCREEN_WIDTH, self.pose[16].y * SCREEN_HEIGHT - 50)
            except:
                return None
        else:
            return None
        
    def shoot(self, victim):
        self.won += 1
        victim.hp -= 1