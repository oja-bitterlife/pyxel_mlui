import os,os.path
os.chdir(os.path.dirname(__file__))

import sys
sys.path.append("..")
sys.path.append("../..")

from orm import db

# キャラチェック
from orm.user_unit_stocks import USER_UNIT_STOCKS
from orm.user_unit import USER_UNITS

# ステージ開始時初期化
# *****************************************************************************
# HPの初期化
USER_UNITS.reset_unit_hps()

# ユニット情報
# *****************************************************************************
unit_names = USER_UNITS.get_unit_names()
print(unit_names)

for name in unit_names:
    print("ユニットデータ", USER_UNITS.load(name))
    print("保有アイテム", list(USER_UNIT_STOCKS(name).stocks))
    print()
