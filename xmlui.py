import xml.etree.ElementTree
from xml.etree.ElementTree import Element
from typing import Callable

class XMLUI():
    root: Element
    updateFuncs: dict[str, Callable[[dict[str,str], Element|None, Element], None]] = {}
    drawFuncs: dict[str, Callable[[dict[str,str], Element|None, Element], None]] = {}

    # ファイルから読み込み
    @classmethod
    def createFromFile(cls, fileName: str):
        with open(fileName, "r") as f:
            return cls.createFromString(f.read())

    # リソースから読み込み
    @classmethod
    def createFromString(cls, xml_data: str):
            return XMLUI(xml.etree.ElementTree.fromstring(xml_data))

    # 初期化。<xmlui>を持つXMLを突っ込む
    def __init__(self, dom: xml.etree.ElementTree.Element):
        # 最上位がxmluiでなくてもいい
        if dom.tag == "xmlui":
            self.root = dom
        else:
            # 最上位でないときは子から探す
            xmlui = dom.find("xmlui")
            if xmlui is None:
                raise Exception("<xmlui> not found")
            else:
                self.root = xmlui

        # 状態保存用
        for element in self.root.iter():
            element.makeelement("xmlui_state", {})


    # 全体を呼び出す処理
    def update(self):
        for element in self.root.iter():
            self.updateElement(element.tag, element.attrib, element.find("xmlui_state"), element)

    def draw(self):
        for element in self.root.iter():
            self.drawElement(element.tag, element.attrib, element.find("xmlui_state"), element)


    # 個別処理。関数のオーバーライドでもいいし、個別関数登録でもいい
    def updateElement(self, name: str, attr: dict[str,str], state: Element | None, element: Element):
        if name in self.updateFuncs:
            self.updateFuncs[name](attr, state, element)

    def drawElement(self, name: str, attr: dict[str,str], state: Element | None, element: Element):
        if name in self.drawFuncs:
            self.drawFuncs[name](attr, state, element)

    # 個別処理登録
    def setUpdateFunc(self, name: str, func: Callable[[dict[str,str], Element|None, Element], None]):
        self.updateFuncs[name] = func

    def setDrawFunc(self, name: str, func: Callable[[dict[str,str], Element|None, Element], None]):
        self.drawFuncs[name] = func
