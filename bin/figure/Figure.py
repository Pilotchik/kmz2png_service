import zope.interface


class Figure(zope.interface.Interface):

    def getExtremes(self):
        """get Extremes of the figure"""

    def getCoordinates(self):
        """get Coordinates of the figure"""
