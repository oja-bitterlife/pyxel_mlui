import logging
logging.basicConfig()

from xmlui.core import XMLUI

def get_logger() -> logging.Logger:
    logger = logging.getLogger("XMLUI")
    if XMLUI.debug_enable:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    return logger

# デバッグ用
class DebugXMLUI(XMLUI):
    DEBUGEVENT_PRINTTREE = "DEBUG_PRINTTREE"
    DEBUGEVENT_RELOAD = "DEBUG_RELOAD"

    def draw(self):
        super().draw()
        if not XMLUI.debug_enable:
            return

        # デバッグ
        if self.DEBUGEVENT_PRINTTREE in self.xmlui.event.trg:
            get_logger().debug(self.xmlui.strtree())
        if self.DEBUGEVENT_RELOAD in self.xmlui.event.trg:
            self.xmlui.reload_templates()

    def __del__(self):
        # 削除完了通知
        get_logger().info("XMLUI was deleted.")
