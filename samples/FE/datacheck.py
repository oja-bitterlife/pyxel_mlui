import os,os.path
os.chdir(os.path.dirname(__file__))

import sys
sys.path.append("..")
sys.path.append("../..")

from orm import db

# キャラチェック
from orm.user_unit_stocks import USER_UNIT_STOCKS
from orm.user_unit import USER_UNITS

print("保有アイテム")
print(list(USER_UNIT_STOCKS("オジャス").stocks))
print(list(USER_UNIT_STOCKS("オジャダ").stocks))
print(list(USER_UNIT_STOCKS("オジャル").stocks))
print(list(USER_UNIT_STOCKS("オジャドン").stocks))
print(list(USER_UNIT_STOCKS("オジャナ").stocks))

print("ユニットデータ")
USER_UNITS("オジャス").load()

