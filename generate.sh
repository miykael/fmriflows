#!/bin/bash

set -e

# Generate Dockerfile
generate_docker() {
  docker run \
      --rm repronim/neurodocker:0.7.0 generate docker \
      --pkg-manager apt \
      --base neurodebian:stretch-non-free \
      --arg DEBIAN_FRONTEND=noninteractive \
      --install gcc g++ make graphviz tree tree less swig netbase \
                git-annex-standalone git-annex-remote-rclone liblzma-dev \
                afni ants fsl-core convert3d \
      --spm12 version=r7771 \
      --add-to-entrypoint "source /etc/fsl/fsl.sh" \
      --add-to-entrypoint 'export PATH=/usr/lib/afni/bin:$PATH' \
      --add-to-entrypoint 'export PATH=/usr/lib/ants:$PATH' \
      --user=neuro \
      --workdir /home/neuro \
      --miniconda version="latest" \
        conda_install="python=3.7 h5py=3.1 ipython=7.21 joblib=1.0 jupyter=1.0
                       jupyter_contrib_nbextensions=0.5 jupyterlab=3.0 matplotlib=3.3
                       nb_conda=2.2 nbformat=5.1 networkx=2.5 nibabel=3.2 nipy=0.4
                       notebook=6.2 numpy=1.20 pandas=1.2 pytest=6.2 scikit-image=0.18
                       scikit-learn=0.24 scipy=1.2 seaborn=0.11 sphinx=3.5 statsmodels=0.12 traits=6.2" \
        pip_install="atlasreader==0.1 autopep8==1.5 datalad[full] duecredit==0.8 nbval==0.9
                     nilearn==0.7 nipype==1.6.0 nistats==0.0.1rc0 nitime==0.9 pybids==0.12" \
        create_env="neuro" \
        activate=True \
      --miniconda miniconda_version="4.6" \
        conda_install="python=2.7 h5py=2.8 hdf5=1.10 imageio=2.6 ipython=5.8 joblib=0.14 jupyter=1.0
                       jupyter_contrib_nbextensions=0.5 jupyterlab=0.33 matplotlib=2.2 nb_conda=2.2
                       nbconvert=5.6 nbformat=4.4 networkx=2.2 nibabel=2.5 nipy=0.4 notebook=5.7
                       numpy=1.16 pandas=0.24 pytest=4.6 scikit-image=0.14 scikit-learn=0.20 scipy=1.1
                       seaborn=0.9 shogun=6.1 statsmodels=0.10" \
        pip_install="atlasreader==0.1 autopep8==1.5 dask datalad[full] duecredit==0.8 nbval==0.9
                     nibabel nilearn==0.5 nistats==0.0.1rc0 pprocess==0.5 pybids==0.9.5" \
        create_env="mvpa" \
        activate=False \
      --run-bash "source activate mvpa && cd /home/neuro  \
             && pip install -U pip \
             && pip install -U numpy \
             && git clone git://github.com/PyMVPA/PyMVPA.git \
             && cd PyMVPA \
             && make 3rd \
             && python setup.py build_ext \
             && python setup.py install \
             && cd .. \
             && rm -rf PyMVPA \
             && source deactivate mvpa" \
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
      --copy notebooks/templates "/reports" \
      --run 'chown -R neuro /home/neuro' \
      --run 'chown -R neuro /templates' \
      --run 'chown -R neuro /data' \
      --run 'rm -rf /opt/conda/pkgs/*' \
      --user=neuro \
      --run-bash "source activate mvpa && jupyter nbextension enable exercise2/main && jupyter nbextension enable hide_input/main && jupyter nbextension enable code_prettify/autopep8 && jupyter nbextension enable hide_input_all/main && jupyter nbextension enable printview/main && jupyter nbextension enable spellchecker/main" \
      --run-bash "source activate neuro && jupyter nbextension enable exercise2/main && jupyter nbextension enable hide_input/main && jupyter nbextension enable code_prettify/autopep8 && jupyter nbextension enable hide_input_all/main && jupyter nbextension enable printview/main && jupyter nbextension enable spellchecker/main" \
      --run-bash "source activate neuro && pip install -U pip && pip install -U numpy nbval" \
      --run-bash "git config --global user.email 'you@example.com' && git config --global user.name 'Your Name'" \
      --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
      --workdir /home/neuro/notebooks \
      --cmd "jupyter-notebook --port=8888 --no-browser --ip=0.0.0.0 --NotebookApp.token=fmriflows" \
      # MANUALLY SPLIT THIS PART IN DOCKERFILE TO
      # CMD ["jupyter-notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--NotebookApp.token=fmriflows"]

}

# Generate Singularity file (does not include last --cmd option)
generate_singularity() {
  docker run \
      --rm repronim/neurodocker:0.7.0 generate singularity \
      --pkg-manager apt \
      --base neurodebian:stretch-non-free \
      --spm12 version=r7771 \
      --install gcc g++ make graphviz tree tree less swig netbase \
                git-annex-standalone git-annex-remote-rclone liblzma-dev \
                afni ants fsl-core convert3d \
      --add-to-entrypoint "source /etc/fsl/fsl.sh" \
      --add-to-entrypoint 'export PATH=/usr/lib/afni/bin:$PATH' \
      --add-to-entrypoint 'export PATH=/usr/lib/ants:$PATH' \
      --user=neuro \
      --workdir /home/neuro \
      --miniconda version="latest" \
        conda_install="python=3.7 h5py=3.1 ipython=7.21 joblib=1.0 jupyter=1.0
                       jupyter_contrib_nbextensions=0.5 jupyterlab=3.0 matplotlib=3.3
                       nb_conda=2.2 nbformat=5.1 networkx=2.5 nibabel=3.2 nipy=0.4
                       notebook=6.2 numpy=1.20 pandas=1.2 pytest=6.2 scikit-image=0.18
                       scikit-learn=0.24 scipy=1.2 seaborn=0.11 sphinx=3.5 statsmodels=0.12 traits=6.2" \
        pip_install="atlasreader==0.1 autopep8==1.5 datalad[full] duecredit==0.8 nbval==0.9
                     nilearn==0.7 nipype==1.6.0 nistats==0.0.1rc0 nitime==0.9 pybids==0.12" \
        create_env="neuro" \
        activate=True \
      --miniconda miniconda_version="4.6" \
        conda_install="python=2.7 h5py=2.8 hdf5=1.10 imageio=2.6 ipython=5.8 joblib=0.14 jupyter=1.0
                       jupyter_contrib_nbextensions=0.5 jupyterlab=0.33 matplotlib=2.2 nb_conda=2.2
                       nbconvert=5.6 nbformat=4.4 networkx=2.2 nibabel=2.5 nipy=0.4 notebook=5.7
                       numpy=1.16 pandas=0.24 pytest=4.6 scikit-image=0.14 scikit-learn=0.20 scipy=1.1
                       seaborn=0.9 shogun=6.1 statsmodels=0.10" \
        pip_install="atlasreader==0.1 autopep8==1.5 dask datalad[full] duecredit==0.8 nbval==0.9
                     nibabel nilearn==0.5 nistats==0.0.1rc0 pprocess==0.5 pybids==0.9.5" \
        create_env="mvpa" \
        activate=False \
      --run-bash "source activate mvpa && cd /home/neuro  \
             && pip install -U pip \
             && pip install -U numpy \
             && git clone git://github.com/PyMVPA/PyMVPA.git \
             && cd PyMVPA \
             && make 3rd \
             && python setup.py build_ext \
             && python setup.py install \
             && cd .. \
             && rm -rf PyMVPA \
             && source deactivate mvpa" \
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
      --copy notebooks/templates "/reports" \
      --run 'chown -R neuro /home/neuro' \
      --run 'chown -R neuro /templates' \
      --run 'chown -R neuro /data' \
      --run 'rm -rf /opt/conda/pkgs/*' \
      --user=neuro \
      --run-bash "source activate mvpa && jupyter nbextension enable exercise2/main && jupyter nbextension enable hide_input/main && jupyter nbextension enable code_prettify/autopep8 && jupyter nbextension enable hide_input_all/main && jupyter nbextension enable printview/main && jupyter nbextension enable spellchecker/main" \
      --run-bash "source activate neuro && jupyter nbextension enable exercise2/main && jupyter nbextension enable hide_input/main && jupyter nbextension enable code_prettify/autopep8 && jupyter nbextension enable hide_input_all/main && jupyter nbextension enable printview/main && jupyter nbextension enable spellchecker/main" \
      --run-bash "source activate neuro && pip install -U pip && pip install -U numpy nbval" \
      --run-bash "git config --global user.email 'you@example.com' && git config --global user.name 'Your Name'" \
      --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
      --workdir /home/neuro/notebooks
}

generate_docker > Dockerfile
generate_singularity > Singularity
