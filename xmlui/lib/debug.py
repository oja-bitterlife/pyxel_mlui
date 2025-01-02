from xmlui.core import XMLUI

# デバッグ用
class XMLUIDebug(XMLUI):
    DEBUGEVENT_PRINTTREE = "DEBUG_PRINTTREE"
    DEBUGEVENT_RELOAD = "DEBUG_RELOAD"

    def __init__(self, screen_w:int, screen_h:int, debug_level:int=0):
        super().__init__(screen_w, screen_h)
        self.debug_level = debug_level

    def __del__(self):
        # 削除完了通知
        print("XMLUI was deleted.")

    def draw(self):
        if self.DEBUGEVENT_PRINTTREE in self.xmlui.event.trg:
            print(self.xmlui.strtree())
        if self.DEBUGEVENT_RELOAD in self.xmlui.event.trg:
            print(self.xmlui.reload_templates())
        super().draw()
