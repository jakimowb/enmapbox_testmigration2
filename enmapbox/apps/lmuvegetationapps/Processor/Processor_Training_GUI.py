# -*- coding: utf-8 -*-

import sys
#ensure to call QGIS before PyQtGraph
from qgis.PyQt.QtWidgets import *
import lmuvegetationapps.Processor.Processor_Inversion_core as processor
from lmuvegetationapps import APP_DIR
from hubflow.core import *

pathUI_train = os.path.join(APP_DIR, 'Resources/UserInterfaces/Processor_Train.ui')
pathUI_wavelength = os.path.join(APP_DIR, 'Resources/UserInterfaces/Select_Wavelengths.ui')
pathUI_prgbar = os.path.join(APP_DIR, 'Resources/UserInterfaces/ProgressBar.ui')

from enmapbox.gui.utils import loadUi

class ANN_Training_GUI(QDialog):
    
    def __init__(self, parent=None):
        super(ANN_Training_GUI, self).__init__(parent)
        loadUi(pathUI_train, self)


class Select_Wavelengths_GUI(QDialog):

    def __init__(self, parent=None):
        super(Select_Wavelengths_GUI, self).__init__(parent)
        loadUi(pathUI_wavelength, self)


class PRG_GUI(QDialog):
    def __init__(self, parent=None):
        super(PRG_GUI, self).__init__(parent)
        loadUi(pathUI_prgbar, self)
        self.allow_cancel = False

    def closeEvent(self, event):
        if self.allow_cancel:
            event.accept()
        else:
            event.ignore()


class ANN_Training:
    def __init__(self, main):
        self.main = main
        self.gui = ANN_Training_GUI()
        self.initial_values()
        self.connections()

    def initial_values(self):
        self.exclude_wavelengths = [[1359, 1480], [1721, 2001]]  # from ... to
        self.LUT_path = None
        self.meta_dict = None
        self.wunit = "nanometers"
        self.wl, self.nbands, self.nbands_valid = (None, None, None)
        self.out_dir = None
        self.model_name = None

    def connections(self):
        self.gui.cmdInputLUT.clicked.connect(lambda: self.open_lut())
        self.gui.cmdModelDir.clicked.connect(lambda: self.get_folder())
        self.gui.cmdRun.clicked.connect(lambda: self.run_training())
        self.gui.cmdClose.clicked.connect(lambda: self.gui.close())

        self.gui.cmdExcludeBands.clicked.connect(lambda: self.open_wavelength_selection())
        self.gui.cmbPCA.toggled.connect(lambda: self.handle_PCA())

    def open_lut(self):
        result = str(QFileDialog.getOpenFileName(caption='Select LUT meta-file', filter="LUT-file (*.lut)")[0])
        if not result:
            return
        self.LUT_path = result
        self.gui.lblInputLUT.setText(result)

        with open(self.LUT_path, 'r') as meta_file:
            content = meta_file.readlines()
            content = [item.rstrip("\n") for item in content]
        keys, values = list(), list()
        [[x.append(y) for x, y in zip([keys, values], line.split(sep="=", maxsplit=1))] for line in content]
        values = [value.split(';') if ';' in value else value for value in values]
        self.meta_dict = dict(zip(keys, values))

        self.wl = np.asarray(self.meta_dict['wavelengths']).astype(np.float16)
        self.nbands = len(self.wl)
        self.exclude_bands = [i for i in range(len(self.wl)) if self.wl[i] < 400 or self.wl[i] > 2500
                              or self.exclude_wavelengths[0][0] <= self.wl[i] <= self.exclude_wavelengths[0][1]
                              or self.exclude_wavelengths[1][0] <= self.wl[i] <= self.exclude_wavelengths[1][1]]
        self.gui.txtExclude.setText(" ".join(str(i) for i in self.exclude_bands))
        self.gui.txtExclude.setCursorPosition(0)
        self.nbands_valid = self.nbands - len(self.exclude_bands)
        self.gui.cmbPCA.setEnabled(True)
        self.gui.cmbPCA.setChecked(True)

    def open_wavelength_selection(self):
        try:
            self.invoke_selection()
        except ValueError as e:
            self.abort(message=str(e))

    def invoke_selection(self):
        if self.LUT_path is None:
            raise ValueError('Specify Lookup-Table first')
        elif not os.path.isfile(self.LUT_path):
            raise ValueError('Lookup-Table not found: {}'.format(self.LUT_path))

        pass_exclude = []
        if not self.gui.txtExclude.text() == "":
            try:
                pass_exclude = self.gui.txtExclude.text().split(" ")
                pass_exclude = [int(pass_exclude[i])-1 for i in range(len(pass_exclude))]
            except:
                self.gui.txtExclude.setText("")
                pass_exclude = []

        self.main.select_wavelengths.populate(default_exclude=pass_exclude)
        self.main.select_wavelengths.gui.setModal(True)
        self.main.select_wavelengths.gui.show()

    def handle_PCA(self):
        if self.gui.cmbPCA.isChecked():
            self.gui.spnPCA.setEnabled(True)
            if self.nbands_valid < 5:
                self.npca = 1
            elif 5 < self.nbands_valid <= 15:
                self.npca = 5
            elif 15 < self.nbands_valid <= 120:
                self.npca = 10
            else:
                self.npca = 15
            self.gui.spnPCA.setValue(self.npca)
        if not self.gui.cmbPCA.isChecked():
            self.gui.spnPCA.setDisabled(True)
            self.npca = None

    def get_folder(self):
        path = str(QFileDialog.getExistingDirectory(caption='Select Output Directory for Model'))
        if path:
            self.gui.txtModelDir.setText(path)
            self.out_dir = self.gui.txtModelDir.text().replace("\\", "/")
            if not self.out_dir[-1] == "/":
                self.out_dir += "/"

    def check_and_assign(self):
        if not self.LUT_path:
            raise ValueError("A Lookup-Table metafile needs to be selected!")
        if not os.path.isdir(self.out_dir):
            raise ValueError("Output directory does not exist!")
        if self.gui.txtModelName.text() == "":
            raise ValueError("Please specify a name for the model")
        else:
            self.model_name = self.gui.txtModelName.text()
            self.model_meta = self.out_dir + self.model_name + '.meta'

        if self.gui.spnPCA.isEnabled():
            self.npca = self.gui.spnPCA.value()
            if self.npca > self.nbands_valid:
                raise ValueError("Model cannot be trained with {:d} components if LUT has only {:d} "
                                 "bands ({:d} minus {:d} excluded)".format(self.npca, self.nbands_valid, self.nbands,
                                                                           len(self.exclude_bands)))
        else:
            self.npca = None

    def abort(self, message):
        QMessageBox.critical(self.gui, "Error", message)

    def run_training(self):
        try:
            self.check_and_assign()
        except ValueError as e:
            self.abort(message=str(e))
            return

        self.prg_widget = self.main.prg_widget
        self.prg_widget.gui.lblCaption_l.setText("Training Machine Learning Model")
        self.prg_widget.gui.lblCaption_r.setText("Setting up training...")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.prg_widget.gui.show()

        self.main.QGis_app.processEvents()

        proc = processor.ProcessorMainFunction()

        try:
            proc.train_main.training_setup(lut_metafile=self.LUT_path, exclude_bands=self.exclude_bands, npca=self.npca,
                                           model_meta=self.model_meta)
        except ValueError as e:
            self.abort(message="Failed to setup model training: {}".format(str(e)))
            self.prg_widget.gui.lblCancel.setText("")
            self.prg_widget.gui.allow_cancel = True
            self.prg_widget.gui.close()
            return

        self.prg_widget.gui.lblCaption_r.setText("Starting training of Neural Network...")
        self.main.QGis_app.processEvents()

        try:
            proc.train_main.train_and_dump(prgbar_widget=self.prg_widget, QGis_app=self.main.QGis_app)
        except ValueError as e:
            self.abort(message="Failed to train model: {}".format(str(e)))
            self.prg_widget.gui.lblCancel.setText("")
            self.prg_widget.gui.allow_cancel = True
            self.prg_widget.gui.close()
            return

        self.prg_widget.gui.lblCancel.setText("")
        self.prg_widget.gui.allow_cancel = True
        self.prg_widget.gui.close()
        QMessageBox.information(self.gui, "Finish", "Training finished")
        self.gui.close()

class Select_Wavelengths:
    def __init__(self, main):
        self.main = main
        self.gui = Select_Wavelengths_GUI()
        self.connections()

    def connections(self):
        self.gui.cmdSendExclude.clicked.connect(lambda: self.send(direction="in_to_ex"))
        self.gui.cmdSendInclude.clicked.connect(lambda: self.send(direction="ex_to_in"))
        self.gui.cmdAll.clicked.connect(lambda: self.select(select="all"))
        self.gui.cmdNone.clicked.connect(lambda: self.select(select="none"))
        self.gui.cmdCancel.clicked.connect(lambda: self.gui.close())
        self.gui.cmdOK.clicked.connect(lambda: self.OK())

    def populate(self, default_exclude):
        if self.main.ann_training.nbands < 10: width = 1
        elif self.main.ann_training.nbands < 100: width = 2
        elif self.main.ann_training.nbands < 1000: width = 3
        else:
            width = 4

        for i in range(self.main.ann_training.nbands):
            if i in default_exclude:
                str_band_no = '{num:0{width}}'.format(num=i + 1, width=width)
                label = "band %s: %6.2f %s" % (str_band_no, self.main.ann_training.wl[i], self.main.ann_training.wunit)
                self.gui.lstExcluded.addItem(label)
            else:
                str_band_no = '{num:0{width}}'.format(num=i+1, width=width)
                label = "band %s: %6.2f %s" % (str_band_no, self.main.ann_training.wl[i], self.main.ann_training.wunit)
                self.gui.lstIncluded.addItem(label)

    def send(self, direction):
        if direction == "in_to_ex":
            origin = self.gui.lstIncluded
            destination = self.gui.lstExcluded
        elif direction == "ex_to_in":
            origin = self.gui.lstExcluded
            destination = self.gui.lstIncluded
        else:
            return

        for item in origin.selectedItems():
            index = origin.indexFromItem(item).row()
            destination.addItem(origin.takeItem(index))

        origin.sortItems()
        destination.sortItems()
        self.gui.setDisabled(False)

    def select(self, select):
        self.gui.setDisabled(True)
        if select == "all":
            self.gui.lstIncluded.selectAll()
            self.gui.lstExcluded.clearSelection()
            self.send(direction="in_to_ex")
        elif select == "none":
            self.gui.lstExcluded.selectAll()
            self.gui.lstIncluded.clearSelection()
            self.send(direction="ex_to_in")
        else:
            return

    def OK(self):
        list_object = self.gui.lstExcluded
        raw_list = []
        for i in range(list_object.count()):
            item = list_object.item(i).text()
            raw_list.append(item)

        self.main.ann_training.exclude_bands = [int(raw_list[i].split(" ")[1][:-1])-1 for i in range(len(raw_list))]
        self.main.ann_training.nbands_valid = self.main.ann_training.nbands - len(self.main.ann_training.exclude_bands)
        exclude_string = " ".join(str(x+1) for x in self.main.ann_training.exclude_bands)
        self.main.ann_training.gui.txtExclude.setText(exclude_string)

        for list_object in [self.gui.lstIncluded, self.gui.lstExcluded]:
            list_object.clear()

        self.gui.close()

class PRG:
    def __init__(self, main):
        self.main = main
        self.gui = PRG_GUI()
        self.gui.lblCancel.setVisible(False)
        self.connections()

    def connections(self):
        self.gui.cmdCancel.clicked.connect(lambda: self.cancel())

    def cancel(self):
        self.gui.allow_cancel = True
        self.gui.cmdCancel.setDisabled(True)
        self.gui.lblCancel.setText("-1")

class MainUiFunc:
    def __init__(self):
        self.QGis_app = QApplication.instance()
        self.ann_training = ANN_Training(self)
        self.select_wavelengths = Select_Wavelengths(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.ann_training.gui.show()

if __name__ == '__main__':
    from enmapbox.testing import initQgisApplication
    app = initQgisApplication()
    m = MainUiFunc()
    m.show()
    sys.exit(app.exec_())
