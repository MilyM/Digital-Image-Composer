from qgis.PyQt import QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QHeaderView, QMessageBox
import os
from .tools import find_bands, create_ccfg


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings_dialog.ui'))

class Settings_Dialog(QtWidgets.QDialog, FORM_CLASS):

    filename = 'bands'

    def __init__(self, data_path, output_path, bands_extension, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.output_path = output_path
        self.data_path = data_path
        bands_list = find_bands(data_path, bands_extension, True)
        bands_list.sort()
        self.bands_size = len(bands_list)

        header = self.table_bands.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.table_bands.setRowCount(self.bands_size)


        for i in range(self.bands_size):
                item = QTableWidgetItem(bands_list[i])
                self.table_bands.setItem(i, 0, item)
                
                # item1 = QTableWidgetItem("zzz")
                # self.table_bands.setItem(i, 1, item1)

                
                
        header = self.table_bands.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)


    def on_le_filename_editingFinished(self):
         self.filename = self.le_filename.text()

    def display_created_info(self):
         QMessageBox.information(self, 'Info',  'Configuration file created!')
         
    def on_button_box_accepted(self):
        bands = {}

        for i in range(self.bands_size):
            if self.table_bands.item(i, 1) == None:
                 continue
            value = self.table_bands.item(i, 0).text()
            key = self.table_bands.item(i, 1).text()
            bands[key] = value
            print(bands)
            print(self.output_path)
        
        create_ccfg(bands, self.filename, self.data_path, self.output_path)
        self.display_created_info()
        
                  



             
             
             