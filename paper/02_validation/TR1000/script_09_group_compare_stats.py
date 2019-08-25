import os
import numpy as np
import pandas as pd
from glob import glob
from nilearn.image import *
from nilearn.plotting import plot_glass_brain
from nistats.second_level_model import SecondLevelModel
from nistats.thresholding import map_threshold
from scipy.ndimage import binary_erosion, binary_dilation, binary_fill_holes

res_path = 'res_09_compare'
if not os.path.exists(res_path + '/zmaps'):
    os.makedirs(res_path + '/zmaps')

# Relevant parameters for processing
temp_res='2.0'
template = 'templates/mni_icbm152_nlin_asym_09c_%smm_T1_brain.nii.gz' % temp_res
con='gain'

# Relevant parameters for stats
p_thresh = 0.05
cluster_threshold = 5
height_control = 'fdr'

# Go through all subjects
slist = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
mlist = ['fmriflows_5', 'fmriflows_none', 'fmriprep', 'fsl', 'spm']

filelist = sorted(['res_04_zmaps/zmap_con_t_{0}_sub-{1:03d}_{2}.nii.gz'.format(con, sdx, mdx)
                   for mdx in mlist
                   for sdx in slist])

# Resample images to geometry of template
imgs = []
for f in filelist:
    if '_spm'  in f:
        img = resample_to_img(f, template)
    else:
        img = load_img(f)
    imgs.append(img)

# Create mask (containing only voxels with values in at least half of the images)
img_concat = concat_imgs(imgs)
mask = np.sum(img_concat.get_data()!=0, axis=-1)>=(img_concat.shape[-1] * 0.8)
mask = binary_fill_holes(
        binary_dilation(binary_erosion(mask, iterations=2), iterations=2))
group_mask = new_img_like(img_concat, mask.astype('int'), copy_header=True)

# Create 2nd-level model
design_matrix = design_matrix = pd.get_dummies([c[37:-7] for c in filelist])
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
        #z_map.to_filename(res_path + '/zmaps/zmap_%04d.nii.gz' % (i + 1))

        img, threshold = map_threshold(
                z_map, level=p_thresh, height_control=height_control,
                cluster_threshold=cluster_threshold)
        img.to_filename(res_path + '/zmaps/zmap_%04d_thr.nii.gz' % (i + 1))

        plot_glass_brain(
                img,
                display_mode='xz',
                black_bg=True,
                colorbar=False,
                threshold=threshold,
                vmin=threshold,
                vmax=7.5,
                symmetric_cbar=False,
                output_file=res_path + '/zmap_%04d.png' % (i + 1))

# Create mosaic figure
!montage res_09_compare/zmap_00??.png -mode Concatenate -tile 5x5 res_09_compare/zmap.png
