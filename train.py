import matplotlib.pyplot as plt
import numpy as np
import torchvision
torchvision.disable_beta_transforms_warning()
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
from my_dataset import MyDataset
from paths import get_preprocessed_images_paths
from seg_model import SegmentationModel
import wandb
import torch.optim as optim
wandb.login()
device = 'cuda' if torch.cuda.is_available() else 'cpu'

config = dict(
    epochs=[5, 10, 20],

)


if __name__ == '__main__':
    train_images, train_masks, val_images, val_masks, test_images, test_masks = get_preprocessed_images_paths()
    batch_size = 64
    train_dataset = MyDataset(train_images, train_masks)
    val_dataset = MyDataset(val_images, val_masks)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=True)


    # Define your model
    model = SegmentationModel(in_channels=3, out_channels=3).to(device)

    wandb.watch(model, log_freq=20)

    # Define your loss function
    criterion = nn.CrossEntropyLoss(weight=torch.tensor([1., 10., 10.])).to(device)



    # Define your optimizer
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer)
    # Define number of epochs
    num_epochs = 10

    # Train the model
    torch.cuda.empty_cache()
    best_val_loss = torch.inf
    tolerance = 2



    for epoch in range(num_epochs):
        # Train
        model.train()
        train_loss = 0
        for idx, (images, masks) in tqdm(enumerate(train_loader), total=len(train_loader)):
            images = images.to(device)
            masks = masks.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

            if idx + 1 % 5 == 0:
                tqdm.write(str(loss.item()))
                fig, ax = plt.subplots(ncols=3)
                output = np.argmax(outputs[0].detach().cpu().numpy(), axis=0)
                mask = masks[0].detach().cpu().numpy()
                mask[mask == 1] = 126
                mask[mask == 2] = 255
                ax[0].imshow(mask, cmap='gray')
                ax[0].axis('off')
                ax[0].set_title('mask')
                pic = np.zeros_like(output)
                pic[output == 1] = 126
                pic[output == 2] = 255
                ax[1].imshow(pic, cmap='gray')
                ax[1].axis('off')
                ax[1].set_title('output')
                image = images[0].detach().cpu().numpy()
                image = np.transpose(image, (1, 2, 0))
                ax[2].imshow(image, cmap='gray')
                ax[2].axis('off')
                ax[2].set_title('input')

                plt.savefig(f'pictures_training/picture_{idx}')
                plt.show()

        train_loss /= len(train_loader)


        # Validate
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for idx, (images, masks) in tqdm(enumerate(val_loader)):
                images = images.to(device)
                masks = masks.to(device)
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()

                scheduler.step(loss)
                if idx + 1 % 5 == 0:
                    tqdm.write(str(loss.item()))
                    fig, ax = plt.subplots(ncols=3)
                    output = np.argmax(outputs[0].detach().cpu().numpy(), axis=0)
                    mask = masks[0].detach().cpu().numpy()
                    mask[mask == 1] = 126
                    mask[mask == 2] = 255
                    ax[0].imshow(mask, cmap='gray')
                    ax[0].axis('off')
                    ax[0].set_title('mask')
                    pic = np.zeros_like(output)
                    pic[output == 1] = 126
                    pic[output == 2] = 255
                    ax[1].imshow(pic, cmap='gray')
                    ax[1].axis('off')
                    ax[1].set_title('output')
                    image = images[0].detach().cpu().numpy()
                    image = np.transpose(image, (1, 2, 0))
                    ax[2].imshow(image, cmap='gray')
                    ax[2].axis('off')
                    ax[2].set_title('input')
                    plt.savefig(f'pictures_training/yay{idx}')
                    plt.show()

        val_loss /= len(val_loader)

        if val_loss <= best_val_loss:
            tolerance = 2
            best_val_loss = val_loss
            tqdm.write(f'Saving the best model')
            torch.save(model.state_dict(), 'best_model.pt')
        else:
            tolerance -= 1
            if tolerance <= 0:
                break

        # Print progress
        print(f"Epoch [{epoch + 1}/{num_epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

