
# -*- coding: utf-8 -*-

# TRIDENT Project
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox, QInputDialog
import subprocess, os, sys
import nibabel as nib
from util.support import *

global path_prefix
global total_row
global total_col
global total_no


# prevent program crashing on errors 
def my_excepthook(type, value, tback):

    # log the exception here

    # then call the default handler
    sys.__excepthook__(type, value, tback)


sys.excepthook = my_excepthook


class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        self.sectionFormat = QtGui.QTextCharFormat()
        self.sectionFormat.setForeground(QtCore.Qt.blue)
        self.sectionFormat.setFontPointSize(30)
        self.successFormat = QtGui.QTextCharFormat()
        self.successFormat.setForeground(QtCore.Qt.darkGreen)
        self.successFormat.setFontPointSize(20)
        self.errorFormat = QtGui.QTextCharFormat()
        self.errorFormat.setForeground(QtCore.Qt.red)
        self.errorFormat.setFontPointSize(20)
        self.normalFormat = QtGui.QTextCharFormat()
        self.normalFormat.setForeground(QtCore.Qt.black)
        self.normalFormat.setFontPointSize(20)

    def highlightBlock(self, text):
        if text.startswith('TRIDENT'):
            self.setFormat(0, len(text), self.sectionFormat)
        elif '[*FAILED*]' in text or '[WARNING!]' in text or '[ERROR]' in text or 'TBD' in text or 'Current' in text:
            self.setFormat(0, len(text), self.errorFormat)
        elif '[SUCCESS]' in text or 'DONE' in text:
            self.setFormat(0, len(text), self.successFormat)
        else:
            self.setFormat(0, len(text), self.normalFormat)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setObjectName("Dialog")
        Dialog.resize(1800, 851)
        # self.result = QtWidgets.QTextEdit(Dialog)
        # self.result.setGeometry(QtCore.QRect(100, 30, 1100, 200))
        # Set result window to be read only
        # self.result.setReadOnly(True)
        # self.result.setObjectName("result")
        #
        # User layout
        self.study_label = QtWidgets.QLabel(Dialog)
        self.study_label.setGeometry(QtCore.QRect(50, 30, 50, 25))
        self.study_label.setObjectName("study_label")
        self.study = QtWidgets.QComboBox(Dialog)
        self.study.setGeometry(QtCore.QRect(100, 30, 100, 25))
        self.study.setObjectName("study")

        self.preset_label = QtWidgets.QLabel(Dialog)
        self.preset_label.setGeometry(QtCore.QRect(250, 30, 50, 25))
        self.preset_label.setObjectName("preset_label")
        self.preset = QtWidgets.QComboBox(Dialog)
        self.preset.setGeometry(QtCore.QRect(300, 30, 100, 25))
        self.preset.setObjectName("preset")

        self.input_label = QtWidgets.QLabel(Dialog)
        self.input_label.setGeometry(QtCore.QRect(450, 30, 130, 25))
        # self.input_label.setObjectName("Input folder path")
        self.input_path = QtWidgets.QTextEdit(Dialog)
        self.input_path.setGeometry(QtCore.QRect(QtCore.QRect(580, 30, 250, 25)))
        self.input_path.setObjectName("input_path")
        self.input_path.setPlaceholderText("[Drag input folder here]")

        # self.input_browser = QtWidgets.QPushButton(Dialog)
        # self.input_browser.setGeometry(QtCore.QRect(850, 30, 80, 25))
        # self.input_browser.setObjectName("input_browser")
        # self.input_browser.setText("Browse...")

        self.foldername_label = QtWidgets.QLabel(Dialog)
        self.foldername_label.setGeometry(QtCore.QRect(1000, 30, 130, 25))
        self.foldername_label.setObjectName("foldername")
        self.foldername = QtWidgets.QLineEdit(Dialog)
        self.foldername.setGeometry(QtCore.QRect(1150, 30, 250, 25))
        self.foldername.setObjectName("foldername")
        self.foldername.setText('lesion_activity')

        self.lesion_file_label = QtWidgets.QLabel(Dialog)
        self.lesion_file_label.setGeometry(QtCore.QRect(50, 60, 130, 25))
        self.lesion_file_label.setObjectName("lesion_file_label")
        self.lesion_file = QtWidgets.QTextEdit(Dialog)
        self.lesion_file.setGeometry(QtCore.QRect(200, 60, 250, 25))
        self.lesion_file.setObjectName("lesion_file")
        self.lesion_file.setPlaceholderText('Drag ROI here')

        # self.subtraction_label = QtWidgets.QLabel(Dialog)
        # self.subtraction_label.setGeometry(QtCore.QRect(500, 60, 130, 25))
        # self.subtraction_label.setObjectName("subtraction_label")
        # self.subtraction = QtWidgets.QLineEdit(Dialog)
        # self.subtraction.setGeometry(QtCore.QRect(650, 60, 250, 25))
        # self.subtraction.setObjectName("subtraction")
        # self.subtraction.setPlaceholderText('Drag subtraction file here')

        self.clear = QtWidgets.QPushButton(Dialog)
        self.clear.setGeometry(QtCore.QRect(600, 780, 150, 40))
        self.clear.setObjectName("clear")
        self.clear.setText('Clear')

        self.find = QtWidgets.QPushButton(Dialog)
        self.find.setGeometry(QtCore.QRect(800, 780, 150, 40))
        self.find.setObjectName("find")
        self.find.setText('Find contrast range')

        self.generate = QtWidgets.QPushButton(Dialog)
        self.generate.setGeometry(QtCore.QRect(1000, 780, 150, 40))
        self.generate.setObjectName("generate")
        self.generate.setText('Generate')
        self.generate.setStyleSheet("QPushButton {color: black;}")

        current_x = start_x = 20
        current_y = start_y = 100
        fix_width = 200
        fix_height = 25
        incremental_x = 350
        incremental_y = 230

        global total_row
        global total_col
        global total_no
        total_row = 3
        total_col = 5
        total_no = total_row * total_col

        self.loc_label = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.associate = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.item_no = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.name_label = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.itemname = [[None for _ in range(total_col)] for _ in range(total_row)]

        self.url_label = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.item_url = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.lesion = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.blank = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.none = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.t1 = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.t1_brain = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.t1_original = [[None for _ in range(total_col)] for _ in range(total_row)]

        self.manual_label = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.m_min_label = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.m_max_label = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.m_min = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.m_max = [[None for _ in range(total_col)] for _ in range(total_row)]

        self.window = [[None for _ in range(total_col)] for _ in range(total_row)]
        self.command = [[None for _ in range(total_col)] for _ in range(total_row)]

        for row_no in range(total_row):
            for col_no in range(total_col):
                self.item_no[row_no][col_no] = QtWidgets.QLabel(Dialog)
                self.item_no[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x, current_y, 40, fix_height))
                self.item_no[row_no][col_no].setText(_translate("Dialog", 'No: ' +
                                                                str(row_no * total_col + col_no + 1)))

                self.loc_label[row_no][col_no] = QtWidgets.QLabel(Dialog)
                self.loc_label[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 50, current_y, fix_width, fix_height))
                self.loc_label[row_no][col_no].setObjectName('loc' + str(row_no+1) + str(col_no+1))
                self.loc_label[row_no][col_no].setText(_translate("Dialog", 'Associate T1 No.:'))

                self.associate[row_no][col_no] = QtWidgets.QComboBox(Dialog)
                self.associate[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 160, current_y, 50, fix_height))
                self.associate[row_no][col_no].setObjectName('associate' + str(row_no + 1) + str(col_no + 1))
                # tmp =
                self.associate[row_no][col_no].addItems((np.arange(1, total_no+1, 1)).astype(str))
                self.associate[row_no][col_no].setCurrentIndex(int((row_no) * 5 + col_no))
                self.associate[row_no][col_no].setEnabled(False)

                self.name_label[row_no][col_no] = QtWidgets.QLabel(Dialog)
                self.name_label[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x, current_y + 30, 40, fix_height))
                self.name_label[row_no][col_no].setObjectName('itemname' + str(row_no + 1) + str(col_no + 1))
                self.name_label[row_no][col_no].setText(_translate("Dialog", 'Name:'))

                self.itemname[row_no][col_no] = QtWidgets.QTextEdit(Dialog)
                self.itemname[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 50, current_y + 30, 180, fix_height))
                self.itemname[row_no][col_no].setObjectName('itemname' + str(row_no + 1) + str(col_no + 1))
                self.itemname[row_no][col_no].setPlaceholderText("[Display name]")
                self.itemname[row_no][col_no].setEnabled(False)

                self.url_label[row_no][col_no] = QtWidgets.QLabel(Dialog)
                self.url_label[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x, current_y + 60, 40, fix_height))
                self.url_label[row_no][col_no].setObjectName('url' + str(row_no + 1) + str(col_no + 1))
                self.url_label[row_no][col_no].setText(_translate("Dialog", 'URL:'))

                self.item_url[row_no][col_no] = QtWidgets.QTextEdit(Dialog)
                self.item_url[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 50, current_y + 60, 180, fix_height))
                self.item_url[row_no][col_no].setObjectName('url' + str(row_no + 1) + str(col_no + 1))
                self.item_url[row_no][col_no].setPlaceholderText("[Drag nii here]")
                self.item_url[row_no][col_no].setEnabled(False)

                self.lesion[row_no][col_no] = QtWidgets.QCheckBox(Dialog)
                self.lesion[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x, current_y + 90, fix_width, fix_height))
                self.lesion[row_no][col_no].setObjectName('lesion' + str(row_no + 1) + str(col_no + 1))
                self.lesion[row_no][col_no].setText('Lesion')
                self.lesion[row_no][col_no].setEnabled(False)

                self.blank[row_no][col_no] = QtWidgets.QCheckBox(Dialog)
                self.blank[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 80, current_y + 90, fix_width, fix_height))
                self.blank[row_no][col_no].setObjectName('blank' + str(row_no + 1) + str(col_no + 1))
                self.blank[row_no][col_no].setText('Blank')
                self.blank[row_no][col_no].setEnabled(False)

                self.none[row_no][col_no] = QtWidgets.QCheckBox(Dialog)
                self.none[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 160, current_y + 90, fix_width, fix_height))
                self.none[row_no][col_no].setObjectName('none' + str(row_no + 1) + str(col_no + 1))
                self.none[row_no][col_no].setText('None')
                self.none[row_no][col_no].setChecked(True)
                self.none[row_no][col_no].stateChanged.connect(self.check_none)

                self.t1[row_no][col_no] = QtWidgets.QCheckBox(Dialog)
                self.t1[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x, current_y + 110, 60, fix_height))
                self.t1[row_no][col_no].setObjectName('t1' + str(row_no + 1) + str(col_no + 1))
                self.t1[row_no][col_no].setText('T1')
                self.t1[row_no][col_no].setEnabled(False)
                self.t1[row_no][col_no].stateChanged.connect(self.check_t1)

                self.t1_brain[row_no][col_no] = QtWidgets.QTextEdit(Dialog)
                self.t1_brain[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 60, current_y + 110, 80, fix_height))
                self.t1_brain[row_no][col_no].setObjectName('url' + str(row_no + 1) + str(col_no + 1))
                self.t1_brain[row_no][col_no].setPlaceholderText("[brain]")
                self.t1_brain[row_no][col_no].setEnabled(False)

                self.t1_original[row_no][col_no] = QtWidgets.QTextEdit(Dialog)
                self.t1_original[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 160, current_y + 110, 80, fix_height))
                self.t1_original[row_no][col_no].setObjectName('url' + str(row_no + 1) + str(col_no + 1))
                self.t1_original[row_no][col_no].setPlaceholderText("[original]")
                self.t1_original[row_no][col_no].setEnabled(False)

                self.manual_label[row_no][col_no] = QtWidgets.QLabel(Dialog)
                self.manual_label[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x, current_y + 130, fix_width, fix_height))
                self.manual_label[row_no][col_no].setObjectName('none' + str(row_no + 1) + str(col_no + 1))
                self.manual_label[row_no][col_no].setText('Manual contrast range: ')

                intensity_rx = QRegExp('^(2[0-5][0-5]|1[0-9][0-9]|[1-9]?[0-9])$')
                validator = QRegExpValidator(intensity_rx)

                self.m_min_label[row_no][col_no] = QtWidgets.QLabel(Dialog)
                self.m_min_label[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x, current_y + 160, 80, fix_height))
                self.m_min_label[row_no][col_no].setObjectName('none' + str(row_no + 1) + str(col_no + 1))
                self.m_min_label[row_no][col_no].setText('Min(0~255): ')

                self.m_min[row_no][col_no] = QtWidgets.QLineEdit(Dialog)
                self.m_min[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 80, current_y + 160, 40, fix_height))
                self.m_min[row_no][col_no].setObjectName('none' + str(row_no + 1) + str(col_no + 1))
                self.m_min[row_no][col_no].setValidator(validator)
                self.m_min[row_no][col_no].setEnabled(False)

                self.m_max_label[row_no][col_no] = QtWidgets.QLabel(Dialog)
                self.m_max_label[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 130, current_y + 160, 80, fix_height))
                self.m_max_label[row_no][col_no].setObjectName('none' + str(row_no + 1) + str(col_no + 1))
                self.m_max_label[row_no][col_no].setText('Max(0~255): ')

                self.m_max[row_no][col_no] = QtWidgets.QLineEdit(Dialog)
                self.m_max[row_no][col_no].setGeometry(
                    QtCore.QRect(current_x + 210, current_y + 160, 40, fix_height))
                self.m_max[row_no][col_no].setObjectName('none' + str(row_no + 1) + str(col_no + 1))
                self.m_max[row_no][col_no].setValidator(validator)
                self.m_max[row_no][col_no].setEnabled(False)

                current_x += incremental_x
            current_x = start_x
            current_y = current_y + incremental_y

        Dialog.setWindowTitle(_translate("Dialog", "Slice Maker Helper"))

        self.study_label.setText(_translate("Dialog", "Study:"))
        self.preset_label.setText(_translate("Dialog", "Preset:"))
        self.foldername_label.setText(_translate("Dialog", "Output folder name:"))
        self.input_label.setText(_translate("Dialog", "Input folder path:"))
        self.lesion_file_label.setText(_translate("Dialog", "Lesion file path:"))
        # self.subtraction_label.setPlaceholderText(_translate("Dialog", "Subtraction file path:"))

        # connect the button/checkbox with the corresponding functions
        # self.highlighter = Highlighter(self.result.document())
        # self.input_browser.clicked.connect(self.browse_folder)
        self.load_preset()
        self.find.clicked.connect(self.find_range)
        self.clear.clicked.connect(self.clear_input)
        self.generate.clicked.connect(self.generate_file)
        self.preset.currentTextChanged.connect(self.load_preset)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Slice Maker Helper"))

        self.study_label.setText(_translate("Dialog", "Study:"))
        self.preset_label.setText(_translate("Dialog", "Preset:"))
        self.foldername_label.setText(_translate("Dialog", "Output folder name:"))
        self.input_label.setText(_translate("Dialog", "Input folder path:"))
        # self.itemname_label.setText(_translate("Dialog", "Item name:"))

    def browse_folder(self):
        fname = QFileDialog.getExistingDirectory(None, 'Select Folder', '/Volumes/Studies')
        self.input_path.setText(fname)

    def check_none(self):
        for row_no in range(total_row):
            for col_no in range(total_col):
                if self.none[row_no][col_no].isChecked():
                    self.associate[row_no][col_no].setEnabled(False)
                    self.itemname[row_no][col_no].setEnabled(False)
                    self.item_url[row_no][col_no].setEnabled(False)
                    self.lesion[row_no][col_no].setChecked(False)
                    self.lesion[row_no][col_no].setEnabled(False)
                    self.blank[row_no][col_no].setChecked(False)
                    self.blank[row_no][col_no].setEnabled(False)
                    self.t1[row_no][col_no].setChecked(False)
                    self.t1[row_no][col_no].setEnabled(False)
                    self.m_min[row_no][col_no].setEnabled(False)
                    self.m_max[row_no][col_no].setEnabled(False)
                else:
                    self.associate[row_no][col_no].setEnabled(True)
                    self.itemname[row_no][col_no].setEnabled(True)
                    self.item_url[row_no][col_no].setEnabled(True)
                    self.lesion[row_no][col_no].setEnabled(True)
                    self.blank[row_no][col_no].setEnabled(True)
                    self.t1[row_no][col_no].setEnabled(True)
                    self.m_min[row_no][col_no].setEnabled(True)
                    self.m_max[row_no][col_no].setEnabled(True)

    def check_t1(self):
        for row_no in range(total_row):
            for col_no in range(total_col):
                if self.t1[row_no][col_no].isChecked():
                    self.t1_brain[row_no][col_no].setEnabled(True)
                    self.t1_original[row_no][col_no].setEnabled(True)
                else:
                    self.t1_brain[row_no][col_no].setEnabled(False)
                    self.t1_original[row_no][col_no].setEnabled(False)

    def generate_file(self):
        path_prefix = self.input_path.toPlainText()[7:]
        output_folder = self.foldername.text()
        exist = os.path.exists(path_prefix)
        print(path_prefix)
        if exist:
            os.chdir(path_prefix)
        else:
            QMessageBox.information(None, 'ERROR', 'Input folder not found!', QMessageBox.Ok)
            return
        subprocess.call(['mkdir', output_folder])

        # Check the existence of all input images and record the position of the images
        position = []
        exist = True
        for row_no in range(total_row):
            for col_no in range(total_col):
                if not self.none[row_no][col_no].isChecked():
                    position.append([row_no, col_no])
                    if not self.blank[row_no][col_no].isChecked():
                        file = parse_url(self.item_url[row_no][col_no].toPlainText())
                        exist = os.path.exists(file)
                    if not exist:
                        QMessageBox.information(None, 'ERROR', 'Image file of Item No.' +
                                                str(row_no * total_col + col_no + 1) + 'not found!', QMessageBox.Ok)
                        return

        print(position)
        # find the size of the output report
        result_size = parse_size(self, position, total_col)
        if not result_size:
            return

        print(result_size)

        # find reference T1-weighted image
        t1_loc = find_t1(self, total_row, total_col)
        print('t1_loc', t1_loc)

        # create corresponding folders and copy associated files to the folders to calculate the intensity value of
        # grey and white matter
        os.chdir(output_folder)
        for loc in t1_loc:
            # store the name of the sequences associated with the current t1 (not including current T1),
            # with .nii or .nii.gz extension
            seq_list = []
            folder_name = self.itemname[loc[0]][loc[1]].toPlainText()
            current_t1_name = parse_url(self.item_url[loc[0]][loc[1]].toPlainText())
            t1_brain = parse_url(self.t1_brain[loc[0]][loc[1]].toPlainText())
            t1_original = parse_url(self.t1_original[loc[0]][loc[1]].toPlainText())
            subprocess.call(['mkdir', folder_name])
            item_no = loc[0] * total_col + loc[1] + 1
            associate_no = find_associate(self, total_row, total_col, item_no)
            print('assciiate_no:', associate_no)
            print(os.getcwd())
            # subprocess.call(['cp', current_t1_name, folder_name])
            # subprocess.call(['cp', t1_brain, folder_name])
            # subprocess.call(['cp', t1_original, folder_name])
            if self.lesion_file.toPlainText() != '':
                subprocess.call(['cp', parse_url(self.lesion_file.toPlainText()), folder_name])
            #
            # for a in associate_no:
            #     url = parse_url(self.item_url[a[0]][a[1]].toPlainText())
            #     tmp_name = url.split('/')[-1]
            #     seq_list.append(tmp_name)
            #     subprocess.call(['cp', url, folder_name])

            os.chdir(folder_name)
            print(os.getcwd())
            tmp_list = []

            # perform fast on T1 and find windowing for T1
            # subprocess.call(['mri_nu_correct.mni', '--i', current_t1_name.split('/')[-1], '--o',
            #                  strip_name(current_t1_name) + '_n3.nii.gz'])
            # subprocess.call(['mri_nu_correct.mni', '--i', t1_original.split('/')[-1], '--o',
            #                  strip_name(t1_original) + '_n3.nii.gz'])

            #
            # seq_list = tmp_list
            t1_brain = strip_name(self.t1_brain[loc[0]][loc[1]].toPlainText()) + '.nii.gz'
            t1_original = strip_name(self.t1_original[loc[0]][loc[1]].toPlainText()) + '_n3.nii.gz'
            # subprocess.call(['fast', t1_brain])
            white_name = t1_brain[:-7] + '_pve_2.nii.gz'
            grey_name = t1_brain[:-7] + '_pve_1.nii.gz'
            i_min, i_max = calculate_t1_window(self, current_t1_name, t1_original, t1_brain, seq_list, white_name,
                                               grey_name)
            i_min = int(i_min)
            i_max = int(i_max)
            print('t1min: ', i_min, 't1max:', i_max)
            self.window[loc[0]][loc[1]] = [i_min, i_max]
            assign_name = folder_name + '/' + strip_name(current_t1_name) + '_n3.nii.gz=' + str(loc[0]) + str(loc[1])
            assign_loc = ''
            if self.lesion[loc[0]][loc[1]].isChecked():
                assign_loc = '(' + str(loc[0]) + str(loc[1]) + ' [' + str(i_min) + ',' + str(i_max) + '] mask les, ' + \
                             "'" + self.itemname[loc[0]][loc[1]].toPlainText() + "')"
            else:
                assign_loc = '(' + str(loc[0]) + str(loc[1]) + ' [' + str(i_min) + ',' + str(i_max) + '], ' +\
                             "'" + self.itemname[loc[0]][loc[1]].toPlainText() + "')"

            self.command[loc[0]][loc[1]] = [assign_name, assign_loc]

            # the images windowing need to be calculated assocaited to current T1 are stored in seq_list
            for a in associate_no:
                url = parse_url(self.item_url[a[0]][a[1]].toPlainText())
                s = url.split('/')[-1]
                # subprocess.call(['mri_nu_correct.mni', '--i', s, '--o', strip_name(s) + '_n3.nii.gz'])
                i_min, i_max = calculate_seq_window(self, strip_name(s) + '_n3.nii.gz', t1_original, t1_brain, white_name, grey_name)
                i_min = int(i_min)
                i_max = int(i_max)
                self.window[a[0]][a[1]] = [i_min, i_max]
                assign_name = folder_name + '/' + strip_name(s) + '_n3.nii.gz=' + str(a[0]) + str(a[1])
                assign_loc = ''
                if self.lesion[a[0]][a[1]].isChecked():
                    assign_loc = '(' + str(a[0]) + str(a[1]) + ' [' + str(i_min) + ',' + str(
                        i_max) + '] mask les, ' + "'" + self.itemname[a[0]][a[1]].toPlainText() + "')"
                else:
                    assign_loc = '(' + str(a[0]) + str(a[1]) + ' [' + str(i_min) + ',' + str(i_max) + '], ' +\
                                 "'" + self.itemname[a[0]][a[1]].toPlainText() + "')"
                print(assign_name, assign_loc)
                self.command[a[0]][a[1]] = [assign_name, assign_loc]

            os.chdir('..')


        # Generate slidemaker bash script
        result = generate_command(self, position)
        print(result)



        # return

    # load settings from preset
    def load_preset(self):
        path = os.path.realpath('helper.py').rstrip('helper.py') + 'preset'
        item = os.listdir(path)
        self.preset.addItems(item)

        return

    def find_range(self):
        return

    def clear_input(self):
        global total_row
        global total_col
        self.input_path.setText('')
        self.foldername.setText('lesion_activity')
        # print(total_row, total_col)

        for row_no in range(total_row):
            for col_no in range(total_col):
                self.itemname[row_no][col_no].setText('')
                self.item_url[row_no][col_no].setText('')
                self.lesion[row_no][col_no].setChecked(False)
                self.blank[row_no][col_no].setChecked(False)
                self.none[row_no][col_no].setChecked(True)
                # self.


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
