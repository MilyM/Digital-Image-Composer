# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ComposerDockWidget
                                 A QGIS plugin
 Creating color compositions from raster spatial data 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-12-19
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Milosz Cygan
        email                : miloszcygan99@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QGridLayout, QWidget, QComboBox, QLabel, QHBoxLayout
from .settings_dialog import Settings_Dialog
from .tools import open_ccfg, create_composition, create_composition_none, read_fastmode
from osgeo import gdal
from qgis.core import QgsRasterLayer, QgsProject

DRIVER = 'GTiff'
OUT_EXT = 'tif'
EMPTY = 'empty'

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'di_composer_dockwidget_base.ui'))


class ComposerDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    data_path = None
    output_path = None
    conffile_path = None
    band_extension = 'TIF'
    bands_names = None
    output_name = None
    history_path = None
    fast_mode = None
    bands_number = 3
    history = {}
    pixel_types = {
                'Byte': gdal.GDT_Byte,
                'CFloat32': gdal.GDT_CFloat32,
                'CFloat64': gdal.GDT_CFloat64, 
                'CInt16': gdal.GDT_CInt16, 
                'CInt32': gdal.GDT_CInt32,
                'Float32': gdal.GDT_Float32,
                'Float64': gdal.GDT_Float64,
                'Int16': gdal.GDT_Int16,
                'Int32': gdal.GDT_Int32,
                'UInt16': gdal.GDT_UInt16,
                'UInt32': gdal.GDT_UInt32
                }
    
    def __init__(self, parent=None):
        super(ComposerDockWidget, self).__init__(parent)
        self.setupUi(self)
        pixel_types = self.pixel_types.keys()
        self.cb_pixel.addItems(pixel_types)
        self.cb_pixel.setCurrentText('UInt16')
        self.cb_fast.blockSignals(True)
        self.fast_mode = read_fastmode('fast_mode.txt')
        fast_mode_names = self.fast_mode.keys()
        self.cb_fast.addItems(fast_mode_names)
        self.cb_fast.addItem('None')
        self.cb_fast.setCurrentText('None')
        self.cb_fast.blockSignals(False)
        self.tabWidget.setTabEnabled(0, False)


    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

# ustawienie sciezki do danych 
    @pyqtSlot()
    def on_pb_data_clicked(self):

        path = QFileDialog.getExistingDirectory()

        if path != None:
            self.le_data.setText(path)
            self.data_path = path

    def on_le_data_editingFinished(self):
        self.data_path = self.le_data.text()

# ustawienie sciezki do folderu roboczego
    @pyqtSlot()
    def on_pb_output_clicked(self):
        path = QFileDialog.getExistingDirectory()
        if path != None:
            self.le_output.setText(path)
            self.output_path = path

    def on_le_output_editingFinished(self):
        self.output_path = self.le_output.text()

# ustawienie rozszerzenia
    def on_le_ext_editingFinished(self):
        self.band_extension = self.le_ext.text()

# otwieranie edytora do tworzenie skrótów nazw bandów + ostrzezenie
    def display_nopath_warning(self):
        QMessageBox.warning(self, 'Warning!',  'No paths provided')


    @pyqtSlot()
    def on_pb_create_clicked(self):
        if self.data_path == None or self.output_path == None:
            self.display_nopath_warning()
        else:
            self.settings_dialog = Settings_Dialog(data_path=self.data_path, output_path=self.output_path, bands_extension=self.band_extension)
            self.settings_dialog.show()

# otwieranie nia ccfg
    def display_nopath_warning(self):
        QMessageBox.warning(self, 'Warning!',  'Cannot open configuration file')
    
    def display_opened_info(self):
         QMessageBox.information(self, 'Info',  'Configuration file opened, shortcuts created!')

        
    @pyqtSlot()
    def on_pb_open_clicked(self):
   
        self.conffile_path, _ = QFileDialog.getOpenFileName()
        
        try:
            self.data_path, self.output_path, self.bands_names = open_ccfg(self.conffile_path)
        except:
            self.tabWidget.setTabEnabled(0, False)
            self.display_nopath_warning()
        else:
            self.shorcuts = self.bands_names.keys()

            self.le_data.setText(self.data_path)
            self.le_output.setText(self.output_path)

            self.cb_list = []

            self.scrollAreaWidgetContents = QWidget()
            self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
            self.sa_creator.setWidget(self.scrollAreaWidgetContents)

            label_name = 1

            if self.bands_number % 3 == 0:
                rows = self.bands_number // 3
            else:
                rows = self.bands_number // 3 + 1
            
            check_number = 0
            for row in range(rows):
                for j in range(3):
                    if check_number == self.bands_number:
                        break
                    else:
                        self.layout = QHBoxLayout()
                        label = QLabel(f'{label_name}')
                        cb = QComboBox()
                        cb.addItems(self.shorcuts)
                        cb.addItem(EMPTY)
                        self.cb_list.append(cb)
                        self.layout.addWidget(label, 0)
                        self.layout.addWidget(cb, 1)
                        self.gridLayout.addLayout(self.layout, row, j)
                        label_name += 1
                        check_number += 1
            self.tabWidget.setTabEnabled(0, True)
            self.display_opened_info()
            self.gb_ccfg.setTitle('Configuration file - SET')



    def on_sb_bands_valueChanged(self, value):
        self.bands_number = value


    def on_le_tifname_textChanged(self):
        self.output_name = self.le_tifname.text()

    def display_noname_warning(self):
        QMessageBox.warning(self, 'Warning!',  'Cannot create tiff')

    @pyqtSlot()
    def on_pb_composition_clicked(self):

        pixel_type = self.pixel_types[self.cb_pixel.currentText()]
        names = [cb.currentText() for cb in self.cb_list]

        if EMPTY in names:
            bands = []
            for cb in self.cb_list:
                if cb.currentText() == EMPTY:
                    bands.append(None)
                else:
                    bands.append(self.bands_names[cb.currentText()])
            try:
                output_tif_path = create_composition_none(bands, names, self.data_path, self.output_path, self.output_name, OUT_EXT, DRIVER, pixel_type)
                qgs_layer = QgsRasterLayer(output_tif_path, self.output_name)
                QgsProject.instance().addMapLayer(qgs_layer)
            except:
                self.display_noname_warning()
        else:
            bands = [self.bands_names[cb.currentText()] for cb in self.cb_list]
            try:
                output_tif_path = create_composition(bands, names, self.data_path, self.output_path, self.output_name, OUT_EXT, DRIVER, pixel_type)
                qgs_layer = QgsRasterLayer(output_tif_path, self.output_name)
                QgsProject.instance().addMapLayer(qgs_layer)
            except:
                self.display_noname_warning()
                  

    def display_noband_warning(self):
        QMessageBox.warning(self, 'Warning!',  "Band doesn't exist!")


    def on_cb_fast_currentIndexChanged(self):
        text = self.cb_fast.currentText()
        if text != 'None':
            to_use = self.fast_mode[text]
            filename = to_use[0]
            print(filename)
            exist_bands = self.bands_names
            bands = [to_use[1], to_use[2], to_use[3]]
            try:
                for i in range(3):
                    self.cb_list[i].setCurrentText(bands[i])
                    self.le_tifname.setText(filename)
            except:
                self.display_noband_warning()
                
        else:
            for i in range(3):
                    self.cb_list[i].setCurrentText(EMPTY)
       
            






   


