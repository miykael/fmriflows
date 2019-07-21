DATA_DIR=/home/TR2000

fmriprep-docker \
    --image=poldracklab/fmriprep:1.2.6 \
    --nthreads=16 \
    --task-id=memory \
    --output-space=template \
    --template-resampling-grid=/data/derivatives/templates/mni_icbm152_nlin_asym_09c_3.5mm_T1_brain.nii.gz \
    --skip-bids-validation \
    --fs-license-file=license.txt \
    --work-dir=${DATA_DIR}/derivatives/workingdir \
    --write-graph \
    ${DATA_DIR} \
    ${DATA_DIR}/derivatives \
    participant --participant_label 01 02 03 04 05 06 07 08 09 10 11 12
