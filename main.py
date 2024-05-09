import pandas as pd
from datetime import datetime
from time import perf_counter
from random import choice
HILLCLIMBING_TIME = 10
class Person:
    def __init__(self, name, coment):
        self.__name = name
        self.__coment = coment
        self.__aviliable_timeframes = set()
        self.__scheduled_timeframes = set()
        
    def add_scheduled_timeframe(self, time):
        """指定された時間帯を予定された時間帯に追加します。"""
        self.__scheduled_timeframes.add(time)
        
    def add_aviliable_timeframe(self, time):
        """指定された時間帯を利用可能な時間帯に追加します。"""
        self.__aviliable_timeframes.add(time)
    
    def discard_scheduled_timeframe(self, time):
        """指定された時間帯を予定された時間帯から削除します。"""
        self.__scheduled_timeframes.discard(time)
        
    def discard_aviliable_timeframe(self, time):
        """指定された時間帯を利用可能な時間帯から削除します。"""
        self.__aviliable_timeframes.discard(time)
    
    def get_sorted_scheduled_timeframes(self):
        """予定された時間帯をソートして返します。"""
        return sorted(self.__scheduled_timeframes)
    
    @property
    def name(self):
        return self.__name
    
    @property
    def comrent(self):
        return self.__coment
    
    @property
    def avilible_timeframes_num(self):
        return len(self.__aviliable_timeframes)
    
    @property
    def scheduled_timeframes_num(self):
        return len(self.__scheduled_timeframes)
    
    @property
    def aviliable_timeframes(self):
        return self.__aviliable_timeframes
    
    @property
    def scheduled_timeframes(self):
        return self.__scheduled_timeframes

class Timeframe:
    def __init__(self, name):
        self.__name = name
        self.__aviliable_persons = set()
        self.__scheduled_persons = set()
        
    def add_scheduled_person(self, person):
        """指定された人物を予定された人物に追加します。"""
        self.__scheduled_persons.add(person)
        
    def add_aviliable_person(self, person):
        """指定された人物を利用可能な人物に追加します。"""
        self.__aviliable_persons.add(person)
        
    def discard_scheduled_person(self, person):
        """指定された人物を予定された人物に追加します。"""
        self.__scheduled_persons.discard(person)
        
    def dicsard_aviliable_person(self, person):
        """指定された人物を利用可能な人物に追加します。"""
        self.__aviliable_persons.discard(person)
        
    def get_sorted_scheduled_persons(self):
        """予定された人物をソートして返します。"""
        return sorted(self.__scheduled_persons)
    
    @property
    def name(self):
        return self.__name
    
    @property
    def aviliable_persons_num(self):
        return len(self.__aviliable_persons)
    
    @property
    def scheduled_persons_num(self):
        return len(self.__scheduled_persons)
        
    @property
    def aviliable_persons(self):
        return self.__aviliable_persons
    
    @property
    def scheduled_persons(self):
        return self.__scheduled_persons
        
def input_need_number():
    """必要な人数をユーザーに入力させます。"""
    num = int(input("時間帯ごとに必要な人数を入力してください。: "))
    return num

def read_questionnaire_data():
    """アンケートデータを読み込みます。"""
    df = pd.read_csv("chouseisan.csv", header=1, index_col='日程')
    return df
    
def get_aggregate_data(df):
    """DataFrameから人と時間帯のデータを集計します。"""
    persons = {}
    timeframes = {}
    for timeframe_name, row in df.iterrows():
        if timeframe_name != "コメント":
            timeframes[timeframe_name] = Timeframe(timeframe_name)
            for person_name, value in row.items():
                if value == "◯":
                    if person_name not in persons:
                        persons[person_name] = Person(person_name, df.loc["コメント", person_name])
                    persons[person_name].add_aviliable_timeframe(timeframe_name)
                    timeframes[timeframe_name].add_aviliable_person(person_name)
    return persons, timeframes

def create_initial_schedule_greedy(persons, timeframes, required_persons_num):
    """貪欲法により初期スケジュールを作成します。"""
    rest_required_shifts_num = required_persons_num * len(timeframes)
    for index, person in enumerate(sorted(persons.values(), key=lambda x: x.avilible_timeframes_num)):
        need_shifts_num = -(-rest_required_shifts_num // (len(persons) - index))
        for timeframe_name in person.aviliable_timeframes:
            if timeframes[timeframe_name].scheduled_persons_num < required_persons_num:
                rest_required_shifts_num -= 1
                person.add_scheduled_timeframe(timeframe_name)
                timeframes[timeframe_name].add_scheduled_person(person.name)
            if person.scheduled_timeframes_num == need_shifts_num:
                break
    for timeframe in timeframes.values():
        for person_name in timeframe.aviliable_persons:
            if timeframe.scheduled_persons_num < required_persons_num:
                persons[person_name].add_scheduled_timeframe(timeframe.name)
                timeframe.add_scheduled_person(person_name)

def timeframe_swap(timeframes,a_person,b_person):
    a_s = a_person.scheduled_timeframes
    a_a = a_person.aviliable_timeframes
    b_s = b_person.scheduled_timeframes
    b_a = b_person.aviliable_timeframes
    a_to_b_timeframes = a_s - b_s & b_a
    b_to_a_timeframes = b_s - a_s & a_a
    if a_to_b_timeframes and b_to_a_timeframes:
        a_to_b = a_to_b_timeframes.pop()
        b_to_a = b_to_a_timeframes.pop()
        a_person.discard_scheduled_timeframe(a_to_b)
        b_person.discard_scheduled_timeframe(b_to_a)
        a_person.add_scheduled_timeframe(b_to_a)
        b_person.add_scheduled_timeframe(a_to_b)
        timeframes[a_to_b].discard_scheduled_person(a_person.name)
        timeframes[b_to_a].discard_scheduled_person(b_person.name)
        timeframes[a_to_b].add_scheduled_person(b_person.name)
        timeframes[b_to_a].add_scheduled_person(a_person.name)
        
        

def timeframe_change(timeframes,send_person,receive_person):
    s_s = send_person.scheduled_timeframes
    s_a = send_person.aviliable_timeframes
    r_s = receive_person.scheduled_timeframes
    r_a = receive_person.aviliable_timeframes
    s_to_r_timeframes = s_s - r_s & r_a
    if s_to_r_timeframes:
        s_to_r = s_to_r_timeframes.pop()
        send_person.discard_scheduled_timeframe(s_to_r)
        receive_person.add_scheduled_timeframe(s_to_r)
        timeframes[s_to_r].discard_scheduled_person(send_person.name)
        timeframes[s_to_r].add_scheduled_person(receive_person.name)
    
    
               
def mode_0(persons,timeframes,a_person,b_person):
    if a_person.name == b_person.name:
        return

    if a_person.scheduled_timeframes_num == b_person.scheduled_timeframes_num:
        timeframe_swap(timeframes,a_person,b_person)
    elif a_person.scheduled_timeframes_num > b_person.scheduled_timeframes_num:
        timeframe_change(timeframes,a_person,b_person)
    elif a_person.scheduled_timeframes_num < b_person.scheduled_timeframes_num:
        timeframe_change(timeframes,b_person,a_person)
        


def mode_1(persons,timeframes,timeframe,required_person_num):
    t_a = timeframe.aviliable_persons 
    t_s = timeframe.scheduled_persons
    tmp = t_a - t_s
    while tmp and timeframe.scheduled_persons_num < required_person_num:
        add_person = tmp.pop()
        timeframe.add_scheduled_person(add_person)
        persons[add_person].add_scheduled_timeframe(timeframe.name)
        tmp = t_a - t_s
        
        
 

def optimize_schedule_hill_climbing(persons, timeframes, required_persons_num):
    """山登り法によりスケジュールを最適化します。"""
    start_time = perf_counter()
    cnt = 0
    persons_name_list = list(persons.keys())
    timeframes_name_list = list(timeframes.keys())
    while True:
        cnt += 1
        if cnt % 100 == 0 and perf_counter() - start_time > HILLCLIMBING_TIME:
            break
        mode = choice([0,0,0,0,1])
        if mode == 0:
            a_person_name,b_person_name = choice(persons_name_list),choice(persons_name_list)
            mode_0(persons,timeframes,persons[a_person_name],persons[b_person_name])
        elif mode == 1:
            timeframe_name = choice(timeframes_name_list)
            mode_1(persons,timeframes,timeframes[timeframe_name],required_persons_num)
            
        

def calc_scheduled_data(persons, timeframes, need_persons_num):
    """スケジュールデータの計算を行います。"""
    create_initial_schedule_greedy(persons, timeframes, need_persons_num)
    optimize_schedule_hill_climbing(persons, timeframes, need_persons_num)

def get_normalized_and_trans_df(persons, timeframes):
    """正規化され、転置されたデータフレームを取得します。"""
    persons_schedules = {i: j.get_sorted_scheduled_timeframes() for i, j in persons.items()}
    max_len = max(len(i) for i in persons_schedules.values())
    for scheduled_timeframes in persons_schedules.values():
        scheduled_timeframes.extend([None] * (max_len - len(scheduled_timeframes)))
    person_df = pd.DataFrame(persons_schedules).transpose()
    
    timeframes_schedules = {i: j.get_sorted_scheduled_persons() for i, j in timeframes.items()}
    max_len = max(len(i) for i in timeframes_schedules.values())
    for scheduled_persons in timeframes_schedules.values():
        scheduled_persons.extend([None] * (max_len - len(scheduled_persons)))
    timeframes_df = pd.DataFrame(timeframes_schedules).transpose()
    
    return person_df, timeframes_df
        
def outout_csv_data(persons, timeframes):
    """生成されたスケジュールデータをCSVに出力します。"""
    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    persons_df, timeframes_df = get_normalized_and_trans_df(persons, timeframes)
    persons_df.to_csv(f"{now}_persons_shift.csv", header=False,encoding='cp932')
    timeframes_df.to_csv(f"{now}_timeframes_shift.csv", header=False,encoding='cp932')
    
def main():
    """メイン関数：必要な処理を一連の手順で実行します。"""
    required_persons_num = input_need_number()
    questionnaire_data = read_questionnaire_data()
    persons, timeframes = get_aggregate_data(questionnaire_data)
    calc_scheduled_data(persons, timeframes, required_persons_num)
    outout_csv_data(persons, timeframes)

if __name__ == "__main__":
    main()