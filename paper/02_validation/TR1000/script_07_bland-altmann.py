# IMPORTANT DISCLAIMER!!!!
# This script heavily borrows from the paper of: Bowring, A., Maumet, C.,
# & Nichols, T. (2018). Exploring the impact of analysis software
# on task fMRI results. BioRxiv, 285585. http://dx.doi.org/10.1101/285585

import os
import numpy as np
import seaborn as sns
from nilearn.image import *
from nibabel.processing import resample_from_to
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from itertools import combinations
from statsmodels.nonparametric.smoothers_lowess import lowess


res_path = 'res_06_bland-altmann'
if not os.path.exists(res_path):
    os.makedirs(res_path)


def mask_using_nan(data_img):
    # Set masking using NaN's
    data_orig = data_img.get_data()

    if np.any(np.isnan(data_orig)):
        # Already using NaN
        data_img_nan = data_img
    else:
        # Replace zeros by NaNs
        data_nan = data_orig
        data_nan[data_nan == 0] = np.nan
        # Save as image
        data_img_nan = new_img_like(data_img, data_nan, copy_header=True)

    return (data_img_nan)


def bland_altman_values(data1_file,
                        data2_file,
                        reslice_on_2=True,
                        *args,
                        **kwargs):

    # Load nifti images
    data1_img = load_img(data1_file)
    data2_img = load_img(data2_file)

    # Set masking using NaN's
    data1_img = mask_using_nan(data1_img)
    data2_img = mask_using_nan(data2_img)

    if reslice_on_2:
        # Resample data1 on data2 using nearest nneighbours
        data1_resl_img = resample_from_to(data1_img, data2_img, order=0)
        gm_resl_img = resample_from_to(img_gm, data2_img, order=0)
        wm_resl_img = resample_from_to(img_wm, data2_img, order=0)
        csf_resl_img = resample_from_to(img_csf, data2_img, order=0)

        # Load data from images
        data1 = data1_resl_img.get_data()
        data2 = data2_img.get_data()
        gm = gm_resl_img.get_data()
        wm = wm_resl_img.get_data()
        csf = csf_resl_img.get_data()
    else:
        # Resample data2 on data1 using nearest nneighbours
        data2_resl_img = resample_from_to(data2_img, data1_img, order=0)
        gm_resl_img = resample_from_to(img_gm, data1_img, order=0)
        wm_resl_img = resample_from_to(img_wm, data1_img, order=0)
        csf_resl_img = resample_from_to(img_csf, data1_img, order=0)

        # Load data from images
        data1 = data1_img.get_data()
        data2 = data2_resl_img.get_data()
        gm = gm_resl_img.get_data()
        wm = wm_resl_img.get_data()
        csf = csf_resl_img.get_data()

    # Masking white matter and csf images for a threshold of 0.5
    gm_mask = gm >= 0.5
    gm_mask = gm_mask * 1
    wm_mask = wm >= 0.5
    wm_mask = wm_mask * 1
    csf_mask = csf >= 0.5
    csf_mask = csf_mask * 1

    # Vectorise input data
    data1 = np.reshape(data1, -1)
    data2 = np.reshape(data2, -1)
    gm_mask = np.reshape(gm_mask, -1)
    wm_mask = np.reshape(wm_mask, -1)
    csf_mask = np.reshape(csf_mask, -1)

    use_gm = False
    if use_gm:
        mask = gm_mask == 1
    else:
        mask = np.logical_not(np.logical_or(wm_mask == 1, csf_mask == 1))

    data1 = data1[mask]
    data2 = data2[mask]

    in_mask_indices = np.logical_not(
        np.logical_or(
            np.logical_or(np.isnan(data1),
                          np.absolute(data1) == 0),
            np.logical_or(np.isnan(data2),
                          np.absolute(data2) == 0)))

    data1 = data1[in_mask_indices]
    data2 = data2[in_mask_indices]

    mean = np.mean([data1, data2], axis=0)
    ci_values = 1.96 * np.std([data1, data2], axis=0) / np.sqrt(2)
    diff = data1 - data2  # Difference between data1 and data2

    md = np.mean(diff)  # Mean of the difference
    sd = np.std(diff, axis=0)  # Standard deviation of the difference

    return mean, diff, ci_values, md, sd


def bland_altman_plot(f, gs, stat_file_1, stat_file_2, con, comparison,
                      res_path, reslice_on_2=True, filename=None,
                      lims=(-8, 8, -6, 6)):
    ax1 = f.add_subplot(gs[:-1, 1:9])
    mean, diff, ci_values, md, sd = bland_altman_values(
        stat_file_1, stat_file_2, reslice_on_2)
    print(con, mean.min(), mean.max(), diff.min(), diff.max())
    hb = ax1.hexbin(mean, diff, bins='log', cmap='viridis', gridsize=50,
                    extent=lims)
    ax1.axis(lims)
    ax1.axhline(linewidth=3.5, color='y')
    stepsize = int(len(mean) / 10000)
    x = mean[np.argsort(mean)][::stepsize]
    y = diff[np.argsort(mean)][::stepsize]
    ci = ci_values[np.argsort(mean)][::stepsize]
    ys = lowess(y, x)[:, 1]
    yci = lowess(ci, x)[:, 1]
    plt.plot(x, ys, '--r', linewidth=3.5)
    plt.plot(x, ys+yci, ':w', linewidth=2.5)
    plt.plot(x, ys-yci, ':w', linewidth=2.5)
    ax2 = f.add_subplot(gs[:-1, 0], xticklabels=[], sharey=ax1)
    ax2.set_ylim(lims[2:4])
    ax2.hist(diff, 100, range=lims[2:4],histtype='stepfilled',
                orientation='horizontal', color='gray')
    ax2.invert_xaxis()
    ax3 = f.add_subplot(gs[-1, 1:9], yticklabels=[], sharex=ax1)
    ax3.hist(mean, 100, range=lims[0:2],histtype='stepfilled',
                orientation='vertical', color='gray')
    ax3.set_xlim(lims[0:2])
    ax3.invert_yaxis()
    ax4 = f.add_subplot(gs[:-1, 9])
    ax4.set_aspect(20)
    pos1 = ax4.get_position()
    ax4.set_position([pos1.x0 - 0.025, pos1.y0, pos1.width, pos1.height])
    cb = f.colorbar(hb, cax=ax4)

    filename = 'fig_{0}_{1}-{2}.svg'.format(con, *comparison)
    plt.tight_layout()
    plt.savefig(os.path.join(res_path, filename))
    plt.savefig(os.path.join(res_path, filename.replace('.svg', '.png')))
    plt.cla()


def bland_altman(file_list, categories, con):

    plt.style.use('seaborn-colorblind')
    sns.set_context('talk')

    # Create Bland-Altman plots
    if 'con_t' in con:
        s = 'T'
        lims = (-4.5, 5.5, -3.75, 4.5)
    else:
        s = 'F'
        lims = (1, 8, -6, 6)


    for idx in set(combinations(range(len(categories)), 2)):
        comparison = [categories[idx[0]], categories[idx[1]]]

        reslice = comparison[0] == 'SPM'
        f = plt.figure(figsize=(10*.6, 9*.6))
        gs0 = gridspec.GridSpec(1, 1)
        gs00 = gridspec.GridSpecFromSubplotSpec(
            9, 10, subplot_spec=gs0[0], hspace=0.0, wspace=0.0)
        bland_altman_plot(
            f,
            gs00,
            file_list[idx[0]],
            file_list[idx[1]],
            con,
            comparison,
            res_path,
            reslice,
            lims=lims)


# Specify masks
img_gm = load_img('templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_gm.nii.gz')
img_gm = mask_using_nan(img_gm)
img_wm = load_img('templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_wm.nii.gz')
img_wm = mask_using_nan(img_wm)
img_csf = load_img('templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_csf.nii.gz')
img_csf = mask_using_nan(img_csf)

# Specify contrasts
contrasts = ['con_t_gain']

# Specify methods to compare
categories = ['fmriflows_5', 'fmriflows_none', 'fmriprep', 'fsl', 'spm']

# Create figures
for con in contrasts:

    file_list = [
        'res_05_2ndlevel_one-sided/nifti_group_%s_%s.nii.gz' % (con, c)
        for c in categories
    ]

    bland_altman(file_list, categories, con)

# Create mosaic figure
!convert res_06_bland-altmann/fig_con_t_gain_fmriflows_5-fmriflows_none.png -alpha off -fill white -colorize 100% res_06_bland-altmann/blank.png
!montage res_06_bland-altmann/fig_con_t_gain_fmriflows_5-*.png -mode Concatenate -tile 4x1 res_06_bland-altmann/summary_part01.png
!montage res_06_bland-altmann/blank.png res_06_bland-altmann/fig_con_t_gain_fmriflows_none-*.png -mode Concatenate -tile 4x1 res_06_bland-altmann/summary_part02.png
!montage res_06_bland-altmann/blank.png res_06_bland-altmann/blank.png res_06_bland-altmann/fig_con_t_gain_fmriprep-*.png -mode Concatenate -tile 4x1 res_06_bland-altmann/summary_part03.png
!montage res_06_bland-altmann/blank.png res_06_bland-altmann/blank.png res_06_bland-altmann/blank.png res_06_bland-altmann/fig_con_t_gain_fsl-spm.png -mode Concatenate -tile 4x1 res_06_bland-altmann/summary_part04.png
!montage res_06_bland-altmann/summary_part0?.png -mode Concatenate -tile 1x4 res_06_bland-altmann/summary.png
