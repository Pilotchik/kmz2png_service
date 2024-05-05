# README

## Описание

Этот репозиторий содержит исходный код сервиса написанного на Python для растаризации kmz файлов.

## Требования

Для запуска сервиса необходимы следующие библиотеки и зависимости:

* Python 3.x
* __Pillow:__ для работы с изображениями
* __cairosvg:__ для растариизации иконок
* __shutil:__ для рекурсивного удаления дирректорий
* __zipfile:__ для распоковки kmz файлов
* __json:__ для работы с конфигуратором
* __time:__ для оценки время работы
* __os:__ для рабооты с файлами
* __pykml:__ для парсинга kml
* __re:__ для разбора информации из kml
* __zope:__ для элементов ооп
* __math:__ для математических операций

## Установка

1. Клонируйте репозиторий:

```
git clone https://github.com/dfa-ra/kmz2png.git
```

2. Установите зависимости:

Установите зависимости выше с помощью:```pip install```

3. Запустите сервис:

```
python3 main.py your_file.kmz output.png lonLU latLU lonRD latRD width height
```
* main.py - основная программа сервиса
* your_file.kmz - растаризуемый файл kmz
* lonLU, latLU, lonRD, latRD - координаты растаризуемого участка (левый верхний и правый нижний угол) 
* width, height - ширина и высота получаемой картинки в пикселях

пример запуска файла
```
python3 main.py foto.kmz output.png 37.7089332 48.1920883 37.8091832 48.1009183 1000 700
```

## Результат работы

После запуска сервиса в консоле будет показываться процент выполнения 
работы и стадии выполнения. После завершения работы в консоле будет 
написано время выполнения программы и по адресу указанному при запуске создасться файл
с получившимся изображением

## Настройки файла конигуратор

Файл config.json это файл отвичающий за настроки выходного файла. В нём можно добавить или убрать
различные фигуры, изменить их размер или цвет. Если вы не хотите чтобы какая-то из опций присутствовала
посттавьте false как её значение. 

### Взаимо исключения конфигуратора 

1) Если отдельный объект представляет из себя больше чем одну координату, то вокруг него
нельзя нарисовать кружочек. Объект будет рисоваться исключительно линиями.
2) Если у объекта в kmz файле нет иконки, то "очевидно" никакая иконка у него не нарисуется
3) Если у объекта нет имени то в выноске он будет подписан как "Без имени"
4) Если объект обведён в круг то выноска будет привязываться не к середине объекта а к 
окружности описанного круга
5) Точку на координаты объекта можно поставить только если этот объект состоит из одной точки координат
6) Выноска к объекту состоящиму более чем из одной точки координат будет привязываться
к центру описанного прямоугольника если такой параметри будет стоять в файле
configurator иначе к любой точке координат принадлежащей этому объекту 