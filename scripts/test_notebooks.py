import os
import nipype
import nbformat


def test_version():
    print('nipype version: ', nipype.__version__)


def prepare_test_data():

    print('Install test dataset ds000114.')
    os.system('datalad install ///workshops/nih-2017/ds000114')

    print('Download required data.')
    task = 'fingerfootlips'
    cmd = 'datalad get -J 4 '
    for i in [1, 2]:
        cmd += 'ds000114/sub-%02d/ses-test/anat/' % i
        cmd += 'sub-%02d_ses-test_T1w.nii.gz ' % i
        cmd += 'ds000114/sub-%02d/ses-test/func/' % i
        cmd += 'sub-%02d_ses-test_task-%s_bold.nii.gz ' % (i, task)
    os.system(cmd)

    print('Move test data to data folder.')
    os.system('cp -lR /home/neuro/notebooks/ds000114/* /data/.')


def create_demo_JSON_specs():
    """
    Create JSON specification file
    """
    nb_path = '/home/neuro/notebooks/00_spec_preparation.ipynb'

    # Load notebook
    with open(nb_path, 'rb') as nb_file:
        nb_node = nbformat.reads(nb_file.read(), nbformat.NO_CONVERT)

    # Rewrite ANTs' registration command
    for cell in nb_node['cells']:
        if 'code' == cell['cell_type']:
            if ' = subject_list' in cell['source']:
                txt = cell['source']
                txt = txt.replace('= subject_list', '= subject_list[:2]')
                cell['source'] = txt
            elif 'func_files = layout.get(' in cell['source']:
                txt = cell['source']
                txt = txt.replace('task_id[0])',
                                  'task_id[1], session=\'test\')[:2]')
                cell['source'] = txt
            elif ' = session_list' in cell['source']:
                txt = cell['source']
                txt = txt.replace('= session_list', '= [session_list[1]]')
                cell['source'] = txt
            elif 'Voxel resolution of reference template' in cell['source']:
                txt = cell['source']
                txt = txt.replace('[1.0, 1.0, 1.0]', '[4.0, 4.0, 4.0]')
                cell['source'] = txt
            elif 'Should ANTs Normalization be done in' in cell['source']:
                txt = cell['source']
                txt = txt.replace(' = 3', ' = 2')
                cell['source'] = txt
            elif ' = task_id' in cell['source']:
                txt = cell['source']
                txt = txt.replace('= task_id', '= [task_id[1]]')
                cell['source'] = txt

    # Overwrite notebook with new changes
    nbformat.write(nb_node, nb_path)

    print('JSON specification file creation adapted to demo dataset.')


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
                txt = txt.replace('1000, 500, 250, 100', '1000, 500')
                txt = txt.replace('3, 2, 1, 0', '3, 2')
                txt = txt.replace('8, 4', '8, 4')
                cell['source'] = txt

    # Overwrite notebook with new changes
    nbformat.write(nb_node, nb_path)

    print('ANTs Registration simplified.')


if __name__ == '__main__':

    test_version()
    prepare_test_data()
    create_demo_JSON_specs()
    reduce_comp_time_anat()

    # Notebooks that should be tested
    notebooks = [
        '/home/neuro/notebooks/00_spec_preparation.ipynb',
        '/home/neuro/notebooks/01_preproc_anat.ipynb',
        '/home/neuro/notebooks/02_preproc_func.ipynb',
        '/home/neuro/notebooks/03_analysis_1st-level.ipynb'
    ]

    for test in notebooks:
        pytest_cmd = 'pytest --nbval-lax --nbval-cell-timeout 7200 -v -s '
        pytest_cmd += test
        print(pytest_cmd)
        os.system(pytest_cmd)
