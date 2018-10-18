#!/bin/bash

set -e

# Generate Dockerfile
generate_docker() {
  docker run --rm kaczmarj/neurodocker:master generate docker \
           --base neurodebian:stretch-non-free \
           --pkg-manager apt \
           --install gcc g++ graphviz tree tree less swig netbase \
                     git-annex-standalone git-annex-remote-rclone \
           --ants version=2.2.0 method=binaries \
           --spm12 version=r7219 \
           --install fsl-core \
           --add-to-entrypoint "source /etc/fsl/fsl.sh" \
           --convert3d version=1.0.0 method=binaries \
           --user=neuro \
           --miniconda version="latest" \
             conda_install="python=3.6 ipython pytest jupyter jupyterlab jupyter_contrib_nbextensions
                            numpy scipy pandas matplotlib seaborn nipy pyface sphinx h5py joblib
                            traits scikit-learn scikit-image nbformat nb_conda statsmodels" \
             pip_install="https://github.com/nipy/nipype/tarball/master
                          https://github.com/INCF/pybids/tarball/0.6.5
                          https://github.com/miykael/atlasreader/tarball/master
                          nibabel nilearn pymvpa2 datalad[full] nipy duecredit nbval" \
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
           --copy notebooks "/home/neuro/notebooks" \
           --copy scripts/test_notebooks.py "/home/neuro/test_notebooks.py" \
           --run 'chown -R neuro /home/neuro' \
           --run 'chown -R neuro /templates' \
           --run 'chown -R neuro /data' \
           --run 'rm -rf /opt/conda/pkgs/*' \
           --user=neuro \
           --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
           --workdir /home/neuro/notebooks \
           --cmd jupyter-notebook
}

# Generate Singularity file (does not include last --cmd option)
generate_singularity() {
  docker run --rm kaczmarj/neurodocker:master generate singularity \
           --base neurodebian:stretch-non-free \
           --pkg-manager apt \
           --install fsl gcc g++ graphviz tree tree less swig netbase \
                     git-annex-standalone git-annex-remote-rclone \
           --ants version=2.2.0 method=binaries \
           --spm12 version=r7219 \
           --install fsl-core \
           --add-to-entrypoint "source /etc/fsl/fsl.sh" \
           --convert3d version=1.0.0 method=binaries \
           --user=neuro \
           --miniconda version="latest" \
             conda_install="python=3.6 ipython pytest jupyter jupyterlab jupyter_contrib_nbextensions
                            numpy scipy pandas matplotlib seaborn nipy pyface sphinx h5py joblib
                            traits scikit-learn scikit-image nbformat nb_conda statsmodels" \
             pip_install="https://github.com/nipy/nipype/tarball/master
                          https://github.com/INCF/pybids/tarball/0.6.5
                          https://github.com/miykael/atlasreader/tarball/master
                          nibabel nilearn pymvpa2 datalad[full] nipy duecredit nbval" \
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
           --copy notebooks "/home/neuro/notebooks" \
           --copy scripts/test_notebooks.py "/home/neuro/test_notebooks.py" \
           --run 'chown -R neuro /home/neuro' \
           --run 'chown -R neuro /templates' \
           --run 'chown -R neuro /data' \
           --run 'rm -rf /opt/conda/pkgs/*' \
           --user=neuro \
           --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
           --workdir /home/neuro/notebooks
}

generate_docker > Dockerfile
generate_singularity > Singularity
