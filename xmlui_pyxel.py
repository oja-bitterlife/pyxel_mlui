import pyxel
import xml.etree.ElementTree
from xml.etree.ElementTree import Element


class XMLUI_PYXEL():
    root: Element

    @classmethod
    def createFromFile(cls, fileName: str):
        with open(fileName, "r") as f:
            data = f.read()
            return XMLUI_PYXEL(xml.etree.ElementTree.fromstring(data))

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

    def update(self):
        self.root.iter
        pass

    def draw(self):
        pass


class UIElement(Element):
    def __init__(self, element: xml.etree.ElementTree.Element):
        self.element = element
        print(element)

    def updateElement(self):
        pass

    def drawElement(self):
        pass

