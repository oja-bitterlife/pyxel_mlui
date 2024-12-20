import sys

class WebIF:
    def __init__(self):
        self.is_web = "_pyodide" in sys.modules
