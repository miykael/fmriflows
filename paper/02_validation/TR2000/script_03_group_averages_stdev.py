import os
import numpy as np
import nibabel as nb
from glob import glob
import seaborn as sns
from nilearn.image import mean_img, concat_imgs, math_img, resample_to_img, new_img_like
from nilearn.plotting import plot_anat
from matplotlib import pyplot as plt
sns.set_style('darkgrid')
plt.style.use('seaborn-colorblind')

# Find files
files_fsl = sorted(glob('res_02_mean/mean_sub-*_task-*_run-*_bold_norm.nii.gz'))
files_fmriprep = sorted(glob('res_02_mean/mean_sub-*_task-*_run-*_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'))
files_spm = sorted(glob('res_02_mean/mean_wasub-*_task-*_run-*_bold.nii.gz'))
files_fmriflows_5 = sorted(glob('res_02_mean/mean_sub-*_task-*_run-*_tFilter_5.0.100.0_sFilter_LP_0.0mm.nii.gz'))
files_fmriflows_none = sorted(glob('res_02_mean/mean_sub-*_task-*_run-*_tFilter_None.100.0_sFilter_LP_0.0mm.nii.gz'))

# Create output folder
res_path = 'res_03_group_stdev'
if not os.path.exists(res_path):
    os.makedirs(res_path)

# Create variable to save for histogram plotting
stdev_values = []

for method, file_list in [['fsl', files_fsl],
                          ['fmriprep', files_fmriprep],
                          ['spm', files_spm],
                          ['fmriflows_5', files_fmriflows_5],
                          ['fmriflows_none', files_fmriflows_none]]:

    # Specify templates
    if method=='spm':
        template_gm = 'templates/spm_TPM_1.5mm_tpm_gm.nii.gz'
        template_wm = 'templates/spm_TPM_1.5mm_tpm_wm.nii.gz'
    else:
        template_gm = 'templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_gm.nii.gz'
        template_wm = 'templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_wm.nii.gz'

    # Create white matter mask to compute mean value
    mask = resample_to_img(template_wm, file_list[0]).get_data() >= 0.8

    imgs_list = []
    for f in file_list:

        # Compute mean of image
        mean = mean_img(f)
        data = mean.get_data()

        # Apply brain mask to data and compute sigma
        temp = data * mask
        sigma = np.percentile(temp[temp!=0], 50) / 1000.

        # Standardize data by sigma and add image to imgs_list
        data /= sigma
        imgs_list.append(nb.Nifti1Image(data, mean.affine, mean.header))

    # Concatenate group means
    group_means = concat_imgs(imgs_list)

    # Only keep voxels that have values in at least 50% of volumes
    group_means = math_img(
        'img * (np.sum(img!=0, axis=-1)>=(img.shape[-1]/2.))[..., None]',
        img=group_means)

    # Create standard deviation map
    group_img = math_img('np.std(img, axis=-1)', img=group_means)
    group_img.to_filename('%s/group_stdev_%s.nii.gz' % (res_path, method))

    # Plot figure
    fig = plt.figure(figsize=(12, 3))
    display = plot_anat(
        group_img,
        display_mode='ortho',
        cut_coords=[-20, -10, 10],
        colorbar=True,
        cmap='cividis',
        threshold=50,
        vmin=50,
        vmax=250,
        title=method,
        dim=1,
        annotate=True,
        draw_cross=False,
        black_bg=True,
        figure=fig,
        )
    img_tmp = nb.load(template_gm)
    img_tmp = new_img_like(img_tmp, (img_tmp.get_data() >= 0.05).astype('int'),
        copy_header=True)
    display.add_contours(img_tmp, color='r', levels=1)
    fig.savefig('%s/group_stdev_%s.svg' % (res_path, method))

    stdev_values.append([method, group_img.get_data()])

# Plot histograms of voxel distribution above threshold
sns.set_style('darkgrid')
plt.style.use('seaborn-colorblind')
threshold = 5
fig = plt.figure(figsize=(8, 4))
for m, t in stdev_values:
    sns.kdeplot(t[t > threshold], shade=True, vertical=False, clip=[threshold, 250])
plt.legend([m for m, t in stdev_values])
plt.xlabel('Normalized STDEV in voxel between threshold [%d to %d]' % (threshold, 250))
plt.ylabel('Percentage of voxels in bin')
plt.title('Group Average Standard Deviation')
plt.tight_layout()
fig.savefig('%s/group_stdev_summary.svg' % res_path)
