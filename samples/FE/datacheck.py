import os,os.path
os.chdir(os.path.dirname(__file__))

import sys
sys.path.append("..")
sys.path.append("../..")

from orm import db

# キャラチェック
from orm.user_unit_stocks import UserUnitStocks
from samples.FE.orm.user_units import UserUnits
from samples.FE.orm.user_unit_state import UserUnitState

# チェックするステージ
check_stage = 1

# ステージ情報が入るまでとりあえず全員
unit_names = UserUnits.get_unit_names()
print(unit_names)

# ユニット情報
# *****************************************************************************
for name in unit_names:
    unit = UserUnitState(name)
    print("ユニットデータ", unit)
    print("保有アイテム", list(UserUnitStocks(unit.unit_id).stocks))
    print()

for enemy in UserUnits.get_map_enemies(1):
    print(enemy)
