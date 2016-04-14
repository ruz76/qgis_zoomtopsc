# -*- coding: utf-8 -*-
"""
/***************************************************************************
    ZoomToPSC
                                                     A QGIS plugin
 Zoom the map extent to postcode in the Czech Republic
 This plugin was developed by students of VSB-TUO (http://gis.vsb.cz/)
 as a part of subject Programming II under supervision of Jan Ruzicka.
 The location of postcodes is based on RUIAN and FreeGeodataCZ data.
                             -------------------
        begin                : 2016-02-25
        copyright            : (C) 2016 by Jan Ruzicka, Martin Konecny, Roman Siwek, Jana Kahankova, Lubos Csonka
        email                : jan.ruzicka.vsb@gmail.com, martin.konecny@vsb.cz

 ***************************************************************************/

/***************************************************************************

*   This plugin is based on ZoomToPostcode written by Matthew Walsh. You      *
*   can redistribute it and/or modify it under the terms of the GNU General *
*   Public License as published by the Free Software Foundation; either     *
*   version 2 of the License, or (at your option) any later version         *

***************************************************************************/

/***************************************************************************

 ZoomToPostcode
                                 A QGIS plugin
 Zoom the map extent to any UK postcode
                             -------------------
        begin                : 2013-06-16
        copyright            : (C) 2015 by Matthew Walsh
        email                : walsh.gis@gmail.com

***************************************************************************/
"""

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import os.path

class ZoomToPSC:

    def __init__(self, iface):
        # Save reference to the QGIS interface + canvas
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'zoomtopsc_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create various class references
        self.marker = None
        self.completer = None
        self.previous_searches = []

    def initGui(self):
        # Create toolbar
        self.toolbar = self.iface.addToolBar("Zoom To PSC Toolbar")
        self.toolbar.setObjectName("Zoom To PSC Toolbar")
        self.toolbar_search = QLineEdit()
        self.toolbar_search.setMaximumWidth(100)
        self.toolbar_search.setAlignment(Qt.AlignLeft)
        self.toolbar_search.setPlaceholderText(u"Zadejte PSČ...")
        self.toolbar.addWidget(self.toolbar_search)
        self.toolbar_search.returnPressed.connect(self.search)
        self.search_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "zoomicon.png")), "Search",  self.iface.mainWindow())
        QObject.connect(self.search_btn, SIGNAL("triggered()"), self.search)
        self.addlayer_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "addlayericon.png")), "Add Layer",  self.iface.mainWindow())
        QObject.connect(self.addlayer_btn, SIGNAL("triggered()"), self.addlayer)
        self.toolbar.addActions([self.search_btn, self.addlayer_btn])

        # Create action that will start plugin configuration
        self.action = QAction(QIcon(os.path.join(os.path.dirname(__file__), "zoomicon.png")), u"Zoom to PSC", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.toolbar.show)

        # Add toolbar button and menu item
        self.iface.addPluginToMenu(u"&Zoom to Postcode", self.action)

    def addlayer(self):
        layer = QgsVectorLayer(os.path.join(os.path.dirname(__file__), "data/cr_psc_centroids.shp"), "psc", "ogr")
        if not layer.isValid():
            print "Layer failed to load!"
        else:
            QgsMapLayerRegistry.instance().addMapLayer(layer)

    def unload(self):
        # Remove the plugin menu item and toolbar
        self.iface.removePluginMenu(u"&Zoom to Postcode", self.action)
        del self.toolbar

    def search_completer(self):
        self.completer = QCompleter(self.previous_searches, self.iface.mainWindow())
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

    def check_crs(self):
        # Check if a transformation needs to take place
        map_renderer = self.canvas.mapRenderer()
        srs = map_renderer.destinationCrs()
        current_crs = srs.authid()
        return current_crs

    def transform(self, cor):
        # Transforms point from british nation grid to map crs
        map_renderer = self.canvas.mapRenderer()
        srs = map_renderer.destinationCrs()
        crs_src = QgsCoordinateReferenceSystem(5514)
        crs_dest = QgsCoordinateReferenceSystem(srs)
        xform = QgsCoordinateTransform(crs_src, crs_dest)
        x = int(cor[0])
        y = int(cor[1])
        t_point = xform.transform(QgsPoint(x, y))
        return t_point

    def search(self):
        # Create dictionary of postcodes from correct Pickle file
        try:
            input_pcode = self.toolbar_search.text().replace(' ', '')
            if input_pcode.upper() not in self.previous_searches:
                self.previous_searches.append(input_pcode.upper())
                self.search_completer()
                self.toolbar_search.setCompleter(self.completer)
            file = open(os.path.join(os.path.dirname(__file__), "data/cr_psc_centroids.csv"), 'r')
            x = -1
            for line in file:
                items = line.split(";")
                if items[0] == input_pcode:
                    x = items[1]
                    y = items[2]
                    break
            if x == -1:
                QMessageBox.information(self.iface.mainWindow(), u"Chybné PSČ", u"PSČ nebylo nalezeno")
            else:
                self.zoomto(x, y)
        except (KeyError, IOError):
            QMessageBox.information(self.iface.mainWindow(), u"Chybné PSČ", u"PSČ nebylo nalezeno")
        except IndexError:
            pass

    def zoomto(self, x, y):
        # Find the coordinates for postcode in the dictionary
        current_crs = self.check_crs()
        #print current_crs
        if current_crs != "EPSG:5514":
            cor = (x, y)
            point = self.transform(cor)
            #print """TT: """ + str(point)
            self.update_canvas(point)
        else:
            point = (x, y)
            #print """OO: """ + str(point)
            self.update_canvas(point)

    def update_canvas(self, point):
        # Update the canvas and add vertex marker
        x = point[0]
        y = point[1]
        #TODO change scale according to srid
        #This condition is just quick hack for some srids with deegrees and meters
        if y > 100:
            scale = 60000
        else:
            scale = 1
        rect = QgsRectangle(float(x)-scale, float(y)-scale, float(x)+scale, float(y)+scale)
        self.canvas.setExtent(rect)
        self.backgroundmarker = QgsVertexMarker(self.canvas)
        self.backgroundmarker.setIconSize(15)
        self.backgroundmarker.setPenWidth(4)
        self.backgroundmarker.setColor(QColor(255, 255, 255, 255))
        self.backgroundmarker.setCenter(QgsPoint(int(x), int(y)))
        self.marker = QgsVertexMarker(self.canvas)
        self.marker.setIconSize(15)
        self.marker.setPenWidth(2)
        self.marker.setCenter(QgsPoint(int(x), int(y)))
        self.canvas.refresh()
        #self.canvas.extentsChanged.connect(self.remove_marker)

    def remove_marker(self):
        # Remove vertex marker
        self.marker.hide()
        self.canvas.scene().removeItem(self.marker)
        self.canvas.extentsChanged.disconnect(self.remove_marker)
