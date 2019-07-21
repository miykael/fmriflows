import os
import numpy as np
import pandas as pd
from glob import glob
from nilearn.image import *
from nilearn.plotting import plot_stat_map, plot_glass_brain, find_cut_slices
from nistats.second_level_model import SecondLevelModel
from nistats.thresholding import map_threshold
from scipy.ndimage import binary_erosion, binary_dilation, binary_fill_holes
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style('darkgrid')
plt.style.use('seaborn-colorblind')

p_thresh = 0.001
height_control = 'fpr'

res_path = 'res_05_2ndlevel'
if not os.path.exists(res_path):
    os.makedirs(res_path)

# Relevant parameters
template = 'templates/mni_icbm152_nlin_asym_09c_1.0mm_T1_brain.nii.gz'

# Specify list of contrasts
contrasts = ['con_t_av_v']

# Go through everything
for con in contrasts:

    t_values = []
    heat_values = []
    t_values_masked = []
    heat_values_masked = []

    for method in ['fmriprep', 'fsl', 'spm', 'fmriflows_none', 'fmriflows_5']:

        # List of contrasts
        cons = sorted(glob('res_04_zmaps/zmap_%s_sub-*_%s.nii.gz' % (con, method)))

        # List of subjects
        subjects = [[s for s in c.split('_') if 'sub' in s][0] for c in cons]
        n_subj = len(subjects)

        # Create subject overview figure
        tmaps = []
        for cidx, tmap in enumerate(cons):
            _, threshold = map_threshold(
                tmap, level=p_thresh, height_control=height_control)
            tmap = math_img('img * (np.abs(img)>=%.8f)' % threshold, img=tmap)
            tmaps.append(tmap)
            print(threshold)

            plot_glass_brain(
                tmap, colorbar=False, threshold=threshold, plot_abs=False,
                symmetric_cbar=False, title=subjects[cidx], display_mode='z',
                axes=axes[int(cidx / 4), int(cidx % 4)])
            #tmap.to_filename(res_path + '/thr_%s_%s_h-%s_p-%.3f.nii.gz' % (
            #    method, subjects[cidx], height_control, p_thresh))
        fig.suptitle(
            '%s: %s (%s - %s)' % (method, con, height_control, p_thresh),
            fontsize=40)
        fig.savefig(res_path + '/overview_subjects_%s_%s.svg' % (con, method))
        fig.tight_layout()
        fig.clf()

        # Create mask (containing only voxels with values in at least half of the subjects)
        img_concat = concat_imgs(cons)
        mask = np.sum(img_concat.get_data()!=0, axis=-1)>=(img_concat.shape[-1] * 0.5)
        mask = binary_fill_holes(
            binary_dilation(binary_erosion(mask, iterations=2), iterations=2))
        group_mask = new_img_like(img_concat, mask.astype('int'),
                                  copy_header=True)

        # Create 2nd-level model
        design_matrix = pd.DataFrame([1] * len(cons), columns=['intercept'])
        second_level_model = SecondLevelModel(n_jobs=-1, mask=group_mask)
        second_level_model = second_level_model.fit(cons, design_matrix=design_matrix)

        # Estimate contrast
        z_map = second_level_model.compute_contrast(output_type='z_score')
        z_map.to_filename(res_path + '/nifti_group_%s_%s.nii.gz' % (con, method))

        # Correct for multiple comparison
        _, threshold = map_threshold(
            z_map, level=p_thresh, height_control=height_control,
            cluster_threshold=3)

        # Plot contrast
        plot_glass_brain(
            z_map,
            display_mode='lyrz',
            black_bg=True,
            colorbar=True,
            threshold=threshold,
            vmin=threshold,
            plot_abs=False,
            symmetric_cbar=False,
            title='%s: %s (%s - %s)' % (method, con, height_control, p_thresh),
            output_file=res_path + '/glass_group_%s_%s_h-%s_p-%.3f.svg' %
            (con, method, height_control, p_thresh))
        plot_stat_map(
            z_map,
            display_mode='z',
            black_bg=False,
            colorbar=True,
            threshold=threshold,
            symmetric_cbar=False,
            bg_img=template,
            cut_coords=[-4, 14, 30],
            draw_cross=False,
            output_file=res_path + '/stat_group_%s_%s_h-%s_p-%.3f.svg' %
            (con, method, height_control, p_thresh))

        # Create and plot p-value heat image
        imgs_threshold = [math_img('1.0*(img>0) - 1.0*(img<0)', img=t) for t in tmaps]
        img_p_heat = mean_img(imgs_threshold)
        #img_p_heat.to_filename(res_path + '/heat_%s_%s_h-%s_p-%.3f.nii.gz' %
        #                       (con, method, height_control, p_thresh))

        plot_glass_brain(
            img_p_heat,
            display_mode='lyrz',
            black_bg=True,
            colorbar=True,
            vmin=0.25,
            vmax=0.8,
            threshold=0.25,
            plot_abs=False,
            symmetric_cbar=False,
            title='%s: %s (%s - %s)' % (method, con, height_control, p_thresh),
            output_file=res_path + '/glass_heat_%s_%s_h-%s_p-%.3f.svg' %
            (con, method, height_control, p_thresh))
        plot_stat_map(
            img_p_heat,
            display_mode='z',
            black_bg=False,
            colorbar=True,
            threshold=0.25,
            symmetric_cbar=False,
            bg_img=template,
            vmax=0.8,
            cut_coords=[-4, 14, 30],
            draw_cross=False,
            output_file=res_path + '/stat_heat_%s_%s_h-%s_p-%.3f.svg' %
            (con, method, height_control, p_thresh))

        # Save values for density plot
        t_values.append([method, z_map.get_data()])
        heat_values.append([method, img_p_heat.get_data()])

        # Apply GM mask for the distribution plots
        if 'spm' in method:
            gm_mask = load_img('templates/spm_TPM_1.5mm_tpm_gm.nii.gz')
        else:
            gm_mask = load_img(
                'templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_gm.nii.gz')
        gm_mask = resample_to_img(gm_mask, z_map).get_data() >= 0.5

        # Save values for density plot after applying a GM mask
        t_values_masked.append([method, z_map.get_data()[gm_mask]])
        heat_values_masked.append([method, img_p_heat.get_data()[gm_mask]])

    # Plot histograms of voxel distribution above threshold
    sns.set_style('darkgrid')
    plt.style.use('seaborn-colorblind')
    threshold = 3.1
    fig = plt.figure(figsize=(8, 4))
    for m, t in t_values:
        sns.kdeplot(t[np.abs(t) > threshold], shade=True, vertical=False)
    plt.legend([m for m, t in t_values])
    plt.xlabel('Z-value in voxel above threshold [thr=%d]' % threshold)
    plt.ylabel('Percentage of voxels in bin')
    plt.title('Group Average of Z-value in contrast: %s' % con)
    plt.tight_layout()
    fig.savefig('%s/summary_zvalue_%s.svg' % (res_path, con))
    fig.clf()

    # Plot histograms of voxel distribution above threshold
    sns.set_style('darkgrid')
    plt.style.use('seaborn-colorblind')
    threshold = 3.1
    fig = plt.figure(figsize=(8, 4))
    for m, t in t_values_masked:
        sns.kdeplot(t[np.abs(t) > threshold], shade=True, vertical=False)
    plt.legend([m for m, t in t_values])
    plt.xlabel('Z-value in voxel above threshold [thr=%d]' % threshold)
    plt.ylabel('Percentage of voxels in bin')
    plt.title('Group Average of Z-value in contrast: %s' % con)
    plt.tight_layout()
    fig.savefig('%s/summary_zvalue_%s_masked.svg' % (res_path, con))
    fig.clf()

    # Plot histograms of voxel distribution above threshold
    sns.set_style('darkgrid')
    plt.style.use('seaborn-colorblind')
    threshold = 0.2
    fig = plt.figure(figsize=(8, 4))
    for m, t in heat_values:
        sns.kdeplot(np.abs(t[np.abs(t) > threshold]), shade=True, vertical=False)
    plt.legend([m for m, t in heat_values])
    plt.xlabel('Overlap in voxel above threshold [thr=%d]' % threshold)
    plt.ylabel('Percentage of voxels in bin')
    plt.title('Group Average of Overlap in contrast: %s' % con)
    plt.tight_layout()
    fig.savefig('%s/summary_overlap_%s.svg' % (res_path, con))
    fig.clf()

    # Plot histograms of voxel distribution above threshold
    sns.set_style('darkgrid')
    plt.style.use('seaborn-colorblind')
    threshold = 0.2
    fig = plt.figure(figsize=(8, 4))
    for m, t in heat_values_masked:
        sns.kdeplot(np.abs(t[np.abs(t) > threshold]), shade=True, vertical=False)
    plt.legend([m for m, t in heat_values])
    plt.xlabel('Overlap in voxel above threshold [thr=%d]' % threshold)
    plt.ylabel('Percentage of voxels in bin')
    plt.title('Group Average of Overlap in contrast: %s' % con)
    plt.tight_layout()
    fig.savefig('%s/summary_overlap_%s_masked.svg' % (res_path, con))
    fig.clf()
