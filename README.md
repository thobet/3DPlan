# 3DPlan

                                           *** The README file is under processing ... ***
## Overview
<pre>
<p>The 3DPlan algorithm was developed during my diploma thesis, entitled "Automated detection of edges in point clouds using<br>
semantic information", at the School of Rural and Surveying Engineering of the National Technical University of Athens,<br>
which is available at <a href="https://dspace.lib.ntua.gr/xmlui/handle/123456789/53090">ThodorisBetsas_DiplomaThesis</a>.<br>
At first, the 3DPlan algorithm enriches the given images with a new channel including the edge semantic information.<br>
Thus the three-channel images (RGB) are transformed into four-channel (RGBL). Afterwards, the four-channel images are<br>
inserted into an SfM-MVS software to produce initially a sparse and finally, a dense point cloud which is enriched with the<br>
edge semantic information.</p>

For this purpose, three approaches were developed.
    1) Using the OpenSfM software which was firstly modified to manipulate four-channel images. 
    2) Using the Agisoft-Metashape software with its GUI. 
    3) Using the Agisoft_Metashape software with the provided python module.

Then the points belonging to edges are firstly detected, into the semantically enriched point cloud and then classified into 
points of each edge. Finally, each segment of points is vectorized and thus, the approximated 3D plan of the object of interest 
is produced as "3DPlan.dxf".
</pre>

## Dependencies
numpy == 1.19.2 <br>
opencv-python == 3.4.8.29 <br>
dxf == 1.1.1 <br>
pathlib == 1.0.1 <br>
imutils == 0.5.3 <br>
metashape == 0.0.4 (Optional for the approach numb. 3) <br>
Pillow == 7.0.0 <br>
sklearn == 0.0 <br>
scikit-image == 0.17.2 <br>

## How to use
<pre>
1) Clone/Download the 3DPlan master.
2) Add the RGB images into "rgb" directory.
3) Edge semantic information.
    3.1) Available:
        Add the semantic channel i.e., 1D image, for each image, into "semantic_images" directory.
        The semantic channels must be named as "rgbimagename_l.jpg"
        For example: RGB image --> 4G0R6560.JPG
                       semantic channel --> 4G0R6560_l.jpg
    3.2) Not available:
        The 3DPlan algorithm contains a live-implementation of the Canny algorithm which could be used for producing
        the edge semantic information.
        The live-editor begins and the user modifies Canny's parameters. When the user is satisfied by the detected
        edges, he presses the Q button to terminate the editing procedure.
        Then the 4D image is produced automatically and saved into "images" directory which is created automatically.
        This procedure is executed for each RGB image.
        (Nothing to do right now, go to step 4)
4) Execute the "3DPlan.py".
</pre>

## During the execution
<pre>
(Question 1) DD:MM:YY Hr:Mins:Sec, 3D (0) or 4D (1) output? (Write 0 or 1): The recommended answer is "1".
(Question 2) DD:MM:YY Hr:Mins:Sec, Agisoft-Metashape (0), Mapillary-OpenSFM (1) or MyTriangulation (2)? (Write 0, 1 or 2):
        Select the answer depending the SfM-MVS algorithm that you want to use. The recommended answer is "0".
        If "0":
            (Question 2.1) DD:MM:YY Hr:Mins:Sec, Python Module (0) or GUI (1) output? (Write 0 or 1):
                Select how you will apply the Agisoft-Metashape pipeline. 
                The python-module choice executes the pipeline automatically.
                On the other hand the GUI option waits for the user to run the algorithm using the Agisoft-Metashape graphical user interface. 
                When the dense point cloud is produced the user must save it into the "Lines" directory, which is produced 
                automatically, as "merged.txt".
(Question 3) DD:MM:YY Hr:Mins:Sec, Canny (0) or external semantic information (1)? (Write 0 or 1):
        If the edge semantic information is not available the user should select the "Canny" choice i.e., write 0 and press "enter".
        Then the 3.2 step (How to use) is executed.
        If the edge semantic information is available the user should select the "semantic information" choice i.e., write 1 and press "enter".
        (! Notice !) Look the step 3.1 (How to use).
(Question 4) DD:MM:YY Hr:Mins:Sec, Give the available image format:
        The user should write the images format, which are stored into "rgb" directory, for example .JPG and the to press "enter".
        The valid answers are '.JPG', '.jpg', '.TIFF', '.tiff', '.tif', '.PNG', '.png'.

The 3DPlan algorithm is executed according to the answers of the user and the 3DPlan.dxf archive is produced into the "Lines" directory.
</pre>

## Examples

Line detection using manually annotateed images and the Agisoft-Metashape software.
The two images which were inserted into the "rgb" directory:<br>
![6621](https://user-images.githubusercontent.com/45883362/113516175-79b29a80-9581-11eb-91f0-8a86fdbb2395.png) <br>
![6622](https://user-images.githubusercontent.com/45883362/113516179-7e774e80-9581-11eb-9518-58453fb3889c.png)

Two manually annotated images which were used for this implementation:<br>
![6621_l2](https://user-images.githubusercontent.com/45883362/113516000-93071700-9580-11eb-88b0-40e23dfd56fc.png)<br>
![6622_l2](https://user-images.githubusercontent.com/45883362/113516003-98646180-9580-11eb-9616-7ea138bbc8f8.png)

Two masks were produced using the manually annotated images. Then the 4D images were created and fed into the SfM-MVS algorithm.

The produced point cloud is visualized using the RGB colors and the labels.<br>
![rgb](https://user-images.githubusercontent.com/45883362/113516906-994bc200-9585-11eb-8b2d-2580c15ad21a.png)<br>
![labels](https://user-images.githubusercontent.com/45883362/113516909-9b158580-9585-11eb-9c53-83b518e25b09.png)

Additionally the detected and vectorized edges are displayed.<br>
![edge](https://user-images.githubusercontent.com/45883362/113517678-2bee6000-958a-11eb-8ba6-7068b5534f71.png)
![TwoLinesVectors](https://user-images.githubusercontent.com/45883362/113517001-1414dd00-9586-11eb-8519-7998a851b1cf.png)

A close view of the vectorized line in combination with the rgb dense point cloud.<br>
![vector_rgb](https://user-images.githubusercontent.com/45883362/113516925-acf72880-9585-11eb-8b92-92d82d335d49.png) <br>

## License
3DPlan is GPL-3.0 licensed, as found in the LICENSE file.
