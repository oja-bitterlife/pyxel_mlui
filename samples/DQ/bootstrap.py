import os,os.path
os.chdir(os.path.dirname(__file__))

import sys
sys.path.append("..")
sys.path.append("../..")

#　デバッグON
from xmlui.core import XMLUI
XMLUI.debug_enable = True

import main
