import os
import nipype
import nbformat


def test_version():
    print('nipype version: ', nipype.__version__)


def prepare_test_data():

    print('Install test dataset ds000114.')
    os.system('datalad install ///workshops/nih-2017/ds000114')

    print('Download required data.')
    cmd = 'datalad get -J 4 '
    cmd += 'ds000114/sub-01/ses-test/anat/sub-01_ses-test_T1w.nii.gz '
    cmd += 'ds000114/sub-01/ses-test/func/sub-01_ses-test_task-fingerfootlips_bold.nii.gz '
    cmd += 'ds000114/sub-02/ses-test/anat/sub-02_ses-test_T1w.nii.gz '
    cmd += 'ds000114/sub-02/ses-test/func/sub-02_ses-test_task-fingerfootlips_bold.nii.gz '
    os.system(cmd)

    print('Move test data to data folder.')
    os.system('cp -rl /home/neuro/notebooks/ds000114/sub-0[12] /data')

    print('Renmae files to be conform to fmriflows.')
    cmd = 'mv /data/sub-01/ses-test/func/sub-01_ses-test_task-fingerfootlips_bold.nii.gz '
    cmd += '/data/sub-01/ses-test/func/sub-01_ses-test_task-fingerfootlips_run-01_bold.nii.gz'
    os.system(cmd)
    cmd = 'mv /data/sub-02/ses-test/func/sub-02_ses-test_task-fingerfootlips_bold.nii.gz '
    cmd += '/data/sub-02/ses-test/func/sub-02_ses-test_task-fingerfootlips_run-01_bold.nii.gz'
    os.system(cmd)

    print('Copy fmriflows configuration files to data folder.')
    os.system('cp /home/neuro/examples/* /data')


def reduce_comp_time_anat():
    """
    Change ANTs' normalization command to reduce computation time on CircleCi.
    """
    nb_path = '/home/neuro/notebooks/01_preproc_anat.ipynb'

    # Load notebook
    with open(nb_path, 'rb') as nb_file:
        nb_node = nbformat.reads(nb_file.read(), nbformat.NO_CONVERT)

    # Rewrite ANTs' registration command
    for cell in nb_node['cells']:
        if 'code' == cell['cell_type']:
            if 'Normalize anatomy to ICBM template' in cell['source']:
                txt = cell['source']
                txt = txt.replace('100, 70, 50, 20', '50, 25, 4, 2')
                cell['source'] = txt

    # Overwrite notebook with new changes
    nbformat.write(nb_node, nb_path)

    print('ANTs Registration simplified.')


if __name__ == '__main__':

    test_version()
    prepare_test_data()
    reduce_comp_time_anat()

    # Notebooks that should be tested
    notebooks = ['/home/neuro/notebooks/01_preproc_anat.ipynb',
                 '/home/neuro/notebooks/02_preproc_func.ipynb']

    for test in notebooks:
        pytest_cmd = 'pytest --nbval-lax --nbval-cell-timeout 7200 -v -s %s' % test
        print(pytest_cmd)
        os.system(pytest_cmd)
