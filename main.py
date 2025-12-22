from cv2 import VideoCapture, CAP_PROP_BUFFERSIZE, flip
from utils.tracking import MediaPipeFacade, split_players
from game_tracking import *
from ui import UI_EVENTS, UIController

GAME = {
    "state": "menu",#menu, instruction, check, countdown, round
    "countdown": 3,
    "error": None
}
ui = UIController()

def check_players(first, second):
    if first.pose is None or second.pose is None:
        return "Нужно два игрока"

    if not first.ready or not second.ready:
        return "Руки или позы не видны"

    if first.state != "Nothing" or second.state != "Nothing":
        return "Уберите руки (ничего не показывайте)"

    return None

def round(first, second):
    ...

    return None


def main():
    cap = VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 360)
    cap.set(CAP_PROP_BUFFERSIZE, 1)

    mp_facade = MediaPipeFacade()

    first_player = Human(None, None, (640, 360))
    second_player = Human(None, None, (640, 360))

    frame_number = 0

    while True:
        cap.grab()
        ret, frame = cap.retrieve()
        frame = flip(frame, 1)
        if not ret:
            break

        if frame_number % 3 == 0:
            frame, hands_results, pose_results = mp_facade.process_frame(frame, debug=True)
        frame_number += 1

        split = split_players(pose_results, hands_results, frame.shape)
        if split:
            left_pose, right_pose, left_hands, right_hands = split

            first_player.pose = left_pose
            first_player.left_hand = left_hands[0]
            first_player.right_hand = left_hands[1]
            first_player.img_shape = frame.shape

            second_player.pose = right_pose
            second_player.left_hand = right_hands[0]
            second_player.right_hand = right_hands[1]
            second_player.img_shape = frame.shape

            first_player.update_state(frame.shape)
            second_player.update_state(frame.shape)

        # ------------ game logic -------------

        if GAME["state"] == "menu":

            if UI_EVENTS["start"]:
                UI_EVENTS["start"] = False
                GAME["state"] = "instruction"

        elif GAME["state"] == "instruction":

            if UI_EVENTS["instruction_yes"] or UI_EVENTS["instruction_no"]:
                UI_EVENTS["instruction_yes"] = False
                UI_EVENTS["instruction_no"] = False
                GAME["state"] = "check"

        elif GAME["state"] == "check":
            GAME["error"] = check_players(first_player, second_player)

            if GAME["error"] is None:
                GAME["countdown"] = 3
                GAME["state"] = "countdown"

        elif GAME["state"] == "countdown":
            GAME["error"] = check_players(first_player, second_player)

            if GAME["error"] is not None:
                GAME["state"] = "check"
            else:
                putText(frame, str(GAME["countdown"]), (frame.shape[1] // 2 - 30, frame.shape[0] // 2), 
                    FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 6)

                if frame_number % 30 == 0:
                    GAME["countdown"] -= 1

                if GAME["countdown"] <= 0:
                    GAME["state"] = "round"

        elif GAME["state"] == "round":
            round(first_player, second_player)
            GAME["state"] = "result"
            GAME["result_timer"] = 90

        elif GAME["state"] == "result":
            putText(frame, f"Счёт: {first_player.won} : {second_player.won}", 
                    (frame.shape[1]//2 - 200, frame.shape[0]//2), FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
            GAME["result_timer"] -= 1
            if GAME["result_timer"] <= 0:
                GAME["state"] = "menu"

        if GAME["error"]:
            putText(frame, GAME["error"], (50, frame.shape[0] - 40),
                FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)

        debugf(frame, first_player, second_player)
        ui.show_error(GAME["error"])
        ui.draw_frame(frame)

if __name__ == "__main__":
    main()
