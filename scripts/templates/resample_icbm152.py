import sys
from os.path import join as opj
from nibabel import load, Nifti1Image
from nilearn.image import resample_img
from nibabel.spaces import vox2out_vox

"""
This script resamples the ICBM 152 template to requested voxel resolution.
"""

# Evaluate requested voxel resolution
if len(sys.argv) == 1:
    res = [1] * 3
elif len(sys.argv) == 2:
    res = [float(sys.argv[1])] * 3
elif len(sys.argv) == 4:
    res = [float(f) for f in sys.argv[1:4]]
else:
    print('No valid voxel resolution!\nSpecify either 1 value for isotropic '
          'resolution\nor 3 values for anisotropic resolution.')
    sys.exit()

# Specify path to ICBM 152 template
fpath = '/templates/mni_icbm152_nlin_asym_09c'

# Compute new shape and affine matrix
img = load(opj(fpath, '1.0mm_T1.nii.gz'))
target_shape, target_affine = vox2out_vox(img, voxel_sizes=res)

# Resample the rest of the templates
for nifti in ['1.0mm_T1.nii.gz',
              '1.0mm_T2.nii.gz',
              '1.0mm_PD.nii.gz',
              '1.0mm_brain.nii.gz',
              '1.0mm_tpm_csf.nii.gz',
              '1.0mm_tpm_gm.nii.gz',
              '1.0mm_tpm_wm.nii.gz',
              '1.0mm_brain_prob_mask.nii.gz',
              '1.0mm_mask.nii.gz']:

    # Load and resample images
    img = load(opj(fpath, nifti))
    img_resample = resample_img(img, target_affine, target_shape, clip=True)
    data = img_resample.get_data()
    new_img = Nifti1Image(data, img_resample.affine, img_resample.header)
    new_img.to_filename(opj(fpath, nifti).replace('1.0mm', 'newmm'))
