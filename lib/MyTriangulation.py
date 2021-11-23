"""

This program is part of the 3DPlan algorithm.
This program contains themanipulates the triangulation process (MyTriangulation) of the 3DPlan software.
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
import cv2 as cv
import os
from lib.utils import *
from lib import Geometry
import numpy as np
from pathlib import Path

from lib.config import default_config

config = default_config()


class Triang:
    """
        Name: Triang

        Description: Triang class manipulates the triangulation process.

        Parameters:
            capture: 'above' or 'front' , indicates if the image is aerial or not.
            suffix:  4D image format.

        Functions:
            --- Setters ---
            set_path:                      Set working directory.
            set_pairs:                     Set a pairs list.
            set_feature_extraction_method: Set different feature extraction method.
            set_capture:                   Set capture method.

            --- Getters ---
            get_path:                      Get the working directory.
            get_capture:                   Get the capture method.
            get_images:                    Get the images' arrays.
            get_imagesnames:               Get the images' names.
            get_feature_extraction_method: Get the feature extraction method.
            get_pairs:                     Get the used pairs.
            get_fundamental_matrix:        Get the fundamental matrix.
            get_essential_matrix:          Get the essential matrix.
            get_R:                         Get the rotation matrix.
            get_t:                         Get the translation matrix.
            get_projection_matrices:       Get pair's projection matrices (left image, right image)
            get_point_cloud:               Get the generated point cloud.

            --- Methods ---
            allimages:                     Manipulates the given RGB images using the Geometry script.
            allpairs:                      Finds all the available pairs i.e. for 3 images the pairs are (0, 1), (0, 2), (1, 2). (!This method needs a further improvmet (Computationally expensive)!).
            pairsmatching:                 Matches each pair and produces its sparse point cloud.
            flann:                         Flann matcher.
            calculate_fundamental_matrix:  Finds the fondumental matrix.
            calculate_essential_matrix:    Finds the essential matrix.
            Rt:                            Finds the rotation and translation matrix.
            projection_matrix_from_pose:   Finds the projection matrix using the image's pose and the camera_matrix.
            starting_projection_matrix:    Adds a 4th column of zeros into camera matrix.
            triangulate_points:            Calculates the homogeneous points applying the triangulation process.
            export_info:                   Exports each pair's point cloud (.txt).

    """

    def __init__(self, capture='front', suffix='.tiff'):
        """ Constructor """
        self.capture = capture
        self.path = Path(os.getcwd())
        self.imagesnames = find_files(f'{self.path}/images', suffix)
        self.images: list = []

        self.pairs: list = []

        self.feature_extraction_method = 'Akaze'

        # --- Pull the trigger ---
        message(f'Found {self.imagesnames} images')
        Triang.allimages(self)
        Triang.allpairs(self)

        for pair in self.pairs:
            self.pair = pair
            Triang.pairsmatching(self)

        # Fondumental Matrix:
        # Uncomment to use fundamental matrix i.e. When the intrinsic parameters are unknown
        '''
        message('Masking points with fundamental matrix and RANSAC algorithm ...')
        points_number_before_filtering = len(self.ptsL)
        Triang.calculate_fundamental_matrix(self)
        message(f'Remain {len(self.ptsL)} out of {points_number_before_filtering}')
        '''

        # Essential Matrix:
        # Comment the essential matrix calculation, to use fundamental matrix i.e. When the intrinsic parameters are unknown     
        message('Masking points with essential matrix ...')
        points_number_before_filtering = len(self.ptsL)
        Triang.calculate_essential_matrix(self)
        message(f'Remain {len(self.ptsL)} out of {points_number_before_filtering}')

        # Rotation and Translation matrix:
        message('Calculating Rotation and Translation matrix ...')
        points_number_before_filtering = len(self.ptsL)
        Triang.Rt(self)
        message(f'Remain {len(self.ptsL)} out of {points_number_before_filtering}')

        # Projection matrix:
        message('Calculating Projection matrices ...')
        Triang.projection_matrix_from_pose(self)
        Triang.starting_projection_matrix(self)

        # Triangulation matrix:
        message('Calculating 3D Points ...')
        Triang.triangulate_points(self)

        # Save the generated point cloud:
        message('Save Sparse Point Cloud ...')
        Triang.export_info(self)

        print('-' * 200 + '\n')

    # --- Setters ---
    def set_path(self, path):
        self.path = path

    def set_pairs(self, pairs):
        self.pairs = pairs

    def set_feature_extraction_method(self, feature_extraction_method):
        self.feature_extraction_method = feature_extraction_method

    def set_capture(self, capture):
        self.capture = capture

    # --- Getters ---
    def get_path(self):
        return self.path

    def get_capture(self):
        return self.capture

    def get_images(self):
        return self.images

    def get_imagesnames(self):
        return self.imagesnames

    def get_feature_extraction_method(self):
        return self.feature_extraction_method

    def get_path(self):
        return self.path

    def get_pairs(self):
        return self.pairs

    def get_fundamental_matrix(self):
        return self.fundamental_matrix

    def get_essential_matrix(self):
        return self.essential_matrix

    def get_R(self):
        return self.R

    def get_t(self):
        return self.t

    def get_projection_matrices(self):
        return self.left_projection_matrix, self.right_projection_matrix

    def get_point_cloud(self):
        return self.points3d

    # --- Methods ---
    def allimages(self):
        """
            Manipulates the given RGB images using the Geometry script.

            args:
                imagesnames (str): Images' names.
        """
        for imagename in self.imagesnames:
            image = Geometry.Image(imagename, self.feature_extraction_method)
            image.imgid = self.imagesnames.index(imagename)
            self.images.append(image)

    def allpairs(self):
        """Finds all the available pairs i.e. for 3 images the pairs are (0, 1), (0, 2), (1, 2)."""
        for i in range(0, len(self.images)):
            for j in range(i + 1, len(self.images)):
                # print (self.images[i].imgid, self.images[j].imgid)
                pair = [self.images[i].imgid, self.images[j].imgid]
                self.pairs.append(pair)

    def pairsmatching(self):
        """Matches pair's images and produces the sparse point cloud."""
        # --- Get pair's info ---
        self.labels = self.images[self.pair[0]].lchannel
        self.leftimage = self.images[self.pair[0]]
        self.rightimage = self.images[self.pair[1]]
        self.camera_matrix = self.leftimage.camera_matrix

        self.colours = []

        self.Lkp = self.leftimage.points
        self.Rkp = self.rightimage.points

        self.LDesc = np.array(self.leftimage.descriptors, dtype=np.float32)
        self.RDesc = np.array(self.rightimage.descriptors, dtype=np.float32)

        # --- Matching Variables ---
        self.matching_method = 'FLANN'

        self.ptsL: list = []
        self.ptsR: list = []
        self.idsL: list = []

        self.good_matches: list = []

        self.fundamental_matrix: list = []
        self.essential_matrix: list = []

        self.R: list = []
        self.t: list = []

        self.left_projection_matrix: list = []
        self.right_projection_matrix: list = []

        self.triangulated_points: list = []
        self.triangulated_pointsT: list = []

        self.labeled_points: list = []

        # --- Pull the triger ---
        if self.matching_method == 'FLANN':
            Triang.flann(self)
        else:
            print(f'Method: {self.matching_method} is not available')

    def flann(self):
        """ This function applies the Flann matcher."""
        message(f'Matching image with id = {self.pair[0]} with image with id = {self.pair[1]}')

        FLANN_INDEX_KDTREE = 1
        # FLANN_INDEX_LSH = 6
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)  # Set index_param (matching parameter).
        # index_params = dict(algorithm = FLANN_INDEX_LSH, table_number = 10, key_size = 20, multi_probe_level = 0).
        search_params = dict(checks=50)  # Set search_param (matching parameter).
        flann = cv.FlannBasedMatcher(index_params, search_params)  # Set the matcher.

        matches = flann.knnMatch(self.LDesc, self.RDesc, k=2)

        if self.feature_extraction_method == 'Sift' or self.feature_extraction_method == 'ORB' or self.feature_extraction_method == 'Surf':
            colouring_points = self.Lkp  # Store the key_points before convert them to cvkeypoints.
            self.Lkp = convert_points_2_cvkeypoints(self.Lkp)  # Convert the feature points to cvkeypoints.
            self.Rkp = convert_points_2_cvkeypoints(self.Rkp)  # Convert the feature points to cvkeypoints.
        else:
            colouring_points = [i.pt for i in self.Lkp]

        message('Apply Lowe\'s paper ratio test')

        lowes_ratio = float(config['lowes_ratio'])

        # Lowe's ratio:
        for i, (m, n) in enumerate(matches):
            if m.distance < lowes_ratio * n.distance:
                self.good_matches.append(m)
                self.ptsR.append(self.Rkp[m.trainIdx].pt)  # Store the index of kp2.
                self.ptsL.append(self.Lkp[m.queryIdx].pt)  # Store the index of kp1.
                self.idsL.append(i)

        message(f'Found {len(self.good_matches)} good matches in pair {self.pair} out of {len(matches)}')

        colours = []
        img = self.images[self.pair[0]].array  # Set image for colouring.
        for i in self.idsL:
            y = int(colouring_points[i][0])  # Get y index for colouring.
            x = int(colouring_points[i][1])  # Get x index for colouring.

            red = img[x, y, 2]  # Get red channel.
            green = img[x, y, 1]
            blue = img[x, y, 0]
            label = img[x, y, 3]

            colours.append(
                [red, green, blue, label])  # Append to the colours' list the colours as well as the associated labels.

        self.colours = np.array(colours, dtype=np.int)  # Convert colours to np.array.

    def calculate_fundamental_matrix(self):
        """This function calculats the fundamental matrix"""
        self.ptsL = np.int32(self.ptsL)  # Convert pts1 to int for the fundamental calculation.
        self.ptsR = np.int32(self.ptsR)

        self.fundamental_matrix, mask = cv.findFundamentalMat(self.ptsL, self.ptsR,
                                                              cv.FM_LMEDS)  # Calculate fundametnal matrix (Unknown camera intrinsics parameters).

        self.ptsL = self.ptsL[
            mask.ravel() == 1]  # Keep only the points which are used for the fundametnal matrix calculation.
        self.ptsR = self.ptsR[mask.ravel() == 1]
        self.colours = self.colours[
            mask.ravel() == 1]  # Keep only the colours and the labels from points which are used for the fundametnal matrix calculation.

    def calculate_essential_matrix(self):
        """This function calculats the essential matrix"""
        self.ptsL = np.int32(self.ptsL)  # Convert ptsL to int for the fundamental calculation.
        self.ptsR = np.int32(self.ptsR)

        self.essential_matrix, mask = cv.findEssentialMat(self.ptsL, self.ptsR, self.camera_matrix,
                                                          cv.LMEDS)  # Calculate essential matrix (Known camera intrinsics parameters).

        self.ptsL = self.ptsL[
            mask.ravel() == 1]  # Keep only the points which are used for the essential matrix calculation.
        self.ptsR = self.ptsR[mask.ravel() == 1]
        self.colours = self.colours[
            mask.ravel() == 1]  # Keep only the colours and the labels of points which are used for the essential matrix calculation.

    def Rt(self):
        """This function finds the rotation matrix R and the translation matrix t using corresponding points and a given camera matrix."""
        pts_1 = np.array(self.ptsL, dtype=np.float)  # Convert points to float
        pts_2 = np.array(self.ptsR, dtype=np.float)
        if self.essential_matrix != []:
            poseval, self.R, self.t, mask = cv.recoverPose(self.essential_matrix, pts_1, pts_2, self.camera_matrix,
                                                           0.4)  # Find image's pose using corresponding points, the essential matrix, the camera matrix and a ratio.
        else:
            poseval, self.R, self.t, mask = cv.recoverPose(self.fundamental_matrix, pts_1, pts_2, self.camera_matrix,
                                                           0.4)
        self.ptsL = self.ptsL[
            mask.ravel() == 255]  # Keep only the points which are used for the pose recover procedure.
        self.ptsR = self.ptsR[mask.ravel() == 255]
        self.colours = self.colours[
            mask.ravel() == 255]  # Keep only the colours of points which are used for the pose recover calculation.

    def projection_matrix_from_pose(self):
        """
        This function computes the projection matrix using the translation and rotation matrix.
        """
        Rt = np.transpose(self.R)
        Rtt = np.matmul(-Rt, self.t)
        P_t = [Rt, Rtt]
        P_t = np.concatenate(P_t, axis=1)
        self.left_projection_matrix = np.matmul(np.array(self.camera_matrix),
                                                P_t)  # Calculate projection matrix from pose.

    def starting_projection_matrix(self):
        """
        This function adds a 4th column of zeros, to the camera matrix.
        """
        zeroMtrx = [[0], [0], [0]]
        self.right_projection_matrix.append(self.camera_matrix)
        self.right_projection_matrix.append(zeroMtrx)
        self.right_projection_matrix = np.concatenate(self.right_projection_matrix,
                                                      axis=1)  # Set the start projection matrix.

    def triangulate_points(self):
        """
        This function compute 4D points via 2D image detected points and the projection matrix.
        """
        ptsLT = np.transpose(self.ptsL)  # Find the transpose of list pts1
        ptsRT = np.transpose(self.ptsR)  # Find the transpose of list pts2

        ptsLT = np.array(ptsLT, dtype=np.float)
        ptsRT = np.array(ptsRT, dtype=np.float)

        self.triangulated_points = cv.triangulatePoints(np.array(self.right_projection_matrix),
                                                        np.array(self.left_projection_matrix), ptsRT,
                                                        ptsLT)  # Calculate 4D points (x, y, z, w) from triangulation
        self.triangulated_pointsT = np.transpose(
            self.triangulated_points)  # Find the transpose of triangulated points list

    def export_info(self):
        """ This finction exports the generated point cloud into ./PointClouds folder"""
        mkdir('Lines')
        points3d = []
        i = -1
        path = f'{os.getcwd()}/Lines'
        for point in np.array(self.triangulated_pointsT):
            i += 1
            if self.capture == 'above':
                x = point[0] / point[3]
                y = point[1] / point[3]
                z = (point[2] / point[3]) * 100

            elif self.capture == 'front':
                x = -point[0] / point[3]
                y = point[2] / point[3] * 100
                z = (point[1] / point[3])

                if x > 10 or y > 10:
                    continue
            else:
                error_message('The capture variable must be above or front', sysex=True)

            point3d = [x, y, z]
            points3d.append(point3d)

            wline = f'{point3d[0]} {point3d[1]} {point3d[2]} {self.colours[i][0]} {self.colours[i][1]} {self.colours[i][2]} {self.colours[i][3]}\n'
            write_a_file(path, f'{self.leftimage.imgid}{self.rightimage.imgid}', '.txt', wline)
            write_a_file(path, 'merged', '.txt', wline)

            if self.colours[i][3] == 255:
                wline = f'{point3d[0]} {point3d[1]} {point3d[2]} {self.colours[i][0]} {self.colours[i][1]} {self.colours[i][2]} {self.colours[i][3]}\n'
                if len(self.pairs) == 1:
                    write_a_file(path, 'edges', '.txt', wline)
                else:
                    write_a_file(path, f'{self.leftimage.imgid}{self.rightimage.imgid}_labeled', '.txt', wline)

                self.labeled_points.append(point3d)

        self.points3d = np.array(points3d)
