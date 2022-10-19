# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from owslib.wms import WebMapService

#url ='http://wms.jpl.nasa.gov/wms.cgi'
url = 'http://localhost:8080/geoserver/wms'

wms = WebMapService(url, version='1.1.1')
print(wms.contents)
print(wms['catiz:gis_osm_places_a_free_1'].boundingBox)

img = wms.getmap( layers=['catiz:gis_osm_places_a_free_1'],
                  srs="EPSG:4326",
                  bbox=(-7.6878667, 61.3895367, -6.2561547, 62.3942991),
                  size=(300, 250),
                  format='image/jpeg',
                  transparent=True)
with open('jpl_mosaic_visb.jpg', 'wb') as out:
    out.write(img.read())