DATA_DIR=/home/TR1000

fmriprep-docker \
    --image=poldracklab/fmriprep:1.2.6 \
    --nthreads=16 \
    --task-id=MGT \
    --output-space=template \
    --template-resampling-grid=/data/derivatives/templates/mni_icbm152_nlin_asym_09c_2.0mm_T1_brain.nii.gz \
    --skip-bids-validation \
    --fs-license-file=license.txt \
    --work-dir=${DATA_DIR}/derivatives/workingdir \
    --write-graph \
    ${DATA_DIR} \
    ${DATA_DIR}/derivatives \
    participant --participant_label 001 002 003 004 005 006 008 009 010 011 013 014 015 016 017 018 019 020 021 022
