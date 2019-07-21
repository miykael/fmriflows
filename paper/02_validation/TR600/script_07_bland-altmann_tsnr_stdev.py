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


res_path = 'res_07_bland-altmann_tsnr_stdev'
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
    diff = data1 - data2  # Difference between data1 and data2

    md = np.mean(diff)  # Mean of the difference
    sd = np.std(diff, axis=0)  # Standard deviation of the difference

    return mean, diff, md, sd


def bland_altman_plot(f, gs, stat_file_1, stat_file_2, postfix, comparison,
                      x_lab, y_lab, reslice_on_2=True, filename=None,
                      lims=(-8, 8, -6, 6)):
    ax1 = f.add_subplot(gs[:-1, 1:5])
    mean, diff, md, sd = bland_altman_values(
        stat_file_1, stat_file_2, reslice_on_2)
    print(postfix, mean.min(), mean.max(), diff.min(), diff.max())
    hb = ax1.hexbin(mean, diff, bins='log', cmap='viridis', gridsize=50,
                    extent=lims)
    ax1.axis(lims)
    ax1.axhline(linewidth=1, color='y')
    ax1.set_title('{0} - {1}'.format(*comparison))
    stepsize = int(len(mean) / 10000)
    x = mean[np.argsort(mean)][::stepsize]
    y = diff[np.argsort(mean)][::stepsize]
    ys = lowess(y, x)[:, 1]
    ax1.plot(x, ys, '--r')
    ax2 = f.add_subplot(gs[:-1, 0], xticklabels=[], sharey=ax1)
    ax2.set_ylim(lims[2:4])
    ax2.hist(diff, 100, range=lims[2:4],histtype='stepfilled',
             orientation='horizontal', color='gray')
    ax2.invert_xaxis()
    ax2.set_ylabel('Difference' + y_lab)
    ax3 = f.add_subplot(gs[-1, 1:5], yticklabels=[], sharex=ax1)
    ax3.hist(mean, 100, range=lims[0:2],histtype='stepfilled',
             orientation='vertical', color='gray')
    ax3.set_xlim(lims[0:2])
    ax3.invert_yaxis()
    ax3.set_xlabel('Average' + x_lab)
    ax4 = f.add_subplot(gs[:-1, 5])
    ax4.set_aspect(20)
    pos1 = ax4.get_position()
    ax4.set_position([pos1.x0 - 0.025, pos1.y0, pos1.width, pos1.height])
    cb = f.colorbar(hb, cax=ax4)
    cb.set_label('log10(N)')

    filename = 'fig_{0}_{1}-{2}.svg'.format(postfix, *comparison)
    plt.savefig(os.path.join('res_07_bland-altmann_tsnr_stdev', filename))


def bland_altman(file_list, categories, postfix):

    plt.style.use('seaborn-colorblind')

    if postfix=='stdev':
        lims = (0, 1600, -1000, 1500)
    elif postfix=='tsnr':
        lims = (-15, 185, -75, 170)

    x_label = ' of {}'.format(postfix)

    for idx in set(combinations([0, 1, 2, 3, 4], 2)):
        comparison = [categories[idx[0]], categories[idx[1]]]

        reslice = comparison[0] == 'SPM'
        f = plt.figure(figsize=(6, 5))
        gs0 = gridspec.GridSpec(1, 1)
        gs00 = gridspec.GridSpecFromSubplotSpec(
            5, 6, subplot_spec=gs0[0], hspace=0.50, wspace=1.3)
        y_label = ' of {0} ({1} - {2})'.format(postfix, *comparison)
        bland_altman_plot(
            f,
            gs00,
            file_list[idx[0]],
            file_list[idx[1]],
            postfix,
            comparison,
            x_label,
            y_label,
            reslice,
            lims=lims)


# Specify masks
img_gm = load_img('templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_gm.nii.gz')
img_gm = mask_using_nan(img_gm)
img_wm = load_img('templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_wm.nii.gz')
img_wm = mask_using_nan(img_wm)
img_csf = load_img('templates/mni_icbm152_nlin_asym_09c_1.0mm_tpm_csf.nii.gz')
img_csf = mask_using_nan(img_csf)

# Specify methods to compare
categories = ['fMRIflows_5', 'fMRIflows_None', 'fMRIPrep', 'FSL', 'SPM']

# Create figures
for postfix in ['stdev', 'tsnr']:

    fmriflows_none_file = 'res_03_group_{0}/group_{0}_fmriflows_none.nii.gz'.format(postfix)
    fmriflows_5_file = 'res_03_group_{0}/group_{0}_fmriflows_5.nii.gz'.format(postfix)
    fmriprep_file = 'res_03_group_{0}/group_{0}_fmriprep.nii.gz'.format(postfix)
    fsl_file = 'res_03_group_{0}/group_{0}_fsl.nii.gz'.format(postfix)
    spm_file = 'res_03_group_{0}/group_{0}_spm.nii.gz'.format(postfix)

    file_list = [fmriflows_5_file, fmriflows_none_file, fmriprep_file,
                 fsl_file, spm_file]

    bland_altman(file_list, categories, postfix)
