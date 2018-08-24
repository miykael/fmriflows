import nbformat

# This script should be run before committing changes in the notebooks,
# as it resets cell counts and deletes cell outputs.


def read_nb(nb_filename):
    """Reads notebooks"""

    with open(nb_filename, 'rb') as nb_file:
        txt = nb_file.read()

    return nbformat.reads(txt, nbformat.NO_CONVERT)


def clean_cells(nb_node):
    """Deletes any outputs and resets cell count"""

    for cell in nb_node['cells']:
        if 'code' == cell['cell_type']:
            if 'outputs' in cell:
                cell['outputs'] = []
            if 'execution_count' in cell:
                cell['execution_count'] = None

    return nb_node


def write_nb(nb_node, nb_filename):
    """Rewrites notebook"""
    nbformat.write(nb_node, nb_filename)


if __name__ == '__main__':

    for nb in [
            'notebooks/01_preproc_anat.ipynb',
            'notebooks/02_preproc_func.ipynb'
    ]:

        # Read Notebook
        nb_content = read_nb(nb)

        # Clean Notebook
        processed_node = clean_cells(nb_content)

        # Rewrite Notebook
        write_nb(processed_node, nb)
