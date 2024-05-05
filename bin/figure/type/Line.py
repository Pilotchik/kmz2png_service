
import zope

from bin.figure import Figure


class Line:
    zope.interface.implementer(Figure)

    def __init__(self, points):
        self.coordinates = points

    def getCoordinates(self):
        return self.coordinates

    def getExtreme(self):
        maxX = 0
        maxY = 0
        minX = self.coordinates[0][0]
        minY = self.coordinates[0][1]
        for point in self.coordinates:
            maxX = max(maxX, point[0])
            maxY = max(maxY, point[1])
            minX = min(minX, point[0])
            minY = min(minY, point[1])

        return [[minX, minY], [maxX, maxY]]

