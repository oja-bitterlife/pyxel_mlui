from xmlui.core import XMLUI

# デバッグ用
# *********************************************************************
class DebugXMLUI[T](XMLUI[T]):
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
            self.logger.debug(self.strtree())

        # 開発用。テンプレートを読み込み直す
        if self.DEBUGEVENT_RELOAD in self.event.trg:
            for xml_filename in self._templates.keys():
                self.load_template(xml_filename)
            self.logger.debug("All XML Template was Reloaded")
