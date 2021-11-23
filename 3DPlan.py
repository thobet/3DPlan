"""

This program is the main one of the 3DPlan algorithm.
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

from lib.SemanticPass import SFMImage
from lib.utils import *
from lib.MyTriangulation import Triang
from lib.Metashape_SFM import MetaSFM
from lib.Clustering import dbscan
import os
from pathlib import Path

if __name__ == '__main__':
    # --- Set the environment ---
    path = Path(os.getcwd())
    parent_directory = path.parent

    # --- Define the number of the output images channels ---
    out = ['3D', '4D']
    out_selection = input_check('3D (0) or 4D (1) output? (Write 0 or 1): ', [0, 1],
                                'Not a valid answer, please try again   ')
    if out_selection == 0:
        message('3D option is selected')
    else:
        message('4D option is selected')
    
    # --- Define the Structure from Motion and Multi View Stereo software --- 
    SFM_selection = input_check('Agisoft-Metashape (0), Mapillary-OpenSFM (1) or MyTriangulation (2)? '
                                '(Write 0, 1 or 2): ', [0, 1, 2], 'Not a valid answer, please try again')
    if SFM_selection == 0:
        message('Agisoft-Metashape option is selected.')
        agi_selection = input_check('Python Module (0) or GUI (1) output? (Write 0 or 1): ', [0, 1],
                                    'Not a valid answer, please try again')
    elif SFM_selection == 1:
        message('Mapillary-OpenSFM option is selected.')
    else:
        message('MyTriangulation option is selected.')
    
    # --- Define the edge semantic information source ---
    semantic_selection = input_check('Canny (0) or external semantic information (1)? (Write 0 or 1): ', [0, 1],
                                     'Not a valid answer, please try again')
    
    imgsuff = input_check('Give the available image format: ', ['.JPG', '.jpg', '.TIFF', '.tiff', '.tif', '.PNG', '.png'],
                          'The given format is not available or valid.')
    images = find_files(f'{path}/rgb', imgsuff)
    
    if len(images) == 0:
        ans = input_check(f'There are 0 images into rgb directory with {imgsuff} format do you want to continue '
                          f'the process? (y, n) ', ['y', 'Y', 'n', 'N'], 'Not a valid answer, please try again')
        if ans == 'n' or ans == 'N':
            error_message('The execution was terminated because the available images are 0', True)
    
    # --- Construct the 4D images ---
    message('Enrich images with semantic information ...')
    if semantic_selection == 0:
        message('Canny option was selected. Set the min and max values, using the trackbars, '
                'and then press Q to edit the next image.')
        for image in images:
            SFMImage(path, image, simages=False, out=out[out_selection], blurmethod='GaussianBlur', edgemethod='Canny')
    else:
        message('External semantic information option was selected.')
        simages = find_files(f'{path}/semantic_images', '.jpg')
        for image in images:
            SFMImage(path, image, simages=True, out=out[out_selection], edgemethod='Sematic_Info')

    sfm = ['Agisoft_Metashape', 'OpenSFM', 'MyTriangulation']
    sfm = sfm[SFM_selection]

    # --- OpenSfM variation ---
    if sfm == 'OpenSFM':
        message('OpenSFM implementation')
        osfm_env(parent_directory)
                
        message('OpenSFM pipeline execution ...')
        os.system(f'{parent_directory}/OpenSfM/bin/opensfm_run_all {parent_directory}/OpenSfM/data/3DPlan')

        lines_env(parent_directory)
        classify_points(f'{path}/Lines', 'merged.ply', 'edges', method=1)

    # --- Agisoft-Metashape variation ---
    if sfm == 'Agisoft_Metashape':
        message('Agisoft Metashape implementation')
        lines_env(parent_directory, method=0)

        # --- Agisoft Metashape Python Variation ---        
        if agi_selection == 0:
            s = MetaSFM('project.psx')
            classify_points(f'{path}/Lines', 'merged.ply', 'edges', method=3)
        
        else:
            # --- Agisoft Metashape GUI Variation ---
            message('GUI was selected. Use the 4D images from the (./3DPlan/images) path for the dense cloud '
                    'production using Agisoft Metashape GUI. When the dense cloud is produced, '
                    'export it as "merged.txt" in the (./3DPlan/Lines) directory.')
            out = input_check('If the produced point cloud i.e., merged.txt is added into ./3DPlan/Lines/ directory '
                              'write 1 and then press enter to continue: ', [1], 'Try again, not a valid answer')
            classify_points(f'{path}/Lines', 'merged.txt', 'edges')

    # --- MyTriangulation Variation ---
    if sfm == 'MyTriangulation':
        message('MyTriangulation implementation')
        Triang(capture='front')
        lines_env(parent_directory, method=2)
        classify_points(f'{path}/Lines', 'merged.txt', 'edges', method=2)

    # --- Line extraction ---
    points = read_txt_coordinates_to_list('./Lines', 'edges.txt')
    dbscan(points, eps=0.01,  min_samples=10)
    
    '''
    txt2ply(f'{Path(os.getcwd())}/Lines/edges.txt', f'{Path(os.getcwd())}/Lines/edges.ply')
    txt2ply(f'{Path(os.getcwd())}/Lines/LinesLabels.txt', f'{Path(os.getcwd())}/Lines/LinesLabels.ply')
    '''
    
    message('3D Plan is saved to Lines folder as 3DPlan.dxf')
