class PlaceMark:
    def __init__(self, name):
        self.picHref = ""
        self.iconHref = ""
        self.name = name
        self.Figure = ""

    def setFigure(self, Figure):
        self.Figure = Figure

    def setIconHref(self, iconHref):
        self.iconHref = iconHref

    def setPicHref(self, picHref):
        self.picHref = picHref

    def getIconHref(self):
        return self.iconHref

    def getPicHref(self):
        return self.picHref

    def getName(self):
        return self.name

    def getFigure(self):
        return self.Figure


