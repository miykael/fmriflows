DATASET=TR1000
TASK=MGT
res=2.0mm

for sdx in 001 002 003 004 005 006 008 009 010 011 013 014 015 016 017 018 019 020 021 022
do

    # Create output folder
    OUTPATH=${DATASET}/derivatives/fsl_feat/sub-${sdx}
    mkdir -p $OUTPATH/anat
    cp ${DATASET}/sub-${sdx}/anat/sub-${sdx}_T1w.nii.gz $OUTPATH/anat/.
    mkdir -p $OUTPATH/func
    cp ${DATASET}/sub-${sdx}/func/sub-${sdx}_task-${TASK}_run-*_bold.nii.gz $OUTPATH/func/.

    # Apply FOV correction for better brain extraction
    robustfov -i $OUTPATH/anat/sub-${sdx}_T1w.nii.gz -r $OUTPATH/anat/sub-${sdx}_T1w.nii.gz

    # Skull strip image
    bet $OUTPATH/anat/sub-${sdx}_T1w.nii.gz $OUTPATH/anat/sub-${sdx}_T1w_brain.nii.gz -R

    # Run FEAT
    feat ${DATASET}/derivatives/fsl_feat/fsl_design_sub-${sdx}.fsf
    echo $sdx

    # Apply Nonlinear Warp
    for rdx in {01..04}
    do
        applywarp \
            --ref=${DATASET}/derivatives/templates/mni_icbm152_nlin_asym_09c_${res}_T1_brain.nii.gz \
            --in=$OUTPATH/func/sub-${sdx}_task-${TASK}_run-${rdx}_bold_sub-${sdx}.feat/filtered_func_data.nii.gz \
            --out=${OUTPATH}/sub-${sdx}_task-${TASK}_run-${rdx}_bold_norm.nii.gz \
            --warp=$OUTPATH/func/sub-${sdx}_task-${TASK}_run-${rdx}_bold_sub-${sdx}.feat/reg/highres2standard_warp.nii.gz \
            --premat=$OUTPATH/func/sub-${sdx}_task-${TASK}_run-${rdx}_bold_sub-${sdx}.feat/reg/example_func2highres.mat \
            --interp=spline

        cp $OUTPATH/func/sub-${sdx}_task-${TASK}_run-${rdx}_bold_sub-${sdx}.feat/mc/prefiltered_func_data_mcf.par \
            ${OUTPATH}/sub-${sdx}_task-${TASK}_run-${rdx}_bold_norm.par

        # Set datatype to int
        fslmaths ${OUTPATH}/sub-${sdx}_task-${TASK}_run-${rdx}_bold_norm.nii.gz \
                 -div 2 \
                 ${OUTPATH}/sub-${sdx}_task-${TASK}_run-${rdx}_bold_norm.nii.gz \
                 -odt short

    done
    echo "Normalized."
done
