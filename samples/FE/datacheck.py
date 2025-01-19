import os,os.path
os.chdir(os.path.dirname(__file__))

import sys
sys.path.append("..")
sys.path.append("../..")

from orm import db

# キャラチェック
from orm.user_unit_stocks import USER_UNIT_STOCKS
from samples.FE.orm.user_units import USER_UNITS
from samples.FE.orm.user_unit_state import USER_UNIT_STATE

# チェックするステージ
check_stage = 1

# ステージ情報が入るまでとりあえず全員
unit_names = USER_UNITS.get_unit_names()
print(unit_names)

# ユニット情報
# *****************************************************************************
for name in unit_names:
    unit = USER_UNIT_STATE(name)
    print("ユニットデータ", unit)
    print("保有アイテム", list(USER_UNIT_STOCKS(unit.unit_id).stocks))
    print()

for enemy in USER_UNITS.get_map_enemies(1):
    print(enemy)
