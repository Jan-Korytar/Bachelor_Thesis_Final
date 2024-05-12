import os
from glob import glob

from matplotlib import pyplot as plt
import numpy as np
import yaml

def plot_input_mask_output(img_input, mask, output, idx, epoch):
    """
    Plot input, mask, and output images side by side for visualization during training.

    Parameters:
    - img_input (torch.Tensor): Input image tensor.
    - mask (torch.Tensor): Mask tensor.
    - output (torch.Tensor): Output tensor.
    - idx (int): Index for saving the plot.

    Returns:
    None
    """
    fig, ax = plt.subplots(ncols=3)

    # Process mask
    mask = mask.detach().cpu().numpy()
    mask[mask == 1] = 126
    mask[mask == 2] = 255
    ax[2].imshow(mask, cmap='gray')
    ax[2].axis('off')
    ax[2].set_title('Mask')

    # Process output
    output = np.argmax(output.detach().cpu().numpy(), axis=0)
    pic = np.zeros_like(output)
    pic[output == 1] = 126
    pic[output == 2] = 255
    ax[1].imshow(pic, cmap='gray')
    ax[1].axis('off')
    ax[1].set_title(f'Output image')

    # Process input
    image = img_input.detach().cpu().numpy()
    image = np.transpose(image, (1, 2, 0))
    ax[0].imshow(image, cmap='gray')
    ax[0].axis('off')
    ax[0].set_title(f'Input Image')

    # Display and save the plot
    os.makedirs('pictures_training/seq', exist_ok=True)
    fig.suptitle(f'Epoch: {epoch}, step: {idx}')
    plt.tight_layout()
    plt.savefig(f'pictures_training/seq/picture_{epoch}_{idx}')
    plt.close('all')







def get_preprocessed_images_paths(size=256, file_extension_img='.jpg', file_extension_mask='.bmp', refresh_search=False):
    if refresh_search:

        with open('config.yaml', 'r') as file:
            file = yaml.safe_load(file)
            paths = file['paths']
            images_path = paths['data_path']

        train_images_path = os.path.join(images_path, f'preprocessed/train/input/{size}/**/*{file_extension_img}')
        train_masks_path = os.path.join(images_path, f'preprocessed/train/labels/{size}/**/*{file_extension_mask}')
        train_images_cropped_path = os.path.join(images_path,
                                                 f'preprocessed/train/input_cropped/{size}/**/*{file_extension_img}')
        train_masks_cropped_path = os.path.join(images_path,
                                                f'preprocessed/train/labels_cropped/{size}/**/*{file_extension_mask}')
        val_images_path = os.path.join(images_path, f'preprocessed/validation/input/{size}/**/*{file_extension_img}')
        val_masks_path = os.path.join(images_path, f'preprocessed/validation/labels/{size}/**/*{file_extension_mask}')
        test_images_path = os.path.join(images_path, f'preprocessed/test/input/{size}/**/*{file_extension_img}')
        test_masks_path = os.path.join(images_path, f'preprocessed/test/labels/{size}/**/*{file_extension_mask}')

        train_images = sorted(glob(train_images_path, recursive=True), key=lambda x: os.path.basename(x))
        train_masks = sorted(glob(train_masks_path, recursive=True), key=lambda x: os.path.basename(x))
        train_images_cropped_path = sorted(glob(train_images_cropped_path, recursive=True), key=lambda x: os.path.basename(x))
        train_masks_cropped_path = sorted(glob(train_masks_cropped_path, recursive=True), key=lambda x: os.path.basename(x))
        val_images = sorted(glob(val_images_path, recursive=True),
                            key=lambda x: os.path.basename(x))
        val_masks = sorted(glob(val_masks_path, recursive=True),
                            key=lambda x: os.path.basename(x))
        test_images = sorted(glob(test_images_path, recursive=True),
                            key=lambda x: os.path.basename(x))
        test_masks = sorted(glob(test_masks_path, recursive=True),
                            key=lambda x: os.path.basename(x))

        paths_dict = {
            'train_images': train_images,
            'train_masks': train_masks,
            'train_images_cropped': train_images_cropped_path,
            'train_masks_cropped': train_masks_cropped_path,
            'val_images': val_images,
            'val_masks': val_masks,
            'test_images': test_images,
            'test_masks': test_masks
        }

        with open('preprocessed_paths.yaml', 'w') as yaml_file:
            yaml.dump(paths_dict, yaml_file)
    else:
        with open('preprocessed_paths.yaml', 'r') as yaml_file:
            paths_dict = yaml.safe_load(yaml_file)

        return (
            paths_dict['train_images'], paths_dict['train_masks'],
            paths_dict['train_images_cropped'], paths_dict['train_masks_cropped'],
            paths_dict['val_images'], paths_dict['val_masks'],
            paths_dict['test_images'], paths_dict['test_masks']
        )

    return train_images, train_masks, train_images_cropped_path, train_masks_cropped_path, val_images, val_masks, test_images, test_masks
