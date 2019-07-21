#!/bin/bash

set -e

# Generate Dockerfile
generate_docker() {
  docker run \
      --rm kaczmarj/neurodocker:master generate docker \
      --base neurodebian:stretch-non-free \
      --pkg-manager apt \
      --spm12 version=r7219 \
      --install gcc g++ make graphviz tree tree less swig netbase \
                git-annex-standalone git-annex-remote-rclone liblzma-dev \
                afni ants fsl-core convert3d \
      --add-to-entrypoint "source /etc/fsl/fsl.sh" \
      --add-to-entrypoint 'export PATH=/usr/lib/afni/bin:$PATH' \
      --add-to-entrypoint 'export PATH=/usr/lib/ants:$PATH' \
      --user=neuro \
      --workdir /home/neuro \
      --miniconda version="latest" \
        conda_install="python=3.7 h5py ipython joblib jupyter
                       jupyter_contrib_nbextensions jupyterlab matplotlib
                       nb_conda nbformat nipy numpy pandas pytest scikit-image
                       scikit-learn scipy seaborn sphinx statsmodels traits " \
        pip_install="https://github.com/nipy/nipype/tarball/master
                     https://github.com/miykael/atlasreader/tarball/master
                     datalad[full] duecredit nbval nibabel nilearn
                     nistats nitime pybids autopep8" \
        create_env="neuro" \
        activate=True \
      --miniconda miniconda_version="4.6" \
        conda_install="python=2.7 h5py hdf5 imageio ipython joblib jupyter
                       jupyter_contrib_nbextensions jupyterlab matplotlib
                       nb_conda nbformat nipy numpy pandas pytest scikit-image
                       scikit-learn scipy seaborn shogun statsmodels " \
        pip_install="https://github.com/miykael/atlasreader/tarball/master
                     dask datalad[full] duecredit nbval nibabel
                     nilearn nistats pprocess pybids autopep8" \
        create_env="mvpa" \
        activate=False \
      --run-bash "source activate mvpa && cd /home/neuro  \
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
      --run-bash "source activate neuro && jupyter nbextension enable exercise2/main && jupyter nbextension enable hide_input/main && jupyter nbextension enable code_prettify/autopep8 && jupyter nbextension enable hide_input_all/main && jupyter nbextension enable printview/main && jupyter nbextension enable spellchecker/main" \
      --run-bash "source activate mvpa && jupyter nbextension enable exercise2/main && jupyter nbextension enable hide_input/main && jupyter nbextension enable code_prettify/autopep8 && jupyter nbextension enable hide_input_all/main && jupyter nbextension enable printview/main && jupyter nbextension enable spellchecker/main" \
      --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
      --workdir /home/neuro/notebooks \
      --cmd jupyter-notebook
}

# Generate Singularity file (does not include last --cmd option)
generate_singularity() {
  docker run \
      --rm kaczmarj/neurodocker:master generate singularity \
      --base neurodebian:stretch-non-free \
      --pkg-manager apt \
      --spm12 version=r7219 \
      --install gcc g++ make graphviz tree tree less swig netbase \
                git-annex-standalone git-annex-remote-rclone liblzma-dev \
                afni ants fsl-core convert3d \
      --add-to-entrypoint "source /etc/fsl/fsl.sh" \
      --add-to-entrypoint 'export PATH=/usr/lib/afni/bin:$PATH' \
      --add-to-entrypoint 'export PATH=/usr/lib/ants:$PATH' \
      --user=neuro \
      --workdir /home/neuro \
      --miniconda version="latest" \
        conda_install="python=3.7 h5py ipython joblib jupyter
                       jupyter_contrib_nbextensions jupyterlab matplotlib
                       nb_conda nbformat nipy numpy pandas pytest scikit-image
                       scikit-learn scipy seaborn sphinx statsmodels traits " \
        pip_install="https://github.com/nipy/nipype/tarball/master
                     https://github.com/miykael/atlasreader/tarball/master
                     datalad[full] duecredit nbval nibabel nilearn
                     nistats nitime pybids autopep8" \
        create_env="neuro" \
        activate=True \
      --miniconda miniconda_version="4.6" \
        conda_install="python=2.7 h5py hdf5 imageio ipython joblib jupyter
                       jupyter_contrib_nbextensions jupyterlab matplotlib
                       nb_conda nbformat nipy numpy pandas pytest scikit-image
                       scikit-learn scipy seaborn shogun statsmodels " \
        pip_install="https://github.com/miykael/atlasreader/tarball/master
                     dask datalad[full] duecredit nbval nibabel
                     nilearn nistats pprocess pybids autopep8" \
        create_env="mvpa" \
        activate=False \
      --run-bash "source activate mvpa && cd /home/neuro  \
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
      --run-bash "source activate neuro && jupyter nbextension enable exercise2/main && jupyter nbextension enable hide_input/main && jupyter nbextension enable code_prettify/autopep8 && jupyter nbextension enable hide_input_all/main && jupyter nbextension enable printview/main && jupyter nbextension enable spellchecker/main" \
      --run-bash "source activate mvpa && jupyter nbextension enable exercise2/main && jupyter nbextension enable hide_input/main && jupyter nbextension enable code_prettify/autopep8 && jupyter nbextension enable hide_input_all/main && jupyter nbextension enable printview/main && jupyter nbextension enable spellchecker/main" \
      --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
      --workdir /home/neuro/notebooks
}

generate_docker > Dockerfile
generate_singularity > Singularity
