import os,os.path
os.chdir(os.path.dirname(__file__))

import sys
sys.path.append("..")
sys.path.append("../..")

from orm import db

# キャラチェック
from orm.user_unit_stocks import USER_UNIT_STOCKS
from orm.user_unit import USER_UNITS

print(list(USER_UNIT_STOCKS("オジャダ").stocks))
print(list(USER_UNIT_STOCKS("オジャル").stocks))
print(list(USER_UNIT_STOCKS("オジャドン").stocks))
print(list(USER_UNIT_STOCKS("オジャナ").stocks))

print("ユニットデータ")
unit_names = USER_UNITS.get_unit_names()
print(unit_names)

for name in unit_names:
    print(USER_UNITS.load_param(name), USER_UNITS.load_state(name))

print("保有アイテム")
for name in unit_names:
    print(list(USER_UNIT_STOCKS(name).stocks))
