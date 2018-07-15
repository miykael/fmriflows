#!/bin/bash
docker run --rm kaczmarj/neurodocker:master generate docker \
           --base neurodebian:stretch-non-free \
           --pkg-manager apt \
           --install gcc g++ graphviz tree less swig convert3d netbase \
                     git-annex-standalone git-annex-remote-rclone \
           --spm12 version=dev \
           --ants version=2.2.0 method=binaries \
           --install fsl-core fsl-harvard-oxford-atlases fsl-harvard-oxford-cortical-lateralized-atlas \
           --add-to-entrypoint "source /etc/fsl/fsl.sh" \
           --user=neuro \
           --miniconda \
             conda_install="python=3.6 ipython pytest jupyter jupyterlab jupyter_contrib_nbextensions
                            numpy scipy pandas matplotlib seaborn nipy pyface sphinx h5py joblib
                            traits scikit-learn scikit-image nbformat nb_conda statsmodels" \
             pip_install="https://github.com/nipy/nipype/tarball/master
                          https://github.com/INCF/pybids/tarball/master
                          nibabel nilearn nitime pymvpa2 datalad[full] nipy duecredit nbval" \
             create_env="neuro" \
             activate=True \
           --user=root \
           --run 'mkdir /data && chmod 777 /data && chmod a+s /data' \
           --run 'mkdir /workingdir && chmod 777 /workingdir && chmod a+s /workingdir' \
           --run 'mkdir /templates && chmod 777 /templates && chmod a+s /templates' \
           --run 'curl -qLO http://www.bic.mni.mcgill.ca/~vfonov/icbm/2009/mni_icbm152_nlin_asym_09c_nifti.zip \
                  && unzip mni_icbm152_nlin_asym_09c_nifti.zip -d /templates \
                  && rm mni_icbm152_nlin_asym_09c_nifti.zip \
                  && cd /templates/mni_icbm152_nlin_asym_09c
                  && mv mni_icbm152_csf_tal_nlin_asym_09c.nii 1.0mm_tpm_csf.nii \
                  && mv mni_icbm152_gm_tal_nlin_asym_09c.nii 1.0mm_tpm_gm.nii \
                  && mv mni_icbm152_pd_tal_nlin_asym_09c.nii 1.0mm_PD.nii \
                  && mv mni_icbm152_t1_tal_nlin_asym_09c_mask.nii 1.0mm_mask.nii \
                  && mv mni_icbm152_t1_tal_nlin_asym_09c.nii 1.0mm_T1.nii \
                  && mv mni_icbm152_t2_tal_nlin_asym_09c.nii 1.0mm_T2.nii \
                  && mv mni_icbm152_wm_tal_nlin_asym_09c.nii 1.0mm_tpm_wm.nii \
                  && gzip 1.0mm_*nii \
                  && /usr/bin/fsl5.0-fslmaths 1.0mm_tpm_gm.nii.gz -add 1.0mm_tpm_wm.nii.gz -add 1.0mm_tpm_csf.nii.gz 1.0mm_brain_prob_mask.nii.gz \
                  && /usr/bin/fsl5.0-fslmaths 1.0mm_T1.nii.gz -mul 1.0mm_mask.nii.gz 1.0mm_brain.nii.gz' \
           --copy scripts/templates/* "/templates/" \
           --copy notebooks "/home/neuro/notebooks" \
           --copy examples "/home/neuro/examples" \
           --copy scripts/test_notebooks.py "/home/neuro/test_notebooks.py" \
           --run 'chown -R neuro /home/neuro' \
           --run 'chown -R neuro /templates' \
           --run 'chown -R neuro /data' \
           --run 'rm -rf /opt/conda/pkgs/*' \
           --user=neuro \
           --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"*\" > ~/.jupyter/jupyter_notebook_config.py' \
           --workdir /home/neuro/notebooks \
           --cmd "jupyter-notebook" > Dockerfile
