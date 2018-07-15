import os
import sys
import nibabel as nb
from os.path import join as opj
from nilearn.image import resample_img
from nibabel.spaces import vox2out_vox

"""
This script extracts the probability maps of all regions in the HarvardOxford
atlas and stores them with a preferred voxel resolution.
"""

# Evaluate requested voxel resolution
if len(sys.argv) == 1:
    res = [1.0] * 3
elif len(sys.argv) == 2:
    res = [float(sys.argv[1])] * 3
elif len(sys.argv) == 4:
    res = [float(f) for f in sys.argv[1:4]]
else:
    print('No valid voxel resolution!\nSpecify either 1 value for isotropic '
          'resolution\nor 3 values for anisotropic resolution.')
    sys.exit()

# Specify path and name of output folder
output_path = '/templates'
output_folder = 'HarvardOxford_ProbMasks'

# Create output folder
output_dir = opj(output_path, output_folder)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load atlas labels
with open(opj(output_path, 'HarvardOxford_labels.csv'), 'r') as f:
    rois = f.readlines()
    rois = [r[:-1].split(',') for r in rois]

# Load lateralized cortical and subcortical probability map
template_path = opj(os.getenv('FSLDIR'), 'data', 'atlases', 'HarvardOxford')
cortl = nb.load(opj(template_path, 'HarvardOxford-cortl-prob-1mm.nii.gz'))
subc = nb.load(opj(template_path, 'HarvardOxford-sub-prob-1mm.nii.gz'))

# Extract and resample (if needed) individual probability maps
for roi_id, roi_name in rois:

    # Get individual map
    roi_id = int(roi_id)
    if roi_id < 100:
        img = cortl.slicer[..., roi_id - 1]
    else:
        img = subc.slicer[..., roi_id - 101]

    # Resample image if needed
    if res != [1.0, 1.0, 1.0]:
        new_shape, new_affine = vox2out_vox(img, voxel_sizes=res)
        img = resample_img(img, new_affine, new_shape, clip=True)

    # Store image in output folder
    img.to_filename(opj(output_dir, '%s.nii.gz' % roi_name))
