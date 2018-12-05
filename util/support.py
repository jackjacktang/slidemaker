from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox
import subprocess, os, sys
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt


def parse_url(input_url):
    output_url = ''
    if input_url.startswith('file:'):
        output_url = input_url[7:]
        return output_url
    else:
        return input_url
    return


def parse_size(self, position, total_col):
    if len(position) == 0:
        QMessageBox.information(None, 'ERROR', 'No image file', QMessageBox.Ok)
        return False
    tmp_row = 0
    tmp_col = 0
    for p in position:
        if p[0] > tmp_row:
            tmp_row += 1
            tmp_col = 0
        if p[1] - tmp_col <= 1:
            tmp_col = p[1]
        elif p[1] - tmp_col > 1:
            QMessageBox.information(None, 'ERROR',
                                    'Invalid position of  item: ' + str(total_col * tmp_row + p[1] + 1), QMessageBox.Ok)
            return False
    return [tmp_row+1, tmp_col+1]


def strip_name(input):
    if input.endswith('.nii'):
        return input.split('/')[-1][:-4]
    elif input.endswith('.nii.gz'):
        return input.split('/')[-1][:-7]


def find_t1(self, total_row, total_col):
    t1_loc = []
    for row_no in range(total_row):
        for col_no in range(total_col):
            if self.t1[row_no][col_no].isChecked():
                t1_loc.append([row_no, col_no])
    return t1_loc


def find_associate(self, total_row, total_col, item_no):
    file_list = []
    for row_no in range(total_row):
        for col_no in range(total_col):
            if int(self.associate[row_no][col_no].currentText()) == int(item_no) and \
                    int(item_no) != int(row_no * total_col + col_no + 1):
                file_list.append([row_no, col_no])
    return file_list

def parse_preset(self, text):
    for i in text():
        print(i)

def input_validator():
    return


def expand_window(self, dat, low, high, percentage=0.9):
    ipt_dat = np.copy(dat)
    ipt_dat[ipt_dat < 0] = 0
    flatten = ipt_dat.ravel()
    flatten[flatten > 255] = 0
    flatten = flatten[flatten > 10]

    occ, b, _ = plt.hist(flatten, bins=255)

    occ = np.insert(occ, 0, occ[1])
    low_ind = 0
    high_ind = 0

    for i in b:
        if i > low:
            break
        low_ind += 1

    for i in b:
        if i > high:
            break
        high_ind += 1

    while np.sum(occ[low_ind:high_ind]) / np.sum(occ) < percentage:
        if b[low_ind] > 10 and low_ind > 1:
            low_ind -= 1
        if b[high_ind] < 255 and len(b) > high_ind:
            high_ind += 1

    return b[low_ind], b[high_ind]


def calculate_t1_window(self, current_t1_name, t1_original, t1_brain, seq_list, white_name, grey_name):
    print(os.getcwd())
    # subprocess.call(['flirt', '-v', '-dof', '6', '-searchrx', '-20', '20',
    #                  '-searchry', '-20', '20', '-searchrz', '-20', '20',
    #                  '-in', t1_original, '-ref', current_t1_name, '-omat', 'rawT1_2_regT1.mat'])
    #
    # subprocess.call(['flirt', '-in', grey_name, '-ref', current_t1_name, '-out', 't1_grey.nii.gz', '-applyxfm',
    #                  '-init', 'rawT1_2_regT1.mat'])
    #
    # subprocess.call(['flirt', '-in', white_name, '-ref', current_t1_name, '-out', 't1_white.nii.gz', '-applyxfm',
    #                  '-init', 'rawT1_2_regT1.mat'])

    t1_img = nib.load(strip_name(current_t1_name) + '_n3.nii.gz')
    t1_dat = t1_img.get_data()
    g_img = nib.load('t1_grey.nii.gz')
    g_dat = g_img.get_data()
    print(np.mean(g_dat))
    g_dat[g_dat > 0.5] = 1
    g_dat[g_dat <= 0.5] = 0
    grey = t1_dat * g_dat
    grey = grey[grey > 0].ravel()
    grey_mean = np.mean(grey)

    w_img = nib.load('t1_white.nii.gz')
    w_dat = w_img.get_data()
    print(np.mean(w_dat))
    w_dat[w_dat > 0.5] = 1
    w_dat[w_dat <= 0.5] = 0
    white = t1_dat * w_dat
    white = white[white > 0].ravel()
    white_mean = np.mean(white)

    print(strip_name(current_t1_name) + '_n3.nii.gz')
    print('grey', grey_mean, 'white', white_mean)
    i_min, i_max = expand_window(self, t1_dat, np.min([grey_mean, white_mean]), np.max([grey_mean, white_mean]))
    return i_min, i_max


def calculate_seq_window(self, seq_name, t1_original, t1_brain, white_name, grey_name):
    # subprocess.call(['flirt', '-v', '-dof', '6', '-searchrx', '-20', '20',
    #                  '-searchry', '-20', '20', '-searchrz', '-20', '20',
    #                  '-in', t1_original, '-ref', seq_name, '-omat', 'rawT1_2_' + strip_name(seq_name) + '.mat'])
    #
    # subprocess.call(['flirt', '-in', grey_name, '-ref', seq_name, '-out', 't1_grey.nii.gz', '-applyxfm',
    #                  '-init', 'rawT1_2_' + strip_name(seq_name) + '.mat'])
    #
    # subprocess.call(['flirt', '-in', white_name, '-ref', seq_name, '-out', 't1_white.nii.gz', '-applyxfm',
    #                  '-init', 'rawT1_2_' + strip_name(seq_name) + '.mat'])

    seq_img = nib.load(strip_name(seq_name) + '.nii.gz')
    seq_dat = seq_img.get_data()
    g_img = nib.load('t1_grey.nii.gz')
    g_dat = g_img.get_data()
    print(np.mean(g_dat))
    g_dat[g_dat > 0.5] = 1
    g_dat[g_dat <= 0.5] = 0
    grey = seq_dat * g_dat
    grey = grey[grey > 0].ravel()
    grey_mean = np.mean(grey)

    w_img = nib.load('t1_white.nii.gz')
    w_dat = w_img.get_data()
    print(np.mean(w_dat))
    w_dat[w_dat > 0.5] = 1
    w_dat[w_dat <= 0.5] = 0
    white = seq_dat * w_dat
    white = white[white > 0].ravel()
    white_mean = np.mean(white)

    print(strip_name(seq_name) + '_n3.nii.gz')
    print('grey', grey_mean, 'white', white_mean)
    i_min, i_max = expand_window(self, seq_dat, np.min([grey_mean, white_mean]), np.max([grey_mean, white_mean]))
    return i_min, i_max


def generate_command(self, position):
    result = 'slidemaker "'

    for p in position:
        result = result + self.command[p[0]][p[1]][0] + ' '

    if self.lesion_file.toPlainText() != '':
        result = result + parse_url(self.lesion_file).split('/')[-1] + '=les '

    for p in position:
        result = result + self.command[p[0]][p[1]][1] + ' '

    return result + '"'
