import os
import sys

import cairosvg
import shutil
import json
import time

from zipfile import ZipFile
from bin.func import *
from PIL import Image, ImageDraw, ImageFont

# python3 main.py kmz_file/context_3115_2024_04_24_07_47.kmz output.png 37.6089332 48.1920883 37.9091832 48.1009183 1000 700

input_file = sys.argv[1]
output_file = sys.argv[2]

lonLU = float(sys.argv[3])
latLU = float(sys.argv[4])

lonRD = float(sys.argv[5])
latRD = float(sys.argv[6])

width = int(sys.argv[7])
height = int(sys.argv[8])


with open('config.json', "r") as f:
    config = json.load(f)

lonLatLeftUp = [lonLU, latLU]
lonLatRightDown = [lonRD, latRD]

deltaLon = abs(lonLatLeftUp[0] - lonLatRightDown[0])
deltaLat = abs(lonLatLeftUp[1] - lonLatRightDown[1])

width = 10000
height = 10000

img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

t = time.time()

kmz = ZipFile(input_file, 'r')
kmz.extractall()

data = parseXml("doc.kml")


L = getDistance(lonLU, lonRD, latLU, latLU)  # ширина рассматриваемово кадра в метрах
H = getDistance(lonLU, latLU, lonLU, latRD)  # высота рассматриваемого кадра в метрах

K = config["icon"]["att"]  # минимальное отношение ширины объекта к шиирине кадра

alpha = math.ceil(width / 5000)  # коэфицциент для ширины всяких линий (пока сделал такможно улучшить)

center_flag = False  # флаг отвечающий за привязку callout-а к центру объекта
circle_flag = config["circle"]  # флаг отвечающий за нанесение кружочка и соответственного форматирования callout-a

dones_coord = []  # координаты на которых находится какой-то из нанесённых объектов
infoLocPic = []  # координаты нанесённых объектов (сделано для callout-ов, чтолбы они не накладывались на объекты)

print("Нанесение разметок на изображение: ")
procent = 0
for pm in data:
    procent += 1
    # реальные размеры объекта в метрах
    extremeCoords = pm.getFigure().getExtreme()  # вытаскиваем максимальные и минимальные координаты фигуры
    lonC = (extremeCoords[0][0] + extremeCoords[1][0]) / 2  # Получаем координаты центра
    latC = (extremeCoords[0][1] + extremeCoords[1][1]) / 2  # Получаем координаты центра
    coordPM = getCoordsOnPicture(pm.getFigure().getCoordinates(), lonLatLeftUp, lonLatRightDown)
    if coordPM != [] and not (pm.getFigure().getCoordinates() in dones_coord):
        lon = abs(lonC - lonLatLeftUp[0])
        lat = abs(latC - lonLatLeftUp[1])
        x = int(lon * width / deltaLon)
        y = int(lat * height / deltaLat)

        # если какой-то из размеров получился 0 то запишим константные значения

        if config["lines"] and len(coordPM) > 1:
            for i in range(len(coordPM) - 1):
                draw.line((
                    int(abs(coordPM[i][0] - lonLatLeftUp[0]) * width / deltaLon),
                    int(abs(coordPM[i][1] - lonLatLeftUp[1]) * height / deltaLat),
                    int(abs(coordPM[i + 1][0] - lonLatLeftUp[0]) * width / deltaLon),
                    int(abs(coordPM[i + 1][1] - lonLatLeftUp[1]) * height / deltaLat)
                ), fill=config["lines"]["color"], width=int(1 * alpha))
                infoLocPic.append({
                    "x1": int(abs(coordPM[i][0] - lonLatLeftUp[0]) * width / deltaLon),
                    "y1": int(abs(coordPM[i][1] - lonLatLeftUp[1]) * height / deltaLat),
                    "x2": int(abs(coordPM[i + 1][0] - lonLatLeftUp[0]) * width / deltaLon),
                    "y2": int(abs(coordPM[i + 1][1] - lonLatLeftUp[1]) * height / deltaLat)
                })

        if config["icon"] and pm.getIconHref() != "":
            center_flag = True
            if pm.getIconHref().endswith('.svg'):
                cairosvg.svg2png(url=pm.getIconHref(), write_to="tmp/output.png")
                with Image.open("tmp/output.png") as image_icon:
                    image_icon.load()
            elif pm.getIconHref().endswith('.png'):
                with Image.open(pm.getIconHref()) as image_icon:
                    image_icon.load()

            alphaI = width * config["icon"]["att"] / image_icon.width  # коэфициет на который надо умножать картинку
            cx = int(x - alphaI * image_icon.width / 2)
            cy = int(y - alphaI * image_icon.height / 2)

            img.paste(
                image_icon.resize((int(image_icon.width * alphaI), int(image_icon.height * alphaI))),
                (cx, cy),
                image_icon.convert('RGBA').resize((int(image_icon.width * alphaI), int(image_icon.height * alphaI)))
            )
            infoLocPic.append({
                "x1": cx,
                "y1": cy,
                "x2": cx + image_icon.width * alphaI,
                "y2": cy + image_icon.height * alphaI
            })

        if circle_flag and len(coordPM) < 2:
            R = config["circle"]["att"] * width
            cx = int(x - R)
            cy = int(y - R)
            draw.arc(
                xy=(cx, cy, cx + 2 * R, cy + 2 * R),
                start=0, end=360,
                fill=config["circle"]["color"], width=alpha
            )
            infoLocPic.append({
                "x1": cx,
                "y1": cy,
                "x2": cx + 2 * R,
                "y2": cy + 2 * R
            })
        if config["points"] and len(coordPM) < 2:
            center_flag = True
            draw.ellipse(
                (x - 2 * alpha, y - 2 * alpha, x + 2 * alpha, y + 2 * alpha),
                fill=config["points"]["color"]
            )
            infoLocPic.append({
                "x1": x - 2 * alpha,
                "y1": y - 2 * alpha,
                "x2": x + 2 * alpha,
                "y2": y + 2 * alpha
            })

        dones_coord.append(pm.getFigure().getCoordinates())
        print(str(procent / len(data) * 100) + " %")


print("Нанесение выносок на изображение: ")
procent = 0
if config["callouts"]:
    dones_coord = []
    anchor_text_center = False
    if config["callouts"]["anchor_text_center"]:
        anchor_text_center = True

    margin = 5  # отступы
    scale = 5  # увеличение размеров выноски
    text_scale = config["callouts"]["text_scale"]
    font = ImageFont.truetype("arialmt.ttf", size=int(alpha * text_scale))

    picWidth = 0 
    picHeight = 0 

    betta = 0  # resize коэфициент изображения на выноске

    for pm in data:
        sign = 1
        procent += 1
        coordPM = getCoordsOnPicture(pm.getFigure().getCoordinates(), lonLatLeftUp, lonLatRightDown)
        if coordPM != [] and not (pm.getFigure().getCoordinates() in dones_coord):

            extremeCoords = pm.getFigure().getExtreme()

            lonC = (extremeCoords[0][0] + extremeCoords[1][0]) / 2
            latC = (extremeCoords[0][1] + extremeCoords[1][1]) / 2

            coeff_callout_line = 0
            R = 0

            if len(coordPM) > 1:
                cords = "Координаты центра масс: " + str(lonC) + "/" + str(latC)
            else:
                cords = str(lonC) + " / " + str(latC)

            lon = abs(lonC - lonLatLeftUp[0])
            lat = abs(latC - lonLatLeftUp[1])

            if len(coordPM) < 2:
                R = K * width
            else:
                R = 0
                coeff_callout_line = alpha * 100
                if not (anchor_text_center):
                    lon = abs(coordPM[int(len(coordPM) / 2)][0] - lonLatLeftUp[0])
                    lat = abs(coordPM[int(len(coordPM) / 2)][1] - lonLatLeftUp[1])

            x = int(lon * width / deltaLon)
            y = int(lat * height / deltaLat)

            if config["callouts"]["pic"] and pm.getPicHref() != "":
                pic_size = config["callouts"]["pic"]["pic_size"]
                with Image.open(pm.getPicHref()) as image_pic:
                    image_pic.load()
                picWidth = image_pic.width
                picHeight = image_pic.height
                betta = text_scale * pic_size * width / image_pic.width

            c = 1  # вспомогательный коэффициент для позиционирования текста в сноске
            sign = 1  # вспомогателььный коэффициет для позиционирования сноски (лево, право)
            nyS = y
            nyE = y

            k = 0.5 / text_scale
            iterator = 0

            flag_sign = True
            while True:
                flag = 1
                if flag_sign:
                    iterator += 1

                nxE = x - sign * R * scale - coeff_callout_line * sign
                maxX = max(nxE, int(nxE - sign * picWidth * betta - sign * margin))
                maxX = max(maxX, int(nxE - sign * font.getsize(pm.getName())[0] - sign * margin))
                maxX = max(maxX, int(nxE - sign * font.getsize(cords)[0] - sign * margin))

                minX = min(nxE, int(nxE - sign * picWidth * betta - sign * margin))
                minX = min(minX, int(nxE - sign * font.getsize(cords)[0] - sign * margin))
                minX = min(minX, int(nxE - sign * font.getsize(pm.getName())[0] - sign * margin))
                for i in infoLocPic:
                    if ((i["x1"] - alpha / k < maxX < i["x2"] + alpha / k and
                         i["y1"] - alpha / k < nyE < i["y2"] + alpha / k) or
                            (i["x1"] - alpha / k < minX < i["x2"] + alpha / k and
                             i["y1"] - alpha / k < nyE < i["y2"] + alpha / k) or
                            (i["x1"] - alpha / k < maxX < i["x2"] + alpha / k and
                             i["y1"] - alpha / k < nyE - alpha * scale - betta * picHeight - alpha / k < i[
                                 "y2"] + alpha / k) or
                            (i["x1"] - alpha / k < minX < i["x2"] + alpha / k and
                             i["y1"] - alpha / k < nyE - alpha * scale - betta * picHeight - alpha / k < i[
                                 "y2"] + alpha / k)
                            or
                            (minX - alpha / k < i["x1"] < maxX + alpha / k and
                             nyE - alpha * scale - betta * picHeight - margin - alpha / k < i[
                                 "y1"] < nyE + alpha / k) or
                            (minX - alpha / k < i["x1"] < maxX + alpha / k and
                             nyE - alpha * scale - betta * picHeight - margin - alpha / k < i[
                                 "y2"] < nyE + alpha / k) or
                            (minX - alpha / k < i["x2"] < maxX + alpha / k and
                             nyE - alpha * scale - betta * picHeight - margin - alpha / k < i[
                                 "y1"] < nyE + alpha / k) or
                            (minX - alpha / k < i["x2"] < maxX + alpha / k and
                             nyE - alpha * scale - betta * picHeight - margin - alpha / k < i["y2"] < nyE + alpha / k)
                            or minX < 0 or maxX > width):
                        if flag_sign:
                            sign = sign * -1
                            flag_sign = not flag_sign
                            c = not (c ^ 0)

                            flag = 0
                            break
                        nyE += (-1) ** (iterator + 1) * (2 * iterator - 1)
                        flag_sign = not flag_sign
                        flag = 0
                        break
                if flag == 1: break

            nxS = x - sign * R

            if center_flag and not circle_flag:
                nxS = x
            draw.line((
                nxS,
                nyS,
                nxE,
                nyE
            ), fill=config["callouts"]["color"], width=alpha)
            draw.line((
                nxE,
                int(nyE + alpha * text_scale),
                nxE,
                int(nyE - alpha * text_scale - betta * picHeight)
            ), fill=config["callouts"]["color"], width=alpha)

            draw.text((
                int(nxE - c * font.getsize(pm.getName())[0] - sign * margin),
                nyE - alpha * text_scale
            ), pm.getName(), fill=config["callouts"]["color"], font=font, align="right")

            draw.text((
                int(nxE - c * font.getsize(cords)[0] - sign * margin),
                nyE
            ), cords, fill=config["callouts"]["color"], font=font, align="right")
            if config["callouts"]["pic"] and pm.getPicHref() != "":
                img.paste(
                    image_pic.resize((int(picWidth * betta), int(picHeight * betta))),
                    (int(nxE - c * picWidth * betta - sign * margin),
                     int(nyE - alpha * text_scale - picHeight * betta - margin * 2)),
                )
            infoLocPic.append({
                "x1": minX,
                "y1": int(nyE - alpha * scale - picHeight * betta),
                "x2": maxX,
                "y2": int(nyE + alpha * scale)
            })
            dones_coord.append(pm.getFigure().getCoordinates())
        print(str(procent / len(data) * 100) + " %")
img.show()
img.save(output_file)
if os.path.isdir('files'):
    shutil.rmtree('files')
os.remove("doc.kml")
print("time: " + str(time.time() - t) + " секунд.")
