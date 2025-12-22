import time
from mediapipe.tasks.python import vision
from mediapipe.tasks import python as mp
from mediapipe import Image, ImageFormat
from cv2 import cvtColor, COLOR_BGR2RGB, circle

class MediaPipeFacade:
    def __init__(self):
        self.hands = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=mp.BaseOptions(model_asset_path="./models/hand_landmarker.task"),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=4
            )
        )

        self.pose = vision.PoseLandmarker.create_from_options(
            vision.PoseLandmarkerOptions(
                base_options=mp.BaseOptions(model_asset_path="./models/pose_landmarker.task"),
                running_mode=vision.RunningMode.VIDEO,
                num_poses=2
            )
        )

    def process_frame(self, frame, debug=False):
        timestamp = int(time.time() * 1000)
        img = cvtColor(frame, COLOR_BGR2RGB)
        mp_img = Image(image_format=ImageFormat.SRGB, data=img)

        hands = self.hands.detect_for_video(mp_img, timestamp)
        pose  = self.pose.detect_for_video(mp_img, timestamp)

        if debug:
            tracking_debug(img, pose, hands)
        return cvtColor(img, COLOR_BGR2RGB), hands, pose
    

def tracking_debug(frame, pose_results, hands_results):
    if hands_results and hands_results.hand_landmarks:
        for hand in hands_results.hand_landmarks:
            for lm in hand:
                circle(frame, (int(lm.x*frame.shape[1]), int(lm.y*frame.shape[0])), 3, (0,255,0), -1)
    if pose_results and pose_results.pose_landmarks:
        for pose in pose_results.pose_landmarks:
            for lm in pose:
                circle(frame, (int(lm.x*frame.shape[1]), int(lm.y*frame.shape[0])), 3, (255,0,0), -1)


def split_players(pose_result, hands_result, shape):
    left_pose = None
    right_pose = None

    if not pose_result or not pose_result.pose_landmarks:
        return
    
    for p in pose_result.pose_landmarks:
        nose = p[0]
        if nose.x * shape[1] < shape[1] / 2:
            left_pose = p
        else:
            right_pose = p
    
    left_player_hands = {"Left": None, "Right": None}
    right_player_hands = {"Left": None, "Right": None}

    if hands_result and hands_result.hand_landmarks and hands_result.handedness:
        for i, hand in enumerate(hands_result.hand_landmarks):
            classs = hands_result.handedness[i][0]
            type = "Left" if classs.category_name == "Right" else "Right"

            cx = sum(lm.x for lm in hand) / len(hand) * shape[1]

            if left_pose and cx < shape[1] / 2:
                left_player_hands[type] = hand
            elif right_pose and cx >= shape[1] / 2:
                right_player_hands[type] = hand

    return left_pose, right_pose, list(left_player_hands.values()), list(right_player_hands.values())
