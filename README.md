# 3DPlan


## Overview:
<dl>
    <dt>textAlign(str)</dt>
    <dd>
        <dl>
            <dt>justify</dt>
            <dd>The 3DPlan algorithm was developed during my diploma thesis, entitled "Automated detection of edges in point clouds using semantic information", 
at the School of Rural and Surveying Engineering of the National Technical University of Athens, which is available at https://dspace.lib.ntua.gr/xmlui/handle/123456789/53090.

At first the 3DPlan algorithm enrich the given images with a new channel including the edge semantic information. Thus
the three channel images (RGB) are transformed into four channel ones (RGBL).
Afterwards, the four channel images are inserted into a SfM-MVS software to produce initially a sparse and finally, a dense point cloud which is enriched with the
edge semantic information.</dd>
        </dl></dd>
</dl>

For this purpose three approaches were developed.
    1) Using the OpenSfM software which firstly was modified to manipulate four channel images.
    2) Using the Agisoft-Metashape software with its GUI.
    3) Using the Agisoft_Metashape software with the provided python module.

Then the points belonging to edges are firstly detected, into the semantically enriched point cloud and then classified into points of each edge. 
Finally, each segment of points is vectorized and thus, the approximated 3D plan of the object of interest is produced as "3DPlan.dxf".
</p>

## Dependencies:

numpy == 1.19.2<br>
opencv-python == 3.4.8.29<br>
dxf == 1.1.1<br>
pathlib == 1.0.1<br>
imutils == 0.5.3<br>
metashape == 0.0.4 (Optional for the approach numb. 3)<br>
Pillow == 7.0.0<br>
sklearn == 0.0<br>
scikit-image == 0.17.2<br>


## How to use:

The RGB images must be stored into "rgb" directory.

The semantic information channel, for each image, must be stored into "semantic_images" directory.

## License
3DPlan is GPL-3.0 licensed, as found in the LICENSE file.
