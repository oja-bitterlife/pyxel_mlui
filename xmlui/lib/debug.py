from xmlui.core import XMLUI
import logging
logging.basicConfig()

# デバッグ用
class DebugXMLUI(XMLUI):
    DEBUGEVENT_PRINTTREE = "DEBUG_PRINTTREE"
    DEBUGEVENT_RELOAD = "DEBUG_RELOAD"

    def __init__(self, screen_w:int, screen_h:int, log_level:int=logging.DEBUG):
        super().__init__(screen_w, screen_h)
        self.log_level = log_level

        self.log = logging.getLogger(__name__)
        self.log.setLevel(self.log_level)

        # デバッグレベルが0の時は出力ナシで
        if self.log_level == 0:
            self.log.disabled = True

    def __del__(self):
        # 削除完了通知
        self.debug("XMLUI was deleted.")

    def draw(self):
        if self.DEBUGEVENT_PRINTTREE in self.xmlui.event.trg:
            self.debug(self.xmlui.strtree())
        if self.DEBUGEVENT_RELOAD in self.xmlui.event.trg:
            self.xmlui.reload_templates()
        super().draw()

    # ロギング
    def debug(self, msg:str, *args, **kwargs):
        self.log.debug(msg, *args, **kwargs)

    def info(self, msg:str, *args, **kwargs):
        self.log.info(msg, *args, **kwargs)

    def warning(self, msg:str, *args, **kwargs):
        self.log.warning(msg, *args, **kwargs)

    def error(self, msg:str, *args, **kwargs):
        self.log.error(msg, *args, **kwargs)

    def critical(self, msg:str, *args, **kwargs):
        self.log.critical(msg, *args, **kwargs)
