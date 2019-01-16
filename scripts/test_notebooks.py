import os
import nipype
import nbformat


def test_version():
    print('nipype version: ', nipype.__version__)


def prepare_test_data():
    """Prepare test data."""
    print('Install test dataset ds000114 in user\'s home folder.')
    os.system('datalad -C /home/neuro install ///workshops/nih-2017/ds000114')

    print('Download required data.')
    task = 'fingerfootlips'
    cmd = 'datalad -C /home/neuro get -J 4 '
    for i in [1, 2]:
        cmd += 'ds000114/sub-%02d/ses-test/anat/' % i
        cmd += 'sub-%02d_ses-test_T1w.nii.gz ' % i
        cmd += 'ds000114/sub-%02d/ses-test/func/' % i
        cmd += 'sub-%02d_ses-test_task-%s_bold.nii.gz ' % (i, task)
    os.system(cmd)

    print('Move test data to data folder.')
    os.system('cp -RL /home/neuro/ds000114/* /data/.')


def reduce_specs():
    """Reduce specification parameters in JSON file a notebooks file."""

    # Load notebook 00_spec_preparation
    nb_path = '/home/neuro/notebooks/00_spec_preparation.ipynb'
    with open(nb_path, 'rb') as nb_file:
        nb_node = nbformat.reads(nb_file.read(), nbformat.NO_CONVERT)

    # Rewrite notebook cells
    for cell in nb_node['cells']:
        if 'code' == cell['cell_type']:
            if 'task_id = sorted(layout.get_tasks())' in cell['source']:
                txt = cell['source']
                txt = txt.replace('task_id = sorted(layout.get_tasks())',
                                  'task_id = [sorted(layout.get_tasks())[1]]')
                cell['source'] = txt
            elif 'Voxel resolution of reference template' in cell['source']:
                txt = cell['source']
                txt = txt.replace('[1.0, 1.0, 1.0]', '[4.0, 4.0, 4.0]')
                cell['source'] = txt
            elif 'Should ANTs Normalization a \'fast\'' in cell['source']:
                txt = cell['source']
                txt = txt.replace('precise', 'fast')
                cell['source'] = txt
            elif 'Create contrasts (unique and versus rest)' in cell['source']:
                txt = cell['source']
                txt = txt.replace('df[\'condition\']', 'df[\'trial_type\']')
                cell['source'] = txt

            elif 'Specify which classifier to use' in cell['source']:
                txt = cell['source']
                txt = txt.replace('[\'SMLR\', \'LinearNuSVMC\']',
                                  '[\'LinearNuSVMC\']')
                cell['source'] = txt
            elif 'Searchlight sphere radius' in cell['source']:
                txt = cell['source']
                txt = txt.replace(' = 3', ' = 2')
                cell['source'] = txt
            elif 'Number of step size to define' in cell['source']:
                txt = cell['source']
                txt = txt.replace(' = 3', ' = 1000')
                cell['source'] = txt
            elif 'Number of chunks to use' in cell['source']:
                txt = cell['source']
                txt = txt.replace(' = len(runs)', ' = 4')
                cell['source'] = txt
            elif 'Which classifications should be performed' in cell['source']:
                txt = 'content_multivariate[\'tasks\'] = '
                txt += '{u\'fingerfootlips\': [[[u\'Finger\', u\'Foot\'], '
                txt += '[u\'Finger\', u\'Lips\']]]}'
                cell['source'] = txt
            elif 'Number of permutations to indicate group' in cell['source']:
                txt = cell['source']
                txt = txt.replace(' = 100', ' = 10')
                cell['source'] = txt
            elif 'Number of bootstrap samples to be' in cell['source']:
                txt = cell['source']
                txt = txt.replace(' = 100000', ' = 100')
                cell['source'] = txt
            elif 'Number of segments used to compute' in cell['source']:
                txt = cell['source']
                txt = txt.replace(' = 1000', ' = 10')
                cell['source'] = txt
            elif 'Feature-wise probability threshold per' in cell['source']:
                txt = cell['source']
                txt = txt.replace(' = 0.001', ' = 0.1')
                cell['source'] = txt

    # Overwrite notebook 00_spec_preparation with new changes
    nbformat.write(nb_node, nb_path)
    print('JSON specification file creation adapted to demo dataset.')

    # Load notebook 05_analysis_multivariate
    nb_path = '/home/neuro/notebooks/05_analysis_multivariate.ipynb'
    with open(nb_path, 'rb') as nb_file:
        nb_node = nbformat.reads(nb_file.read(), nbformat.NO_CONVERT)

    # Rewrite notebook cells
    for cell in nb_node['cells']:
        if 'code' == cell['cell_type']:
            if 'collects the relevant input files' in cell['source']:
                txt = cell['source']
                txt = txt.replace('glob(template_con.format',
                                  '4 * glob(template_con.format')
                cell['source'] = txt
            elif '==%s\' % imgs_orig.shape[-1]' in cell['source']:
                txt = cell['source']
                txt = txt.replace('==%s\' % imgs_orig.shape[-1]', '!=0\'')
                cell['source'] = txt

    # Overwrite notebook 05_analysis_multivariate with new changes
    nbformat.write(nb_node, nb_path)
    print('Multivariate specification adapted to demo dataset.')


def reduce_comp_time_anat():
    """Change ANTs' normalization command to reduce comp. time on CircleCi."""
    nb_path = '/home/neuro/notebooks/01_preproc_anat.ipynb'

    # Load notebook
    with open(nb_path, 'rb') as nb_file:
        nb_node = nbformat.reads(nb_file.read(), nbformat.NO_CONVERT)

    # Rewrite ANTs' registration command
    for cell in nb_node['cells']:
        if 'code' == cell['cell_type']:
            if 'ANTs Normalization accuracy' in cell['source']:
                txt = cell['source']
                txt = txt.replace('norm_accuracy', 'norm_accuracy = \'fast\'')
                cell['source'] = txt
            if 'Normalize anatomy to ICBM template' in cell['source']:
                txt = cell['source']
                txt = txt.replace('1e-06, 1e-06, 1e-06', '1e-03, 1e-03, 1e-03')
                txt = txt.replace('20, 20, 10', '8, 4, 2')
                cell['source'] = txt

    # Overwrite notebook with new changes
    nbformat.write(nb_node, nb_path)

    print('ANTs Registration simplified.')


if __name__ == '__main__':

    test_version()
    prepare_test_data()
    reduce_comp_time_anat()
    reduce_specs()

    # Notebooks that should be tested in environment 'neuro'
    notebooks = [
        '/home/neuro/notebooks/00_spec_preparation.ipynb',
        '/home/neuro/notebooks/01_preproc_anat.ipynb',
        '/home/neuro/notebooks/02_preproc_func.ipynb',
        '/home/neuro/notebooks/03_analysis_1st-level.ipynb',
        '/home/neuro/notebooks/04_analysis_2nd-level.ipynb',
    ]

    for test in notebooks:
        pytest_cmd = 'pytest --nbval-lax --nbval-cell-timeout 7200 -v -s '
        pytest_cmd += test
        print(pytest_cmd)
        os.system(pytest_cmd)

    # Notebooks that should be tested in environment 'mvpa'
    notebooks = [
        '/home/neuro/notebooks/05_analysis_multivariate.ipynb',
    ]

    for test in notebooks:

        cmd_prep = "sed -i 's/conda-env-mvpa-py/python2/g' "
        cmd_prep += test
        print(cmd_prep)
        os.system(cmd_prep)

        pytest_cmd = '/opt/miniconda-latest/envs/mvpa/bin/pytest '
        pytest_cmd += '--nbval-lax -v -s '
        pytest_cmd += test
        print(pytest_cmd)
        os.system(pytest_cmd)
