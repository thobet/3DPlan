"""

This program is part of the 3DPlan algorithm.
This program calculates image's camera matrix and extracts image's feature points.
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


***The feature extraction methods impelementation, they are similar to OpenSfM sofware (https://github.com/mapillary/OpenSfM/blob/master/opensfm/features.py)***
***The configuration file (lib.config) is the OpenSfM's one.***

"""

import numpy as np
import PIL
from lib.utils import message
import cv2 as cv
from PIL import ExifTags, Image

from lib.config import default_config

config = default_config()


class Image:
    """
        Name: Image

        Description: Image class: 1) Calculates image's camera matrix.
                                  2) Extracts image's feature points.

        Functions:
            --- Setters ---
            set_imagename:                 Set image's name.
            set_focal:                     Set focal length (mm).
            set_width:                     Set image's width.
            set_height:                    Set image's height.
            set_camera_model:              Set camera's model.
            set_principal_point:           Set image's principal point.
            set_camera_matrix:             Set image's camera matrix.
            set_feature_extraction_method: Set different feature extraction method.

            --- Getters ---
            get_array:                     Get image's channels.
            get_imagename:                 Get image's name.
            get_imgid:                     Get image's id.
            get_focal:                     Get focal length.
            get_width:                     Get image's width.
            get_height:                    Get image's height.
            get_camera_model:              Get camera's model.
            get_principal_point:           Get image's principal point.
            get_camera_matrix:             Get the camera matrix.
            get_feature_extraction_method: Get the feature extraction method (Akaze, Sift, Surf, ORB).

            --- Methods ---
            image_exif:                    Extracts image's metadata.
            camera_matrix:                 Calculates image's camera matrix.
            akaze:                         Extracts image's features using Akaze algorithm.
            sift:                          Extracts image's features using Sift algorithm.
            surf:                          Extracts image's features using Surf algorithm.
            orb:                           Extracts image's features using ORB algorithm.
            save_label_channel:            Saves image's 4th channel i.e. labels.

            The feature extraction methods impelementation, they are similar to OpenSfM sofware (https://github.com/mapillary/OpenSfM/blob/master/opensfm/features.py)
            The configuration file (lib.config) is the OpenSfM's one.
    """

    def __init__(self, imgname, method):
        """Constructor"""
        self.array = cv.imread(f'./images/{imgname}', cv.IMREAD_UNCHANGED)
        self.imagename = imgname
        self.imgid: int = 0

        self.focal: int = 0
        self.width: int = 0
        self.height: int = 0
        self.camera_model: str = ''

        self.lchannel: list = []

        # --- Feature Extraction Variables ---
        self.feature_extraction_method = method
        self.points: list = []
        self.descriptors: list = []
        self.color: list = []

        # --- Camera Matrix Variables ---
        self.principal_point: list = []
        self.camera_matrix: list = []

        # --- Pull the trigger ---
        Image.camera_matrix()

        if method == 'Akaze':
            Image.akaze()

        if method == 'Sift':
            Image.sift()

        if method == 'Surf':
            Image.surf()

        if method == 'ORB':
            Image.orb()

    # --- Setters ---
    def set_imagename(self, name):
        self.imagename = name

    def set_focal(self, focal):
        self.focal = focal

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_camera_model(self, camera_model):
        self.camera_model = camera_model

    def set_principal_point(self, principal_point):
        self.principal_point = principal_point

    def set_camera_matrix(self, camera_matrix):
        self.camera_matrix = camera_matrix

    def set_feature_extraction_method(self, method):
        self.feature_extraction_method = method

    # --- Getters ---
    def get_array(self):
        return self.array

    def get_imagename(self):
        return self.imagename

    def get_imgid(self):
        return self.imgid

    def get_focal(self):
        return self.focal

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_camera_model(self):
        return self.camera_model

    def get_principal_point(self):
        return self.principal_point

    def get_camera_matrix(self):
        return self.camera_matrix

    def get_feature_extraction_method(self):
        return self.feature_extraction_method

    # --- Methods ---
    def image_exif(self, suffix):
        """
            This function extracts image's metadata.

            args:
                suffix (str): 3 channel image's suffix i.e. (.JPG, .jpg, .tif etc.)
        """
        image = PIL.Image.open(f'./rgb/{self.imagename[:-5]}{suffix}')

        exif = {ExifTags.TAGS[k]: v for k, v in image._getexif().items() if k in ExifTags.TAGS}

        # print (exif)
        self.focal = [exif.get('FocalLength')][0][0]
        self.width = [exif.get('ExifImageWidth')][0]
        self.height = [exif.get('ExifImageHeight')][0]
        self.camera_model = exif.get('Model ')

        if self.camera_model == 'Canon EOS 6D':
            self.principal_point = [2756, 1774]
        else:
            if self.width > self.height:
                self.principal_point = [self.width / 2,
                                        self.height / 2]  # Sets principal point as the central pixel (Approximation)
            elif self.width < self.height:
                self.principal_point = [self.height / 2, self.width / 2]

    def camera_matrix(self):
        """Calculates the camera matrix"""
        Image.image_exif('.JPG')

        camera_matrix = [[self.focal, 0, self.principal_point[0]],
                         [0, self.focal, self.principal_point[1]],
                         [0, 0, 1]]

        self.camera_matrix = np.array(camera_matrix)

    def akaze(self):
        """Implements the AKAZE algorithm"""
        method = cv.AKAZE_create()

        self.points, self.descriptors = method.detectAndCompute(self.array, None)

        message(f'Found {len(self.points)} key points on image {self.imagename} using Akaze method')

        pts = [self.points[idx].pt for idx in range(0, len(self.points))]
        pts = np.array(pts)

        xs = pts[:, 0].round().astype(int)
        ys = pts[:, 1].round().astype(int)
        color = self.array[ys, xs]
        self.color = np.array(color)

    def sift(self):
        """Implements the Sift algorithm"""
        sift_edge_threshold = config['sift_edge_threshold']
        sift_peak_threshold = float(config['sift_peak_threshold'])

        try:
            detector = cv.xfeatures2d.SIFT_create(edgeThreshold=sift_edge_threshold,
                                                  contrastThreshold=sift_peak_threshold)
        except AttributeError:
            print('OpenCV Contrib modules are required to extract SIFT features')
            raise

        descriptor = detector
        detector = cv.xfeatures2d.SIFT_create()

        points = detector.detect(self.array)
        self.points, self.descriptors = descriptor.compute(self.array, points)
        message(f'Found {len(points)} key points on image {self.imagename} using sift method')
        self.points = np.array([(i.pt[0], i.pt[1], i.size, i.angle) for i in self.points])

        xs = self.points[:, 0].round().astype(int)
        ys = self.points[:, 1].round().astype(int)
        color = self.array[ys, xs]
        self.color = np.array(color)

    def surf(self):
        """Implements the SURF feature extraction algorithm"""
        surf_hessian_threshold = config['surf_hessian_threshold']

        try:
            detector = cv.xfeatures2d.SURF_create()
        except AttributeError:
            message('OpenCV Contrib modules are required to extract surf features')
            raise

        descriptor = detector
        detector.setHessianThreshold(surf_hessian_threshold)
        detector.setNOctaves(config['surf_n_octaves'])
        detector.setNOctaveLayers(config['surf_n_octavelayers'])
        detector.setUpright(config['surf_upright'])
        detector.setHessianThreshold(surf_hessian_threshold)

        points = detector.detect(self.array)

        self.points, self.descriptors = descriptor.compute(self.array, points)
        message(f'Found {len(self.points)} key points on image {self.imagename} using surf method')
        self.points = np.array([(i.pt[0], i.pt[1], i.size, i.angle) for i in self.points])

        xs = self.points[:, 0].round().astype(int)
        ys = self.points[:, 1].round().astype(int)
        self.color = self.array[ys, xs]

    def orb(self):
        """Implements the ORB feature extraction algorithm"""
        detector = cv.ORB_create(nfeatures=int(config['feature_min_frames']))
        descriptor = detector

        points = detector.detect(self.array)

        self.points, self.descriptors = descriptor.compute(self.array, points)
        message(f'Found {len(self.points)} key points on image {self.imagename} using orb method')
        self.points = np.array([(i.pt[0], i.pt[1], i.size, i.angle) for i in self.points])

        xs = self.points[:, 0].round().astype(int)
        ys = self.points[:, 1].round().astype(int)
        self.color = self.array[ys, xs]

    def save_label_channel(self):
        """Saves image's 4th channel i.e. labels"""
        cv.imwrite(f'{self.imagename}label.jpg', self.lchannel)
