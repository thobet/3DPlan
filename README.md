# 3DPlan

## Overview

The 3DPlan algorithm was developed during my diploma thesis at the School of Rural and Surveying Engineering of the National Technical University of Athens, 
entitled "Automated detection of edges in point clouds using semantic information", which is available at https://dspace.lib.ntua.gr/xmlui/handle/123456789/53090.

At first the 3DPlan algorithm enrich the given images with a new channel including the edge semantic information. Thus
the three channel images (RGB) are transformed into four channel images (RGBL).
Afterwards, the four channel images are inserted into a SfM-MVS software to produce initially a sparse and finally, a dense point cloud.

For this purpose three approaches were developed.
    1) Using the OpenSfM software which firstly was modified to manipulate four channel images.
    2) Using the Agisoft-Metashape software with its GUI.
    3) Using the Agisoft_Metashape software with the provided python module.

Using one of the proposed approaches a semantically enriched point cloud is produced.
Then the points belonging to edges are extracted and classified into points of each edge. 
Finally, each segment of points is vectorized and thus, the approximated 3D plan of the object of interest is produced.

The RGB images must be stored into "rgb" directory.

The semantic information channel, for each image, must be stored into "semantic_images" directory.
