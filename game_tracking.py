from numpy import array, int32
from cv2 import minEnclosingCircle, FONT_HERSHEY_SIMPLEX, putText, line, getTextSize, rectangle
from utils.line import crossRS as cross_ray_segment
from utils.line import Segment, Ray


def finger_dist(a, b, hand, shape) -> float:
    if hand is None:
        return 0.0
    x1, y1 = hand[a].x * shape[1], hand[a].y * shape[0]
    x2, y2 = hand[b].x * shape[1], hand[b].y * shape[0]
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def is_pistol(hand, shape) -> bool:
    v1  = finger_dist(0, 20, hand, shape)
    v2  = finger_dist(0, 18, hand, shape)
    v3  = finger_dist(0, 12, hand, shape)
    v4  = finger_dist(0, 10, hand, shape)
    v5  = finger_dist(0, 16, hand, shape)
    v6  = finger_dist(0, 14, hand, shape)
    v7  = finger_dist(12, 8, hand, shape)
    v8  = finger_dist(10, 8, hand, shape)
    v9  = finger_dist(4, 5, hand, shape)
    v10 = finger_dist(4, 9, hand, shape)

    return (
        v1 - v2 < 0 and
        v3 - v4 < 0 and
        v5 - v6 < 0 and
        v7 - v8 > 0 and
        v10 - v9 > 0
    )


def is_shield(hand, shape) -> bool:
    if hand is None:
        return False

    points = array(
        [[m.x * shape[1], m.y * shape[0]] for m in hand],
        dtype=int32
    )

    x1, y1 = hand[0].x * shape[1], hand[0].y * shape[0]
    x2, y2 = hand[5].x * shape[1], hand[5].y * shape[0]

    ws = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    _, r = minEnclosingCircle(points)

    return (2 * r / ws) < 1.6


def debugf(frame, player1, player2):
    if player1.collider:
        start = (int(player1.collider[0].start.x), int(player1.collider[0].start.y))
        end =                                                                                (int(player1.collider[2].end.x), int(player1.collider[2].end.y))
        line(frame, start, end, (255,70,0), 2)

    if player2.collider:
        start = (int(player2.collider[0].start.x), int(player2.collider[0].start.y))
        end = (int(player2.collider[2].end.x), int(player2.collider[2].end.y))
        line(frame, start, end, (0,70,255), 2)

    putText(frame, f"P1: {player1.state}", (50,50), FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    putText(frame, f"P2: {player2.state}", (50,80), FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    
    if player1._shot:
        putText(frame, "P1 shot!", (50,110), FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    if player2._shot:
        putText(frame, "P2 shot!", (50,140), FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    
    debug_tag(frame, player1, 1)
    debug_tag(frame, player2, 2)

    line(frame, (frame.shape[1]//2, 0), (frame.shape[1]//2, frame.shape[0]), (0, 255, 0), 4)


def debug_tag(frame, player, index):
    if player.pose is None or len(player.pose) < 1:
        return
    
    nose = player.pose[0]
    x = int(nose.x * player.img_shape[1])
    y = int(nose.y * player.img_shape[0]) - 20

    text = f"#{index} {player.state}"
    (w, h), _ = getTextSize(text, FONT_HERSHEY_SIMPLEX, 0.5, 1)

    rectangle(frame, (x - 2, y - h - 2), (x + w + 2, y + 2), (50, 50, 50), -1)
    putText(frame, text, (x, y), FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


class Human:
    def __init__(self, hands_results, pose_results, img_shape):
        self.pose = pose_results
        self.img_shape = img_shape
        self.left_hand = hands_results
        self.right_hand = hands_results

        self.hp = 3
        self.won = 0
        self.state = "Nothing"
        self._shot = False

        self.safe = {
            "head": False,
            "Body": False,
            "Legs": False,
        }

    @property
    def ready(self):
        return (
            self.pose is not None and
            self.left_hand is not None and
            self.right_hand is not None and
            len(self.pose) >= 33
        )

    @property
    def left_hand(self):
        return self._left_hand
    @left_hand.setter
    def left_hand(self, hand):
        self._left_hand = hand

    @property
    def right_hand(self):
        return self._right_hand
    @right_hand.setter
    def right_hand(self, hand):
        self._right_hand = hand

    def update_state(self, shape):
        if is_pistol(self.right_hand, shape):
            self.state = "Gun"
        elif is_shield(self.left_hand, shape):
            self.state = "Shield"
        else:
            self.state = "Nothing"
            self._shot = False

    @property
    def collider(self):      
        if self.pose is None or len(self.pose) < 33:
            return None
    
        nose, neck = self.pose[0], self.pose[1]
        k1, k2 = self.pose[31], self.pose[32]

        head = (
            int(nose.x * self.img_shape[1]),
            int(nose.y * self.img_shape[0] - 4 * (nose.y - neck.y) * self.img_shape[0]))
        
        neck = (
            int(neck.x * self.img_shape[1]),
            int(neck.y * self.img_shape[0])
        )

        hip1, hip2 = self.pose[24], self.pose[23]

        hip = (
            int((hip1.x + hip2.x) * 0.5 * self.img_shape[1]),
            int((hip1.y + hip2.y) * 0.5 * self.img_shape[0])
        )

        knees = (
            int((k1.x + k2.x) * 0.5 * self.img_shape[1]),
            int((k1.y + k2.y) * 0.5 * self.img_shape[0]))
        return Segment(head, neck), Segment((neck[0], neck[1] - 1), hip), Segment((hip[0], hip[1] - 1), knees)

    @property
    def bullet(self):
        try:
            start = (
                self.pose[14].x *  self.image_shape[1],
                self.pose[14].y *  self.image_shape[0])
            end = (
                self.pose[16].x *  self.image_shape[1],
                self.pose[16].y *  self.image_shape[0])
            
            return Ray(start=start, point=end)
        except:
            return None

    @property
    def shield(self):
        x = self.pose[16].x *  self.image_shape[1]
        y = self.pose[16].y *  self.image_shape[0]
        
        segments = self.collider
        
        if min(segments[0].start.y, segments[0].end.y) <= y <= max(segments[0].start.y, segments[0].end.y):
            self.safe["head"] = True
        elif min(segments[1].start.y, segments[1].end.y) <= y <= max(segments[1].start.y, segments[1].end.y):
            self.safe["body"] = True
        elif min(segments[2].start.y, segments[2].end.y) <= y <= max(segments[2].start.y, segments[2].end.y):
            self.safe["legs"] = True

    def shoot(self, enemy) -> bool:
        if self.state != "Gun" or self._shot:
            return False
        self._shot = True

        if enemy.state == "Shield":
            enemy.shield

        if cross_ray_segment(self.bullet, enemy.collider[0]):
            if enemy.safe['head']:
                return False
            else:
                self.won += 1
                enemy.hp -= 1.5
                return True
            
        elif cross_ray_segment(self.bullet, enemy.collider[1]):
            if enemy.safe['body']:
                return False
            else:
                self.won += 1
                enemy.hp -= 1
                return True
        elif cross_ray_segment(self.bullet, enemy.collider[2]):
            if enemy.safe['legs']:
                return False
            else:
                self.won += 1
                enemy.hp -= .5
                return True
        else:
            return False

