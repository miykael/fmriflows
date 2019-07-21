import os
import numpy as np
from os.path import basename
from nipype.algorithms.confounds import TSNR
from nilearn.image import math_img

for res_path in ['res_02_tsnr', 'res_02_mean']:
    if not os.path.exists(res_path):
        os.makedirs(res_path)

task = 'memory'

for sidx in range(1, 13):
    for ridx in range(1, 5):
        for i, in_file in enumerate([
                'fmriflows/preproc_func/sub-{0:02d}/sub-{0:02d}_task-{2}_run-{1:02d}_tFilter_5.0.100.0_sFilter_LP_0.0mm.nii.gz',
                'fmriflows/preproc_func/sub-{0:02d}/sub-{0:02d}_task-{2}_run-{1:02d}_tFilter_None.100.0_sFilter_LP_0.0mm.nii.gz',
                'fmriprep/sub-{0:02d}/func/sub-{0:02d}_task-{2}_run-{1:02d}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz',
                'fsl_feat/sub-{0:02d}/sub-{0:02d}_task-{2}_run-{1:02d}_bold_norm.nii.gz',
                'spm/sub-{0:02d}/wasub-{0:02d}_task-{2}_run-{1:02d}_bold.nii.gz',
        ]):

            in_file = in_file.format(sidx, ridx, task)
            file_name = basename(in_file).replace('.nii.gz', '')
            out_tsnr = 'res_02_tsnr/tsnr_%s.nii.gz' % file_name
            out_mean = 'res_02_mean/mean_%s.nii.gz' % file_name

            tsnr = TSNR(regress_poly=2,
                        in_file=in_file,
                        tsnr_file=out_tsnr,
                        mean_file=out_mean)
            res = tsnr.run()
