import os
import numpy as np
import pandas as pd
from glob import glob
from nilearn.image import *
from nilearn.plotting import plot_stat_map
from nistats.second_level_model import SecondLevelModel
from nistats.thresholding import map_threshold
from scipy.ndimage import binary_erosion, binary_dilation, binary_fill_holes

res_path = 'res_09_compare'
if not os.path.exists(res_path + '/tsnr'):
    os.makedirs(res_path + '/tsnr')

# Relevant parameters for processing
task = 'memory'
temp_res='3.5'
template = 'templates/mni_icbm152_nlin_asym_09c_%smm_T1_brain.nii.gz' % temp_res
nrun=4
nvol=275

# Relevant parameters for stats
p_thresh = 0.001
cluster_threshold = 5
height_control = 'fdr'

# Go through all subjects
slist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
mlist = ['fmriflows_5', 'fmriflows_none', 'fmriprep', 'fsl', 'spm']

# Get list of files
filelist = []
filelist += ['res_02_tsnr/tsnr_sub-{0:02d}_task-{1}_run-{2:02d}_tFilter_5.0.100.0_sFilter_LP_0.0mm.nii.gz'.format(sdx, task, rdx + 1) for sdx in slist for rdx in range(nrun)]
filelist += ['res_02_tsnr/tsnr_sub-{0:02d}_task-{1}_run-{2:02d}_tFilter_None.100.0_sFilter_LP_0.0mm.nii.gz'.format(sdx, task, rdx + 1) for sdx in slist for rdx in range(nrun)]
filelist += ['res_02_tsnr/tsnr_sub-{0:02d}_task-{1}_run-{2:02d}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'.format(sdx, task, rdx + 1) for sdx in slist for rdx in range(nrun)]
filelist += ['res_02_tsnr/tsnr_sub-{0:02d}_task-{1}_run-{2:02d}_bold_norm.nii.gz'.format(sdx, task, rdx + 1) for sdx in slist for rdx in range(nrun)]
filelist += ['res_02_tsnr/tsnr_wasub-{0:02d}_task-{1}_run-{2:02d}_bold.nii.gz'.format(sdx, task, rdx + 1) for sdx in slist for rdx in range(nrun)]

# Create method identifier
method_id = [m for m in mlist for s in slist for rdx in range(nrun)]

# Resample images to geometry of template and rescale TSNR value with SQRT(NVol)
imgs = []
for i, e in enumerate(method_id):
    if 'spm' in e:
        img = resample_to_img(filelist[i], template)
    else:
        img = load_img(filelist[i])
    imgs.append(math_img('img * np.sqrt(%d)' % nvol, img=img))

# Create mask (containing only voxels with values in at least half of the images)
img_concat = concat_imgs(imgs)
mask = np.sum(img_concat.get_data()!=0, axis=-1)>=(img_concat.shape[-1] * 0.8)
mask = binary_fill_holes(
        binary_dilation(binary_erosion(mask, iterations=2), iterations=2))
group_mask = new_img_like(img_concat, mask.astype('int'), copy_header=True)

# Create 2nd-level model
design_matrix = design_matrix = pd.get_dummies(method_id)
second_level_model = SecondLevelModel(n_jobs=-1, mask=group_mask)
second_level_model = second_level_model.fit(imgs, design_matrix=design_matrix)

# Compute contrasts, save nifti and plot glass brain
weights = [ [1, 0, 0, 0, 0], [1,-1, 0, 0, 0], [1, 0,-1, 0, 0], [1, 0, 0,-1, 0], [1, 0, 0, 0,-1],
           [-1, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1,-1, 0, 0], [0, 1, 0,-1, 0], [0, 1, 0, 0,-1],
           [-1, 0, 1, 0, 0], [0,-1, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1,-1, 0], [0, 0, 1, 0,-1],
           [-1, 0, 0, 1, 0], [0,-1, 0, 1, 0], [0, 0,-1, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1,-1],
           [-1, 0, 0, 0, 1], [0,-1, 0, 0, 1], [0, 0,-1, 0, 1], [0, 0, 0,-1, 1], [0, 0, 0, 0, 1]]

for i, w in enumerate(weights):

        # Estimate contrast
        z_map = second_level_model.compute_contrast(
                second_level_contrast=w, second_level_stat_type='t',
                output_type='z_score')
        #z_map.to_filename(res_path + '/tsnr/tsnr_%04d.nii.gz' % (i + 1))

        img, threshold = map_threshold(
                z_map, level=p_thresh, height_control=height_control,
                cluster_threshold=cluster_threshold)
        img.to_filename(res_path + '/tsnr/tsnr_%04d_thr.nii.gz' % (i + 1))

        plot_stat_map(
                img,
                cut_coords=[-20, 10],
                draw_cross=False,
                annotate=False,
                bg_img=template,
                dim=0.5,
                vmax=20,
                display_mode='xz',
                black_bg=True,
                colorbar=False,
                threshold=threshold,
                symmetric_cbar=False,
                output_file=res_path + '/tsnr_%04d.png' % (i + 1))

# Create mosaic figure
!montage res_09_compare/tsnr_00??.png -mode Concatenate -tile 5x5 res_09_compare/tsnr.png
