"""

This program is part of the 3DPlan algorithm.
This program contains the utilities of the 3DPlan software.
Copyright (C) 2021 Theodore Betsas

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os
import cv2 as cv
import numpy as np
import sdxf
import sys
from pathlib import Path
import datetime


def classify_points(path: str = '', filename: str = '', savefilename: str = '', t: int = 230, method: int = 0):
    """
    This function classifies the point cloud into labelled and unlabelled points
    Args:
        path (str)         = Working directory.
        filename (str)     = Ppoint cloud file.
        savefilename (str) = The name of the saved file.
        t (int)            = Threshold value.
        method(int)        = In which approach will be used.

    Returns:

    """
    message('Save the detected points to edges.txt file ...')
    detected_points = 0
    savefile = f'{path}/{savefilename}.txt'
    cleararchive(savefile)
    with open(f'{path}/{filename}', 'r') as f:
        all_lines = f.readlines()
        for line in all_lines[15:]:
            splitline = line.split(' ')
            if method == 0 or method == 2:
                label = int(splitline[-1])
            else:
                label = int(splitline[-2])
            if label >= t:
                detected_points += 1
                write_a_file(path, savefilename, '.txt', line)
    message(f'{detected_points} points are saved!')


def convert_points_2_cvkeypoints(points):
    """
    This function converts a given point set to cvkeypoints.
    Args:
        points (numpy array/list) = The set of points.

    Returns:
        cv_kp (numpy array) = The set of points as "cvkeypoints"

    """
    cv_kp = [cv.KeyPoint(x=pt[0], y=pt[1], _size=1) for pt in points]
    return cv_kp


def error_message(msg: str = '', sysex: bool = False):
    """
    This function is used for printing error messages when the latter occur
    Args:
        msg (str)    = Working directory.
        sysex (bool) = Ppoint cloud file.

    Returns:

    """
    dt = datetime.datetime.now()
    if sysex:
        sys.exit(f'{dt}, {msg}\n')
    else:
        message(msg)


def export2ply(points3d: list = [], colors: list = [], filename: str = ''):
    """
    This function saves the calculated 3D points with their corresponding colours to a .ply file.
    Args:
        points3d (list) = The set of points.
        colors (list)   = The set of colors.
        filename (str)  = The name of the saved file.

    Returns:

    """
    colors = np.array(colors)
    points3d = np.hstack([points3d, colors])

    ply_header = 'ply\nformat ascii 1.0\nelement vertex %(points_num)d\nproperty float x\nproperty float y\nproperty float z\nproperty int red\nproperty int green\nproperty int blue\nend_header\n'
    with open(f'{Path(os.getcwd())}/Lines/{filename}', 'w') as f:
        f.write(ply_header % dict(points_num=len(points3d)))
        np.savetxt(f, points3d, '%f %f %f %d %d %d')


def find_files(file_path: str = '', file_suffix: str = ''):
    """
    This function finds all the files that a directory contains with a specific suffix.
    Args:
        file_path (str)   = The path of the images.
        file_suffix (str) = The suffix of the desired images.

    Returns:
        filenames (list) = Contains the imagenames of all the detected images.

    """
    filenames = [f for f in os.listdir(file_path) if os.path.splitext(f)[-1] == file_suffix]
    return filenames


def input_check(msg: str = '', valid: list = [], error_msg: str = ''):
    """
    This function receives an answer from the user and checks if it is valid or not.
    Args:
        msg (str)       = The question.
        valid (list)    = The valid answers.
        error_msg (str) = The message, printed if a wrong answer is given.

    Returns:
        inpt (etc) = User's answer.

    """
    done = 1
    while done == 1:
        try:
            dt = datetime.datetime.now()
            inpt = input(f'{dt}, {msg}')

            if type(valid[0]) == int:
                inpt = int(inpt)

            if inpt in valid:
                done = 0

            else:
                error_message(f'{error_msg}. The valid answers are {valid}. Choose one!')
        except ValueError:
            done = 1
            error_message(f'{error_msg} the valid answers are {valid}. Choose one!')
    return inpt


def lines2dxf(lines: list = []):
    """
    This function receives a list of lists in which the first and the second element is the firs the last point of a line. The points must be 3D.
    Args:
        lines (list of lists) = A list of lists which contains two of each lines' points for the vectorization step.

    Returns:

    """
    d = sdxf.Drawing()
    layername = 'lines'
    for line in lines:
        pts = [[np.float(line[0][0]), np.float(line[0][1]), np.float(line[0][2])],
               [np.float(line[1][0]), np.float(line[1][1]), np.float(line[1][2])]]
        # print (pts)
        d.append(sdxf.Line(points=[pts[0], pts[1]], layer=layername, color=255))
    d.saveas(f'{os.getcwd()}/Lines/3DPlan.dxf')


def lines_env(parent_directory, method=1):
    """
    This function constructs the environment of the 3DPlan algorithm
    Args:
        parent_directory (str) = The parent directory.
        method (int)           = Which method was used.

    Returns:

    """
    mkdir('Lines')
    if method == 1:
        osf_path = f'{parent_directory}/OpenSfM/data'
        os.system(f'cp {osf_path}/3DPlan/undistorted/depthmaps/merged.ply Lines')


def message(msg: str = ''):
    """
    This function is used instead of the print function
    Args:
        msg (str) = The message.

    Returns:

    """
    dt = datetime.datetime.now()
    print(f'{dt}, {msg}\n')


def metamessage(msg: str = ''):
    """
    This function is the same as the message but is compatible with metashape software v.1.5.2
    Args:
        msg (str) = The message.

    Returns:

    """
    dt = datetime.datetime.now()
    print(dt + ', ' + msg + '\n')


def mkdir(new_directory_name: str = ''):
    """
    This function makes a new directory into the working directory.
    Args:
        new_directory_name (str) = New directory's name.
    """
    if not os.path.exists(new_directory_name):
        os.mkdir(new_directory_name)


def osfm_env(parent_directory):
    """
    This function makes the directories and copy-paste the appropriate files for the OpenSFM pipeline
    Args:
        parent_directory (str) = The parent directory.

    Returns:

    """
    osf_path = f'{parent_directory}/OpenSfM/data'
    mkdir(f'{osf_path}/3DPlan')
    mkdir(f'{osf_path}/3DPlan/images')
    os.system(f'cp images/*tiff {osf_path}/3DPlan/images')
    os.system(f'cp {osf_path}/berlin/config.yaml {osf_path}/3DPlan')


def points2clusters(points, labels, label):
    """
    This function identifies wich points are included into the given label class, and then returns theirs coordinates and colors.
    Args:
        points (list) = The under-process points.
        labels (list) = The list of labels.
        label  (int)  = The under-process label.

    Returns:
        pout (list) = The coordinates of the points which are characterized by the under-process label value.
        cout (list) = The colors of the points which are characterized by the under-process label value.

    """
    pout = []
    cout = []
    indices = np.where(labels == label)
    colors = list(np.random.choice(range(256), size=3))
    for index in indices[0]:
        pout.append(points[index])
        cout.append(colors)
    return pout, cout


def read_txt_coordinates_to_list(path2folder: str = '', txtfilename: str = '', seperator: str = ' ',
                                 colour: bool = False):
    """
    This function reads the points' coordinates and colors from a .txt archive and adds them into a list.
    Args:
        path2folder (str)  = The path to the folder, contains the .txt archive.
        txtfilename (str)  = The name of the .txt archive.
        seperator   (str)  = The seperator i.e. "space", "," etc.
        colour      (bool) = If the point cloud contains the color information or not.

    Returns:
        points (list) = The points.
        colors (list) = The colors.

    """
    with open(f'{path2folder}/{txtfilename}') as txtfile:
        points = []
        colours = []
        for line in txtfile:
            coordinates = line.split(seperator)
            points.append([np.float64(coordinates[0]), np.float64(coordinates[1]), np.float64(coordinates[2])])
            if colour:
                colours.append([np.int(coordinates[6]), np.int(coordinates[7]), np.int(coordinates[8])])
    if colour:
        return points, colours
    else:
        return points


def txt2ply(txtfilename, plyfilename):
    """
    This function transforms the given .txt file to a .ply one.
    Args:
        txtfilename (str)  = The name of the .txt archive.
        plyfilename (str)  = The name of the .ply archive which will be saved.

    Returns:

    """
    txtobj = open(txtfilename, 'r')
    data = txtobj.read().splitlines()
    points_num = len(data)
    ply_header = f'ply\nformat ascii 1.0\nelement vertex {points_num}\nproperty float x\nproperty float y\nproperty float z\nproperty float nx\nproperty float ny\nproperty float nz\nproperty int red\nproperty int green\nproperty int blue\nproperty uchar label\nproperty uchar value\nend_header\n'
    plyobj = open(plyfilename, 'w')
    plyobj.write(ply_header)
    for line in data:
        plyobj.write(f'{line}\n')


def write_a_file(writing_path: str = '', filename: str = '', suffix: str = '', line: str = ''):
    """
    This function writes a new archive line by line.
    Args:
        writing_path (str)  = The path in which the file will be saved.
        filename (str)      = The name of the archive which will be saved into the writing_path.
        suffix (str)        = The saffix of the archive.
        line (str)          = The line which will be write into the produced archive.

    Returns:

    """
    filename = f'{writing_path}/{filename}{suffix}'
    with open(filename, 'a') as f:
        f.write(line)
    f.close()


def cleararchive(file):
    """
    This function clears an existing archive
    Args:
        file (str)  = The name of the file.

    Returns:

    """
    try:
        with open(file, 'w'):
            pass
    except FileNotFoundError:
        pass
