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


def name():
    return "Zoom to Postcode in Czech Republic"


def description():
    return "Zoom the map extent to postcode in the Czech Republic"


def version():
    return "Version 0.0.1"


def icon():
    return "zoomicon.png"


def qgisMinimumVersion():
    return "2.0"

def author():
    return "Jan Ruzicka, Martin Konecny, Roman Siwek, Jana Kahankova, Lubos Csonka"

def email():
    return "jan.ruzicka.vsb@gmail.com"

def classFactory(iface):
    from zoomtopsc import ZoomToPSC
    return ZoomToPSC(iface)
