"""

This program is part of the 3DPlan algorithm.
This program executes the workflow of the Metashape software until the production of the dense point cloud.
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


***The workflow was made according to metashape's pyhon api manual. Available at: https://www.agisoft.com/pdf/metashape_python_api_1_6_0.pdf***

"""

import Metashape
import os
from lib.utils import *


class MetaSFM():
    """
        Name: MetaSFM

        Description: This class executes the workflow of the Metashape software until the production of the dense point cloud.

        Parameters:
            projectname: The name of the .psx file in which the process will be saved.

        Functions:
            sfmmvs:      Executes the entire procedure.

        The workflow was made according to metashape's pyhon api manual. Available at: https://www.agisoft.com/pdf/metashape_python_api_1_6_0.pdf
    """

    def __init__(self, projectname: str = ' '):
        """Constructor"""
        self.projectname = projectname
        self.path = Path(os.getcwd())
        self.doc = Metashape.Document(self.projectname)
        self.doc.addChunk()

        self.imagesnames: list = []
        self.metaimages: list = []

        MetaSFM.sfmmvs(self)

    def sfmmvs(self):
        """This function executes the workflow of the Metashape software until the dense cloud production"""
        imagesnames = find_files(f'{self.path}/images', '.tiff')
        for imagename in imagesnames:
            imagepath = f'{self.path}/images/{imagename}'
            self.imagesnames.append(imagepath)
        self.doc.chunk.addPhotos(self.imagesnames)

        message(f'New chunk with {len(imagesnames)} images is created')

        message('Matching has been started')
        self.doc.chunk.matchPhotos(generic_preselection=True, reference_preselection=False)

        message('Align has been started')
        self.doc.chunk.alignCameras()

        message('Build depth maps has been started')
        self.doc.chunk.buildDepthMaps()

        message('Dense cloud production has been started')
        self.doc.chunk.buildDenseCloud()

        message(f'Save the project to {self.path / self.projectname}')
        if Metashape.app.activated:
            path = f'{self.path}/{self.projectname}'
            self.doc.chunk.exportPoints(path=f'{self.path}/Lines/merged.ply', binary=False, save_normals=False,
                                        save_colors=True, colors_rgb_8bit=False)
            self.doc.save(path)
        else:
            error_message(
                'Project was not saved due to deactivated license. Please activate your Agisoft Metashape License and try again.',
                sysex=True)
