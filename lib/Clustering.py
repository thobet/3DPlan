"""

This program is part of the 3DPlan algorithm.
This program manipulates the clustering procedure of the 3DPlan software
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

from sklearn.cluster import DBSCAN
from skimage.measure import LineModelND, ransac
from lib.utils import *
from pathlib import Path
import numpy as np
import os

def dbscan(points, eps=0.001, min_samples=10):
    '''
    This function is inspired by skimage's implementation at: https://scikit-learn.org/stable/modules/clustering.html#overview-of-clustering-methods. (Accessed 20/11/2020)
    Firstly, finds the clusters via DBSCAN algorithm implementation. Then, executes the RANSAC algorithm to separates the inliers from the outliers.
    Args:
        points (numpy array) = The 3D calculate points i.e Point Cloud without the colors.
        eps (int/float)      = Circle's diameter.
        min_samples (int)    = Minimum points that will be accepted as a cluster.

    Returns:

    '''
    # Compute DBSCAN:
    db = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean').fit(points)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present:
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    message(f'Estimated number of clusters: {n_clusters_}')
    message(f'Estimated number of noise points: {n_noise_}')

    # Save points' coordinates with label linked to their cluster:
    cleararchive(f'{Path(os.getcwd())}/Lines/LinesLabels.txt')
    cleararchive(f'{Path(os.getcwd())}/Lines/noisepoints.txt')
    for i in range (0, len(labels)):
        if labels[i] != -1:
            line = f'{points[i][0]} {points[i][1]} {points[i][2]} {labels[i]}\n'
            write_a_file(f'{Path(os.getcwd())}/Lines', 'LinesLabels', '.txt', line)
        else:
            line = f'{points[i][0]} {points[i][1]} {points[i][2]} {labels[i]}\n'
            write_a_file(f'{Path(os.getcwd())}/Lines', 'noisepoints', '.txt', line)

    # Save each cluster as .ply archive, execute RANSAC algorithm and add the detected lines to 3DPlan.dxf:
    lines   = []
    for n in range (0, n_clusters_):
        pout, cout = points2clusters(points, labels, n)
        #export2ply(pout, cout, f'cluster{n}.ply')
        if len(pout) > 2:
            #cleararchive(f'{Path(os.getcwd())}/Lines/RANSAC{n}.txt')
            lpoints, params, line = rnsc(pout,  min_samples=2, residual_threshold=(eps-eps/10), max_trials=1000)
            #for point in lpoints:
                #line = f'{point[0]} {point[1]} {point[2]} {labels[i]}\n'
                #write_a_file(f'{Path(os.getcwd())}/Lines', f'RANSAC{n}', '.txt', line)
            lines.append(line)
        elif len(pout) == 2:
            lines.append([pout[0], pout[1]])
        else:
            continue
    
    message('Vectorization ...')
    lines2dxf(lines)


def rnsc(points, min_samples=2, residual_threshold=0.0009, max_trials=1000):
    '''
    This function implements the RANSAC algorithm.
    Args:
        points (numpy array)           = The 3D calculate points i.e Point Cloud without the colors.
        min_samples (int)              = Minimum points that will be accepted as a cluster.
        residual_threshold (int/float) = Maximum distances from the line in order to classify a point as inlier.
        max_trials (int)               = Maximum itteration of ransac algorithm.

    Returns:
        inliers_points (numpy array)   = The points that are classified as inliers.

    '''
    points = np.array(points, dtype=np.float)
    outliers_points = points
    model_robust, inliers = ransac(outliers_points, LineModelND, min_samples=min_samples, residual_threshold=residual_threshold, max_trials=max_trials)
    outliers = inliers == False
    inliers_points = outliers_points[inliers[:]]
    outliers_points = outliers_points[outliers][:]

    line = [inliers_points[0], inliers_points[-1]]

    return inliers_points, model_robust.params, line