from __future__ import annotations
import pandas as pd
from datetime import datetime
from time import perf_counter
from random import choice
from typing import List, Dict, Set, Tuple

# 定数
HILLCLIMBING_TIME = 10  # 山登りを行う時間（秒）


class Person:
    def __init__(self, name: str, comment: str) -> None:
        self._name = name
        self._comment = comment
        self._aviliable_timeframes = set()
        self._scheduled_timeframes = set()

    def add_scheduled_timeframe(self, time: str) -> None:
        """指定された時間帯を予定された時間帯に追加します。"""
        self._scheduled_timeframes.add(time)

    def add_aviliable_timeframe(self, time: str) -> None:
        """指定された時間帯を利用可能な時間帯に追加します。"""
        self._aviliable_timeframes.add(time)

    def discard_scheduled_timeframe(self, time: str) -> None:
        """指定された時間帯を予定された時間帯から削除します。"""
        self._scheduled_timeframes.discard(time)

    def discard_aviliable_timeframe(self, time: str) -> None:
        """指定された時間帯を利用可能な時間帯から削除します。"""
        self._aviliable_timeframes.discard(time)

    def get_sorted_scheduled_timeframes(
        self, timeframes: Dict[str:Timeframe]
    ) -> List[str]:
        """予定された時間帯を入力CVSファイルの並び順にソートして返します。"""
        return sorted(self._scheduled_timeframes, key=lambda x: timeframes[x].id)

    @property
    def name(self) -> str:
        return self._name

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def aviliable_timeframes_num(self) -> int:
        return len(self._aviliable_timeframes)

    @property
    def scheduled_timeframes_num(self) -> int:
        return len(self._scheduled_timeframes)

    @property
    def aviliable_timeframes(self) -> Set[str]:
        return self._aviliable_timeframes

    @property
    def scheduled_timeframes(self) -> Set[str]:
        return self._scheduled_timeframes


class Timeframe:
    def __init__(self, name: str, id_: int) -> None:
        self._name = name
        self._id = id_
        self._aviliable_persons = set()
        self._scheduled_persons = set()

    def add_scheduled_person(self, person: str) -> None:
        """指定された人物を予定された人物に追加します。"""
        self._scheduled_persons.add(person)

    def add_aviliable_person(self, person: str) -> None:
        """指定された人物を利用可能な人物に追加します。"""
        self._aviliable_persons.add(person)

    def discard_scheduled_person(self, person: str) -> None:
        """指定された人物を予定された人物から削除します。"""
        self._scheduled_persons.discard(person)

    def discard_aviliable_person(self, person: str) -> None:
        """指定された人物を利用可能な人物から削除します。"""
        self._aviliable_persons.discard(person)

    def get_sorted_scheduled_persons(self, persons: Dict[str:Person]) -> List[str]:
        """予定された人物をコメントでソートして返します。"""
        return sorted(self._scheduled_persons, key=lambda x: persons[x].comment)

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @property
    def aviliable_persons_num(self) -> int:
        return len(self._aviliable_persons)

    @property
    def scheduled_persons_num(self) -> int:
        return len(self._scheduled_persons)

    @property
    def aviliable_persons(self) -> Set[str]:
        return self._aviliable_persons

    @property
    def scheduled_persons(self) -> Set[str]:
        return self._scheduled_persons


def input_need_number() -> int:
    """必要な人数をユーザーに入力させます。"""
    num = int(input("時間帯ごとに必要な人数を入力してください。: "))
    return num


def read_questionnaire_data() -> pd.DataFrame:
    """アンケートデータを読み込みます。"""
    df = pd.read_csv(
        "chouseisan.csv", header=1, index_col="日程", encoding="cp932", dtype=str
    )
    df = df.fillna('')
    return df


def get_aggregate_data(
    df: pd.DataFrame,
) -> Tuple[Dict[str:Person], Dict[str:Timeframe]]:
    """DataFrameから人と時間帯のデータを集計します。"""
    persons = {}
    timeframes = {}
    for index, (timeframe_name, row) in enumerate(df.iterrows()):
        if timeframe_name != "コメント":
            timeframes[timeframe_name] = Timeframe(timeframe_name, index)
            for person_name, value in row.items():
                if value == "◯":
                    if person_name not in persons:
                        persons[person_name] = Person(
                            person_name, df.loc["コメント", person_name]
                        )
                    persons[person_name].add_aviliable_timeframe(timeframe_name)
                    timeframes[timeframe_name].add_aviliable_person(person_name)
    return persons, timeframes


def create_initial_schedule_greedy(
    persons: Dict[str:Person],
    timeframes: Dict[str:Timeframe],
    required_persons_num: int,
) -> None:
    """貪欲法により初期スケジュールを作成します。"""
    rest_required_shifts_num = required_persons_num * len(timeframes)
    for index, person in enumerate(
        sorted(persons.values(), key=lambda x: x.aviliable_timeframes_num)
    ):
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


def timeframe_swap(
    timeframes: Dict[str:Timeframe], a_person: Person, b_person: Person
) -> bool:
    """シフトを交換します。"""
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
        return True
    else:
        return False


def timeframe_change(
    timeframes: Dict[str:Timeframe], send_person: Person, receive_person: Person
) -> bool:
    """シフト受け持つ人を変更します。"""
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
        return True
    else:
        return False


def neighbor_change_0(
    timeframes: Dict[str:Timeframe], a_person: Person, b_person: Person
) -> bool:
    """
    乱択したaさんとbさんの参加シフト回数を比較し、差がある場合は差が縮まるようにする。
    同じ場合は、一部交代できる場合は交代する
    """
    if a_person.name == b_person.name:
        return False

    if a_person.scheduled_timeframes_num == b_person.scheduled_timeframes_num:
        if timeframe_swap(timeframes, a_person, b_person):
            return True
    elif a_person.scheduled_timeframes_num > b_person.scheduled_timeframes_num:
        if timeframe_change(timeframes, a_person, b_person):
            return True
    elif a_person.scheduled_timeframes_num < b_person.scheduled_timeframes_num:
        if timeframe_change(timeframes, b_person, a_person):
            return True
    return False


def neighbor_change_1(
    persons: Dict[str:Person],
    timeframe: Timeframe,
    required_person_num: int,
):
    """選んだ時間帯の人数が不足している場合、追加できる人員がいれば追加する"""
    # 今のところ不必要
    t_a = timeframe.aviliable_persons
    t_s = timeframe.scheduled_persons
    tmp = t_a - t_s
    while tmp and timeframe.scheduled_persons_num < required_person_num:
        add_person = tmp.pop()
        timeframe.add_scheduled_person(add_person)
        persons[add_person].add_scheduled_timeframe(timeframe.name)
        tmp = t_a - t_s


def optimize_schedule_hill_climbing(
    persons: Dict[str:Person], timeframes: Dict[str:Timeframe]
) -> None:
    """山登り法によりスケジュールを最適化します。"""
    start_time = perf_counter()
    cnt = 0
    persons_name_list = list(persons.keys())
    while True:
        cnt += 1
        if cnt % 100 == 0 and perf_counter() - start_time > HILLCLIMBING_TIME:
            break
        a_person_name, b_person_name = choice(persons_name_list), choice(
            persons_name_list
        )
        neighbor_change_0(timeframes, persons[a_person_name], persons[b_person_name])


def calc_scheduled_data(
    persons: Dict[str:Person],
    timeframes: Dict[str:Timeframe],
    required_persons_num: int,
) -> None:
    """スケジュールデータの計算を行います。"""
    create_initial_schedule_greedy(persons, timeframes, required_persons_num)
    optimize_schedule_hill_climbing(persons, timeframes)


def get_normalized_and_trans_df(
    persons: Dict[str:Person], timeframes: Dict[str:Timeframe]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """正規化され、転置されたデータフレームを取得します。"""
    persons_schedules = {
        i: j.get_sorted_scheduled_timeframes(timeframes) for i, j in persons.items()
    }
    max_len = max(len(i) for i in persons_schedules.values())
    for scheduled_timeframes in persons_schedules.values():
        scheduled_timeframes.extend([None] * (max_len - len(scheduled_timeframes)))
    person_df = pd.DataFrame(persons_schedules).transpose()

    timeframes_schedules = {
        i: j.get_sorted_scheduled_persons(persons) for i, j in timeframes.items()
    }
    max_len = max(len(i) for i in timeframes_schedules.values())
    for scheduled_persons in timeframes_schedules.values():
        scheduled_persons.extend([None] * (max_len - len(scheduled_persons)))
    timeframes_df = pd.DataFrame(timeframes_schedules).transpose()

    return person_df, timeframes_df


def outout_csv_data(persons: Dict[str:Person], timeframes: Dict[str:Timeframe]) -> None:
    """生成されたスケジュールデータをCSVに出力します。"""
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    persons_df, timeframes_df = get_normalized_and_trans_df(persons, timeframes)
    persons_df.to_csv(f"{now}_persons_shift.csv", header=False, encoding="cp932")
    timeframes_df.to_csv(f"{now}_timeframes_shift.csv", header=False, encoding="cp932")


def main() -> None:
    """メイン関数：必要な処理を一連の手順で実行します。"""
    required_persons_num = input_need_number()
    questionnaire_data = read_questionnaire_data()
    persons, timeframes = get_aggregate_data(questionnaire_data)
    calc_scheduled_data(persons, timeframes, required_persons_num)
    outout_csv_data(persons, timeframes)


if __name__ == "__main__":
    main()
