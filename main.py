from cv2 import VideoCapture, CAP_PROP_BUFFERSIZE, flip
from utils.tracking import MediaPipeFacade, split_players
from game_tracking import *
from ui import UI_EVENTS, UIController
import time

GAME = {
    "state": "menu",#menu, ask_rules, rules, check, countdown, round, final
    "num_people": 0,
    "countdown": 3,
    "reaction_time": 5,
    "error": None,
}

ui = UIController()

def check_players(first, second):
    if GAME.get("num_people", 0) != 2:
        if GAME.get("num_people", 0) == 0:
            return "Нужно только два игрока!"
        else:
            return "В кадре должно быть ровно 2 игрока!"

    if not first.in_ready_pos or not second.in_ready_pos:
        return "Все руки или колени не видны! (Могут быть не в своей половине кадра!)"

    if first.state != "Nothing" or second.state != "Nothing":
        return "Не показывайте жесты!"

    return None

def round(first_player, second_player, shape):

    if first_player.right_hand is not None and is_pistol(first_player.right_hand, shape):
        first_player.state = "Gun"
    elif first_player.left_hand is not None and is_shield(first_player.left_hand, shape):
        first_player.state = "Shield"
    else:
        first_player.state = "Nothing"

    if second_player.right_hand is not None and is_pistol(second_player.right_hand, shape):
        second_player.state = "Gun"
    elif second_player.left_hand is not None and is_shield(second_player.left_hand, shape):
        second_player.state = "Shield"
    else:
        second_player.state = "Nothing"

    if first_player.state == "Gun" and second_player.state != 'Gun':
        result = "ПЕРВЫЙ:" + first_player.shoot(second_player)
    elif first_player.state != "Gun" and second_player.state == "Gun":
        result = "ВТОРОЙ:" + second_player.shoot(first_player)
    elif first_player.state == "Gun" and second_player.state == 'Gun':
        result = "ПЕРВЫЙ" + first_player.shoot(second_player) + "\n" + "ВТОРОЙ:" + second_player.shoot(first_player)
    else:
        result = "НЕТ ВЫСТРЕЛОВ"
    
    return result

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

        if frame_number % 1 == 0:
            frame, hands_results, pose_results = mp_facade.process_frame(frame, debug=True)
        frame_number += 1

        split = split_players(pose_results, hands_results, frame.shape)

        if pose_results and pose_results.pose_landmarks:
            GAME["num_people"] = len(pose_results.pose_landmarks)
        else:
            GAME["num_people"] = 0
        
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
            ui.show_menu()

            if UI_EVENTS["start"]:
                UI_EVENTS["start"] = False
                GAME["state"] = "ask_rules"

            elif UI_EVENTS["open_rules"]:
                UI_EVENTS["open_rules"] = False
                GAME["state"] = "rules"

        elif GAME["state"] == "ask_rules":
            ui.show_ask_rules()

            if UI_EVENTS["instruction_yes"]:
                UI_EVENTS["instruction_yes"] = False
                GAME["state"] = "rules"

            if UI_EVENTS["instruction_no"]: 
                UI_EVENTS["instruction_no"] = False
                GAME["state"] = "check"

        elif GAME["state"] == "rules":
            ui.show_rules()

            if UI_EVENTS["continue_game"]:
                UI_EVENTS["continue_game"] = False
                GAME["state"] = "check"

        elif GAME["state"] == "check":
            ui.show_game()
            GAME["error"] = check_players(first_player, second_player)

            if GAME["error"] is None:
                countdown_time = time.time()
                GAME["countdown"] = 3
                GAME["state"] = "countdown"

        elif GAME["state"] == "countdown":
            GAME["error"] = check_players(first_player, second_player)

            if GAME["error"] is not None:
                GAME["state"] = "check"
            else:
                ui.show_text(GAME["countdown"])
                current_time = time.time()
                if current_time - countdown_time >= 1:
                    GAME["countdown"] -= 1
                    countdown_time = current_time

                if GAME["countdown"] < 0:
                    ui.window.play_go_sound()
                    GAME["state"] = "round"
                    reaction_time = time.time()

        elif GAME["state"] == "round":
            ui.show_game()
            ui.update_hp(int(first_player.hp), int(second_player.hp))
            current_time = time.time()
            if current_time - reaction_time >= 2.5:
                result = round(first_player, second_player, frame.shape)
                GAME["round_result"] = result
                GAME["state"] = "result"
                GAME["result_timer"] = 40

        elif GAME["state"] == "result":
            ui.show_game()
            ui.update_hp(int(first_player.hp), int(second_player.hp))
            ui.show_text(GAME["round_result"])

            GAME["result_timer"] -= 1
            if GAME["result_timer"] <= 0:
                GAME["round_result"] = ""

                if first_player.hp > 0 and second_player.hp > 0:
                    GAME["state"] = "check"
                else:
                    GAME["state"] = "final"

        elif GAME["state"] == "final":
            ui.show_game()

            if first_player.hp > second_player.hp:
                text = "ПРАВЫЙ ИГРОК ПОБЕДИЛ!"
            elif second_player.hp > first_player.hp:
                text = "ВТОРОЙ ИГРОК ПОБЕДИЛ!"
            else:
                text = "НИЧЬЯ"

            ui.show_final_result(text)

            GAME["result_timer"] -= 1
            if GAME["result_timer"] <= 0:
                first_player.hp = 3
                second_player.hp = 3
                first_player.state = "Nothing"
                second_player.state = "Nothing"
                GAME["state"] = "menu"

        debugf(frame, first_player, second_player)
        ui.draw_frame(frame)
        ui.show_error(GAME["error"])

if __name__ == "__main__":
    main()
