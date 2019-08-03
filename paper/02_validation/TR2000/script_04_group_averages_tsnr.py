import os
import numpy as np
import nibabel as nb
from glob import glob
import seaborn as sns
from nilearn.image import mean_img, concat_imgs, math_img, resample_to_img
from nilearn.plotting import plot_anat
from matplotlib import pyplot as plt
sns.set_style('darkgrid')
plt.style.use('seaborn-colorblind')

# Find files
files_fsl = sorted(glob('res_02_tsnr/tsnr_sub-*_task-*_run-*_bold_norm.nii.gz'))
files_fmriprep = sorted(glob('res_02_tsnr/tsnr_sub-*_task-*_run-*_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'))
files_spm = sorted(glob('res_02_tsnr/tsnr_wasub-*_task-*_run-*_bold.nii.gz'))
files_fmriflows_5 = sorted(glob('res_02_tsnr/tsnr_sub-*_task-*_run-*_tFilter_5.0.100.0_sFilter_LP_0.0mm.nii.gz'))
files_fmriflows_none = sorted(glob('res_02_tsnr/tsnr_sub-*_task-*_run-*_tFilter_None.100.0_sFilter_LP_0.0mm.nii.gz'))

# Create output folder
res_path = 'res_03_group_tsnr'
if not os.path.exists(res_path):
    os.makedirs(res_path)

# Create variable to save for histogram plotting
tsnr_values = []

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

    # Correct TSNR images for lenght of functional run
    n_volumes = 275
    tsnr_list = []
    for f in file_list:
        tsnr_list += [math_img('img * %.08f' % np.sqrt(n_volumes), img=f)]

    # Concatenate group means
    group_means = concat_imgs(file_list)

    # Only keep voxels that have values in at least 50% of volumes
    group_means = math_img(
        'img * (np.sum(img!=0, axis=-1)>=(img.shape[-1]/2.))[..., None]',
        img=group_means)

    # Create tsnr mean map
    group_img = math_img('np.mean(img, axis=-1)', img=group_means)
    group_img.to_filename('%s/group_tsnr%s.nii.gz' % (res_path, method))

    # Plot figure
    display = plot_anat(
        group_img,
        display_mode='xz',
        cut_coords=[-20, 10],
        colorbar=False,
        cmap='Spectral_r',
        threshold=350,
        vmin=350,
        vmax=1400,
        dim=1,
        annotate=False,
        draw_cross=False,
        black_bg=True,
    )
    img_tmp = nb.load(template_gm)
    display.savefig('%s/group_tsnr%s_%s.svg' % (res_path, postfix, method))

    tsnr_values.append([method, group_img.get_data()])

# Plot histograms of voxel distribution above threshold
sns.set_style('darkgrid')
plt.style.use('seaborn-colorblind')
threshold = 1
fig = plt.figure(figsize=(8, 4))
for m, t in tsnr_values:
    sns.kdeplot(t[t >= threshold], shade=True, vertical=False)
plt.legend([m for m, t in tsnr_values])
plt.xlabel('TSNR in voxel above threshold [thr=%d]' % threshold)
plt.ylabel('Percentage of voxels in bin')
plt.title('Group Average TSNR')
plt.tight_layout()
fig.savefig('%s/group_tsnr_summary.svg' % res_path)
