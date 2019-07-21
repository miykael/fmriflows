import os
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.ndimage import label, binary_fill_holes
from nilearn.image import load_img, resample_to_img
from matplotlib import pyplot as plt
sns.set_style('darkgrid')
plt.style.use('seaborn-colorblind')

# Specify output folder
res_path = 'res_08_euler'
if not os.path.exists(res_path):
    os.makedirs(res_path)


def get_euler_stats(in_file, method, min_clust_size=1, vmin=-5, vmax=5,
                    steps=100, con='_t_'):

    # Load Data
    img = load_img(in_file)
    data = img.get_data()

    # Prepare mask
    if method == 'spm':
        img_mask = load_img('templates/spm_TPM_1.5mm_mask.nii.gz')
    else:
        img_mask = load_img(
            'templates/mni_icbm152_nlin_asym_09c_1.0mm_mask.nii.gz')
    mask = resample_to_img(img_mask, in_file).get_data() >= 0.5

    # Mask Data
    data *= mask

    # Prepare variables
    if '_F_' in con:
        vmin = 0
        vmax = 8
    X = np.linspace(vmin, vmax, steps)
    euler_chars = []
    cluster_count = []
    max_extent = []

    for x in X:

        # Threshold stat image
        if x < 0:
            mask_bin = 1. * (data < x)
        else:
            mask_bin = 1. * (data >= x)

        # Fill holes in the binary mask
        mask_filled = 1. * binary_fill_holes(mask_bin)

        # Extract cluster info
        labels, ncluster = label(mask_bin)

        # Compute euler characteristics
        _, holes = label(mask_filled - mask_bin)
        euler_chars.append(ncluster - holes)

        # Count clusters in volume
        sum_cluster = np.sum(
            [np.sum(labels == i) >= min_clust_size for i in np.unique(labels)])
        cluster_count.append(sum_cluster)

        # Save size of biggest cluster in volume
        label_ids = np.unique(labels)
        if len(label_ids) == 1:
            max_extent.append(0)
        else:
            max_size = np.max([np.sum(labels == n) for n in label_ids[1:]])
            max_extent.append(max_size)

    return euler_chars, cluster_count, max_extent, X


# Specify contrasts
contrasts = ['con_t_av_v']

# Specify methods to compare
methods = ['fmriflows_5', 'fmriflows_none', 'fmriprep', 'fsl', 'spm']

# Range of exploration
vmin, vmax, steps = (-8, 8, 128)

# Minimum cluster size for cluster count
min_clust_size = 1

# Create figures
for con in contrasts:

    file_list = [
        'res_05_2ndlevel/nifti_group_%s_%s.nii.gz' % (con, c) for c in methods]

    res_euler = []
    res_cluster = []
    res_size = []
    for i, f in enumerate(file_list):
        euler, cluster, max_extent, X = get_euler_stats(
            f, methods[i], min_clust_size, vmin, vmax, steps, con)
        res_euler.append(euler)
        res_cluster.append(cluster)
        res_size.append(max_extent)

        print(con, f, 'done.')

    res_euler = np.array(res_euler)
    res_cluster = np.array(res_cluster)
    res_size = np.array(res_size)

    # Plot euler characteristics
    df = pd.DataFrame(res_euler.T, X, columns=methods)
    plt.figure(figsize=(6, 3))
    ax = sns.lineplot(data=df, dashes=False, linewidth=2.0)
    ax.set(xlabel='Threshold', ylabel='Euler Characteristics', title=con, yscale="log")
    plt.tight_layout()
    plt.savefig(res_path + '/plot_euler_%s.svg' % con)

    # Plot cluster count
    df = pd.DataFrame(res_cluster.T, X, columns=methods)
    plt.figure(figsize=(6, 3))
    ax = sns.lineplot(data=df, dashes=False, linewidth=2.0)
    ax.set(xlabel='Threshold', ylabel='Cluster Count', title=con, yscale="log")
    plt.tight_layout()
    plt.savefig(res_path + '/plot_cluster_%s.svg' % con)

    # Plot size of biggest cluster
    df = pd.DataFrame(res_size.T, X, columns=methods)
    plt.figure(figsize=(6, 3))
    ax = sns.lineplot(data=df, dashes=False, linewidth=2.0)
    ax.set(xlabel='Threshold', ylabel='Size of Biggest Cluster', title=con, yscale="log")
    plt.tight_layout()
    plt.savefig(res_path + '/plot_size_%s.svg' % con)
