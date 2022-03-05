"""

This program is part of the 3DPlan algorithm.
This program constructs the images i.e. 4 channel images, which are used into SfM-MVS workflow.
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

from pathlib import Path

import cv2
import imutils
import numpy as np

from lib.utils import mkdir, error_message

edge_parameters = {'minimum': 200, 'maximum': 300}
gray = None


class SFMImage:
    """
        Name SFMImage

        Description: SFMImage class constructs the images i.e. 4 channel images, which are used into SfM-MVS workflow.

        Parameters:
            path:                    Pass into the class the working directory.
            imname:                  Pass into the class image's name.
            simages:                 Pass into the class semantic image's name.
            out:                     Pass into the class the number of the channels of the output image (3 or 4)
            bluremethod:             Pass into the class the chosen blured method.
            edgemethod:              Pass into the class the edge detection technique.

        Functions:
            --- Setters ---
            set_path:                Set the working directory.
            set_edgemethod:          Set the edgemethod.
            set_kernel:              Set the kernel's, which is used to blure the image, size.
            set_blurmethod:          Set the blured method.

            --- Getters ---
            get_path:                Get the working directory.
            get_image:               Get the image.
            get_edgemethod:          Get the edge extraction method.
            get_kernel:              Get the kernel's, which is used to blure the image, size.
            get_blurmethod:          Get the blured method.
            get_bluredim:            Get the blured image.
            get_labels:              Get the labels.

            --- Methods ---
            save_blur_image:         Saves the blurred image.
            save_labels:             Saves the label channel.
            add_channel:             Adds to each image the label channel.
            save_output_image:       Saves the output image.
            define_labels:           Constructs the channel which will be added as the label channel.
            semiauto_edge_detection: Semi automatic Canny implementation i.e. Canny with image viewer.
            define_min:              Defines starting Canny min value.
            define_max:              Defines starting Canny max value.
            new_value:               Updates min and max values using user's input.
            find_edges:              Executes locally the Canny algorithm and visualize the results.

            The live Canny viewer implementation was inspired by Arapelis (Arapellis, O. 2020. Semiautomated edge detection on digital images. Postgraduate Degree Thesis, Postgraduate Course in Geoinformatics, NTUA (in Greek))
    """

    def __init__(self, path: str = '', imname: str = '', simages: bool = False, out='4D', blurmethod='',
                 edgemethod='Canny'):
        # --- Image Variables ---
        self.imname = imname
        self.out = out
        self.path = Path(path)
        self.image = cv2.imread(f'{self.path}/rgb/{imname}', cv2.IMREAD_UNCHANGED)
        self.shape = self.image.shape
        self.blue = self.image[:, :, 0]
        self.green = self.image[:, :, 1]
        self.red = self.image[:, :, 2]
        self.edgemethod = edgemethod

        # --- Set Labels Variables if semantic image exists---
        if simages:
            self.siname = f'{self.imname[:-4]}_l.jpg'
            self.simage = cv2.imread(f'{self.path}/semantic_images/{self.siname}', cv2.IMREAD_UNCHANGED)
            if len(self.simage.shape) == 3:
                if self.simage.shape[2] == 3:
                    self.tchl = True
                    self.sblue = self.simage[:, :, 0]
                    self.sgreen = self.simage[:, :, 1]
                    self.sred = self.simage[:, :, 2]
                else:
                    error_message('Please use a 1 channel or 3 channels annotated image', sysex=True)
            else:
                self.tchl = False

        # --- Blur Variables ---
        self.kernel = (51, 51)
        self.blurmethod = blurmethod
        if self.blurmethod == 'GaussianBlur' and self.edgemethod == 'Canny':
            self.bluredim = cv2.GaussianBlur(self.image, self.kernel, 0)
            self.bluredimname = f'{self.imname[:-4]}_b.jpg'

        # --- Set labels Variables ---
        if edgemethod == 'Canny':

            # --- Canny Parameters ---
            global edge_parameters, gray
            SFMImage.semiauto_edge_detection(self)
            '''
            min_val = edge_parameters['minimum']
            max_val = edge_parameters['maximum']
            '''
            if self.blurmethod != '':
                self.gray = cv2.cvtColor(self.bluredim, cv2.COLOR_BGR2GRAY)
            else:
                self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

            # self.labels = cv2.Canny(self.gray, min_val, max_val, 3)

        elif edgemethod == 'Sematic_Info':
            self.labels = np.zeros_like(self.red, dtype=np.int)

        self.sfmchannels = np.zeros_like(self.image)
        self.sfmlname = f'{self.imname[:-4]}_l.jpg'

        # --- Output Image ---
        if out == '4D':
            self.outname = f'{self.imname[:-4]}.tiff'
        else:
            self.outname = f'{self.imname[:-4]}.JPG'

        self.outim: list = []

        # --- Pull the trigger ---
        if edgemethod == 'Canny':
            # SFMImage.save_blur_image(self)
            SFMImage.save_labels(self)

        elif edgemethod == 'Sematic_Info':
            SFMImage.define_labels(self)
            # SFMImage.save_labels(self)

        SFMImage.add_channel(self)
        SFMImage.save_output_image(self)

    # --- Setters ---
    def set_path(self, path):
        self.path = path

    def set_edgemethod(self, edgemethod):
        self.edgemethod = edgemethod

    def set_kernel(self, kernel):
        self.kernel = kernel

    def set_blurmethod(self, blurmethod):
        self.blurmethod = blurmethod

    # --- Getters ---
    def get_path(self):
        return self.path

    def get_image(self):
        return self.image

    def get_edgemethod(self):
        return self.edgemethod

    def get_kernel(self):
        return self.kernel

    def get_blurmethod(self):
        return self.blurmethod

    def get_bluredim(self):
        return self.bluredim

    def get_labels(self):
        return self.labels

    # --- Methods ---
    def save_blur_image(self):
        """This function saves the blurred image"""
        mkdir('Blur_rgb')
        cv2.imwrite(f'{self.path}/Blur_rgb/{self.bluredimname}', self.bluredim)

    def save_labels(self):
        """This function saves the label channel"""
        mkdir('Labels')
        cv2.imwrite(f'{self.path}/Labels/{self.sfmlname[:-4]}.tiff', self.labels)

    def add_channel(self):
        """This function adds to the image the label channel"""
        if self.out == '4D':
            self.outim = cv2.merge((self.blue, self.green, self.red, self.labels))
        elif self.out == '3D':
            self.outim = cv2.merge((self.blue, self.green, self.labels))

    def save_output_image(self):
        """This function saves th output image"""
        mkdir('images')
        cv2.imwrite(f'{self.path}/images/{self.outname}', self.outim)

    def define_labels(self):
        """This function constructs the channel which will be added as the label channel"""
        if self.tchl:
            self.labels = np.zeros_like(self.red)
            for i in range(0, self.sred.shape[0]):
                for j in range(0, self.sred.shape[1]):
                    r = self.sred[i, j]
                    # g = self.sgreen[i, j] #Uncomment if the semantic information is in green color
                    # b = self.sblue[i, j] #Uncomment if the semantic information is in blue color
                    if r > 253:
                        self.labels[i, j] = 255
            SFMImage.save_labels(self)  # Uncomment for debugging
        else:
            self.labels = self.simage

    def semiauto_edge_detection(self):
        """This function semi automatic Canny implementation i.e. Canny with image viewer"""
        global edge_parameters, gray
        image = imutils.resize(self.image, height=self.shape[1] // 10)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.namedWindow('MyImage')
        cv2.createTrackbar('Min', 'MyImage', edge_parameters['minimum'], 1200, SFMImage.define_min)
        cv2.createTrackbar('Max', 'MyImage', edge_parameters['maximum'], 1200, SFMImage.define_max)
        cv2.imshow('MyImage', gray)
        SFMImage.find_edges()
        while True:
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.labels = cv2.resize(edges, (self.shape[1], self.shape[0]))
                cv2.destroyAllWindows()
                break

    @staticmethod
    def define_min(new_min):
        """This function defines starting Canny min value"""
        SFMImage.new_value('minimum', new_min)

    @staticmethod
    def define_max(new_max):
        """This function defines starting Canny max value."""
        SFMImage.new_value('maximum', new_max)

    @staticmethod
    def new_value(parameter, new_value):
        """This function updates min and max values using user's input."""
        global edge_parameters
        edge_parameters[parameter] = new_value
        SFMImage.find_edges()

    @staticmethod
    def find_edges():
        """This function executes locally the Canny algorithm and visualize the results"""
        global edge_parameters, gray, edges
        edges = cv2.Canny(gray, edge_parameters['minimum'], edge_parameters['maximum'], 3)
        cv2.imshow('Edges', imutils.resize(edges, edges.shape[1]))
