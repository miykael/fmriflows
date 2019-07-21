import os
import numpy as np
import pandas as pd
import nibabel as nb
from glob import glob
from nilearn.image import smooth_img, new_img_like
from nilearn.plotting import plot_stat_map
from nistats.design_matrix import make_first_level_design_matrix
from nistats.reporting import plot_contrast_matrix, plot_design_matrix
from nistats.first_level_model import FirstLevelModel
from nistats.thresholding import map_threshold

res_path = 'res_04_zmaps'
if not os.path.exists(res_path):
    os.makedirs(res_path)

# Relevant parameters
task = 'MGT'
fwhm = 6.0
slice_time_ref = 0.
drift_model = 'cosine'
period_cut = 100.
tr = 1.0
design_matrix_size = 17
hrf_model = 'spm'
template = 'templates/mni_icbm152_nlin_asym_09c_1.0mm_T1_brain.nii.gz'
n_subj = 20

# How many runs
rtop = 4

# Go through all subjects
for sdx in [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]:

    # Select all relevant files
    func_fmriflows_none = ['fmriflows/preproc_func/sub-{0:03d}/sub-{0:03d}_task-{2}_run-{1:02d}_tFilter_None.100.0_sFilter_LP_0.0mm.nii.gz'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    func_fmriflows_5 = ['fmriflows/preproc_func/sub-{0:03d}/sub-{0:03d}_task-{2}_run-{1:02d}_tFilter_5.0.100.0_sFilter_LP_0.0mm.nii.gz'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    func_fmriprep = ['fmriprep/sub-{0:03d}/func/sub-{0:03d}_task-{2}_run-{1:02d}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    func_fsl = ['fsl_feat/sub-{0:03d}/sub-{0:03d}_task-{2}_run-{1:02d}_bold_norm.nii.gz'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    func_spm = ['spm/sub-{0:03d}/wsub-{0:03d}_task-{2}_run-{1:02d}_bold.nii.gz'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]

    mcf_fmriflows_none = ['fmriflows/preproc_func/sub-{0:03d}/sub-{0:03d}_task-{2}_run-{1:02d}_tFilter_None.100.0.par'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    mcf_fmriflows_5 = ['fmriflows/preproc_func/sub-{0:03d}/sub-{0:03d}_task-{2}_run-{1:02d}_tFilter_5.0.100.0.par'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    mcf_fmriprep = ['fmriprep/sub-{0:03d}/func/sub-{0:03d}_task-{2}_run-{1:02d}_desc-confounds_regressors.par'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    mcf_fsl = ['fsl_feat/sub-{0:03d}/sub-{0:03d}_task-{2}_run-{1:02d}_bold_norm.par'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    mcf_spm = ['spm/sub-{0:03d}/rp_sub-{0:03d}_task-{2}_run-{1:02d}_bold.txt'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]

    nss_files = ['fmriflows/preproc_func/sub-{0:03d}/sub-{0:03d}_task-{2}_run-{1:02d}_nss.txt'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]
    event_files = ['event_files/sub-{0:03d}_task-{2}_run-{1:02d}_events.tsv'.format(sdx, rdx, task) for rdx in range(1, rtop + 1)]

    # Go through the different methods
    for method, funcs, mcf_par in [
        ['fmriprep', func_fmriprep, mcf_fmriprep],
        ['fsl', func_fsl, mcf_fsl],
        ['spm', func_spm, mcf_spm],
        ['fmriflows_5', func_fmriflows_5, mcf_fmriflows_5],
        ['fmriflows_none', func_fmriflows_none, mcf_fmriflows_none],
    ]:

        # Smooth images
        imgs_smooth = smooth_img(funcs, fwhm=fwhm)

        # Create design matrix
        design_matrices = []

        for idx, e in enumerate(event_files):

            # Collect events information
            events = pd.read_csv(e, sep='\t')
            events['trial_type'] = np.where(
                events['participant_response'].str.contains("accept"), 'accept',
                'reject')
            events['modulation'] = np.abs(events['gain'] - events['loss'])
            events = events[['trial_type', 'onset', 'duration', 'modulation']]

            if 'fmriflows' in method:
                nss_delay = tr * np.loadtxt(nss_files[idx])
                events['onset'] -= nss_delay

            # Build experimental paradigm
            img = imgs_smooth[idx]
            n_scans = img.shape[-1]
            frame_times = np.arange(n_scans) * tr
            nuisance_reg = np.loadtxt(mcf_par[idx])

            if 'par' in method:
                nuisance_reg = np.hstack((nuisance_reg,
                                       np.loadtxt(mcf_par[idx].replace(
                                           '5.0', 'None'))))
                par_offset = 12
            else:
                par_offset = 6

            # Build design matrix with the reviously defined parameters
            design_matrix = make_first_level_design_matrix(
                    frame_times,
                    events,
                    hrf_model=hrf_model,
                    drift_model=drift_model,
                    period_cut=period_cut,
                    add_regs=nuisance_reg,
                    )

            dm_diff = design_matrix_size + (par_offset - 6) - design_matrix.shape[1]
            if dm_diff:
                for d in range(1, dm_diff + 1):
                    design_matrix['rand_%02d' % d] = np.repeat(
                        1.0, len(design_matrix))

            # Put the design matrices in a list
            design_matrices.append(design_matrix)

        # Create GLM
        fmri_glm = FirstLevelModel(
            t_r=tr,
            slice_time_ref=slice_time_ref,
            hrf_model=hrf_model,
            drift_model=drift_model,
            period_cut=period_cut,
            standardize=False,
            noise_model='ar1',
            n_jobs=-1)

        # Estimate GLM
        fmri_glm = fmri_glm.fit(imgs_smooth, design_matrices=design_matrices)
        design_matrix = fmri_glm.design_matrices_[0]

        # Specify contrasts
        contrast_list = {}
        dm_size = design_matrix.shape[1]

        contrast_gain = np.zeros(dm_size)
        contrast_gain[0] = 1
        contrast_list['con_t_gain'] = contrast_gain

        contrast_loss = np.zeros(dm_size)
        contrast_loss[1] = 1
        contrast_list['con_t_loss'] = contrast_loss

        contrast_diff = np.zeros(dm_size)
        contrast_diff[0] = 1
        contrast_diff[1] = -1
        contrast_list['con_t_diff'] = contrast_diff

        contrast_motion = np.zeros((par_offset, dm_size))
        for r in range(par_offset):
            contrast_motion[r, 2 + r] = 1
        contrast_list['con_F_motion'] = contrast_motion

        # Estimate and plot contrasts
        for cont in contrast_list:
            z_map = fmri_glm.compute_contrast(
                contrast_list[cont], stat_type=cont[4], output_type='z_score')
            identifier = '%s_sub-%03d_%s' % (cont, sdx, method)
            out_file = '%s/zmap_%s' % (res_path, identifier)
            z_map.to_filename('%s.nii.gz' % out_file)

        # Plot design matrices and contrasts
        plot_design_matrix(
            fmri_glm.design_matrices_[0],
            output_file='%s/design_matrix_01_sub-%03d.svg' % (res_path, sdx))

        plot_design_matrix(
            fmri_glm.design_matrices_[1],
            output_file='%s/design_matrix_02_sub-%03d.svg' % (res_path, sdx))

        plot_design_matrix(
            fmri_glm.design_matrices_[2],
            output_file='%s/design_matrix_03_sub-%03d.svg' % (res_path, sdx))

        plot_design_matrix(
            fmri_glm.design_matrices_[3],
            output_file='%s/design_matrix_04_sub-%03d.svg' % (res_path, sdx))

        # Plot contrast matrix
        for cont in contrast_list:
            plot_contrast_matrix(
                contrast_list[cont],
                design_matrix=fmri_glm.design_matrices_[0],
                output_file='%s/%s.svg' % (res_path, cont))

        print('Finished sub: %03d - Method: %s' % (sdx, method))
