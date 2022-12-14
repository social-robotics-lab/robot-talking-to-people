import random
import threading
import time
import pymongo

# --------------------------------------------------------
# BehaviorはStateと一対一対応する。
# あるStateに入ると前回のStateで開始されたBehaviorは停止され、
# 次のStateに対応するBehaviorが開始される。
# --------------------------------------------------------
class Behavior:
    def __init__(self, db, document:dict):
        self.db = db
        self.running = False
    
    def start(self):
        """ Behaviorを開始 """
        self.running = True
        print(f'{self.__class__.__name__} started.')
        threading.Thread(target=self.run, daemon=True).start()
    
    def stop(self):
        """ Behaviorを終了 """
        self.running = False
        print(f'{self.__class__.__name__} stopped.')

    def to_document(self) -> dict:
        """ MongoDBにinsertするデータ形式に変換 """
        return dict(name=self.__class__.__name__)

    def run(self):
        """ Behavior実行中の処理をここで実装する """
        pass


class Init(Behavior):
    def start(self):
        pass

    def stop(self):
        pass

class Idle(Behavior):
    """ アイドル状態 """
    def __init__(self, db, document:dict):
        super().__init__(db, document)
        self.prev_look_direction = {}
    
    def run(self):
        self.start_idling_motion()
        while self.running:
            self.look_around()
            time.sleep(5)
        self.stop_idling_motion()

    def start_idling_motion(self):
        print('Idle motion started.')
    
    def stop_idling_motion(self):
        print('Idle motion stopped.')

    def look_around(self):
        RANDOM_DIRECTION = [
            {'pitch' : 0, 'yaw' : -100}, {'pitch' : 0, 'yaw' : -50 },
            {'pitch' : 0, 'yaw' :  50 }, {'pitch' : 0, 'yaw' :  100},
        ]
        direction = random.choice([d for d in RANDOM_DIRECTION if d != self.prev_look_direction])  
        # servo_map = dict(BODY_Y=0, HEAD_P=direction['pitch'], HEAD_Y=direction['yaw'])
        # msec = calc_msec(ip, port, servo_map, speed=1.0)
        # pose = dict(Msec=msec, Servo_map=servo_map)
        # cl.play_pose(ip, port, pose)
        print(f'Looked at {direction}.')


class Greet(Behavior):
    def __init__(self, db, document:dict):
        super().__init__(db, document)
        self.target_id = document['target_id']
    
    def to_document(self):
        return dict(name=self.__class__.__name__, target_id=self.target_id)

    def run(self):
        """ ターゲットを見て挨拶し、その後ターゲットを見続ける """
        self.start_idling_motion()
        self.look_at_target()
        self.say()
        while self.running:
            self.look_at_target()
            time.sleep(3)
        self.stop_idling_motion()

    def start_idling_motion(self):
        print('Idle motion started.')
    
    def stop_idling_motion(self):
        print('Idle motion stopped.')

    def say(self):
        print('Said hello.')

    def look_at_target(self):
        document = self.db['human_recognition'].find_one({ 
            'results.id' : self.target_id
        })
        r = next(result for result in document['results'] if result['id'] == self.target_id)
        x = r['x1'] + (r['x2'] - r['x1']) / 2.0
        y = r['y1'] + (r['y2'] - r['y1']) / 4.0
        # servo_map = calc_servo_map_head(x, y)
        # pose = dict(Msec=500, ServoMap=servo_map)
        # cl.play_pose(ip, port, pose)    
        print(f'Look at target {self.target_id}, x={x}, y={y}')