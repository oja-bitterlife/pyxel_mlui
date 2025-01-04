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

        # デバッグで無いときはdrawだけでおしまい
        if not XMLUI.debug_enable:
            return

        # 以下デバッグ時
        # *********************************************************************
        if self.DEBUGEVENT_PRINTTREE in self.event.trg:
            get_logger().debug(self.strtree())

        # 開発用。テンプレートを読み込み直す
        if self.DEBUGEVENT_RELOAD in self.event.trg:
            for xml_filename in self._templates.keys():
                self.load_template(xml_filename)
            get_logger().debug("All XML Template was Reloaded")

    # 削除完了通知
    def __del__(self):
        get_logger().info("XMLUI was deleted.")
