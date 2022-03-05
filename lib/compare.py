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


This program is used to evaluate the enrichment of the RGB images with the label channels.
First enabling the saving function of the labels, into the 3DPlan algorithm (SemanticPass.py, "save_labels" function).
Then copy the labels, the four-channel images and the compare.py script, into a new directory.
Run the script.

"""

import cv2, os


directory = os.listdir()
allimages = []
for name in directory:
    if name[-5:] == ".tiff":
        allimages.append(name)

print (allimages)

imagesnames = []
labelsnames = []
for name in allimages:
	if name[-6] != 'l':
		imagesnames.append(name)
	else:
		labelsnames.append(name)

imagesnames.sort()
labelsnames.sort()

print(imagesnames)
print(labelsnames)

for i in range(0, len(imagesnames)):
    arrays = cv2.imread(imagesnames[i], cv2.IMREAD_UNCHANGED)
    larray = arrays[:, :, 3]
    label  = cv2.imread(f'{labelsnames[i]}', cv2.IMREAD_UNCHANGED)

    compare = cv2.compare(larray, label, 0)

    if compare.all():
    	print ("Same")
    else:
    	print ("Not same")