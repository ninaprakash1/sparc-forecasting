import pandas as pd
import torch
import matplotlib.pyplot as plt
import os
import shutil

def load_data(filename,index_col=0):
    return torch.tensor(pd.read_csv(filename,index_col=[index_col]).values)

def plot_loss_curve(train_losses, val_losses, model_output):
    plt.figure()
    plt.plot(train_losses)
    plt.plot(val_losses)
    plt.xlabel('Epoch')
    plt.ylabel('MSE Loss')
    plt.legend(['Train','Validation'])
    plt.savefig(os.path.join(model_output,"loss_curve.png"))

def log_progress(text, model_output):
    if not os.path.exists(model_output):
        print("[INFO] Checkpoint Directory does not exist! Making directory {}".format(model_output))
        os.mkdir(model_output)
    path = os.path.join(model_output,'log.txt')
    if not os.path.exists(path):
        with open(path,'w') as file:
            file.write(text + '\n')
    else:
        with open(path,'a+') as file:
            file.write(text + '\n')
    print(text)

# Note: The following function was sourced from Stanford CS 230's Computer
# Vision project code examples, located at:
# https://github.com/cs230-stanford/cs230-code-examples
def save_checkpoint(state, is_best, checkpoint):
    """
    Saves model and training parameters at checkpoint + 'last.pth.tar'.
    If is_best==True, also saves checkpoint + 'best.pth.tar'
    Args:
        state: (dict) contains model's state_dict, may contain other keys such as epoch, optimizer state_dict
        is_best: (bool) True if it is the best model seen till now
        checkpoint: (string) folder where parameters are to be saved
    """
    filepath = os.path.join(checkpoint, 'last.pth.tar')
    if not os.path.exists(checkpoint):
        print("[INFO] Checkpoint Directory does not exist! Making directory {}".format(checkpoint))
        os.mkdir(checkpoint)
    torch.save(state, filepath)
    if is_best:
        shutil.copyfile(filepath, os.path.join(checkpoint, 'best.pth.tar'))


# Note: The following function was sourced from Stanford CS 230's Computer
# Vision project code examples, located at:
# https://github.com/cs230-stanford/cs230-code-examples
def load_checkpoint(checkpoint, model, optimizer=None):
    """
    Loads model parameters (state_dict) from file_path.
    If optimizer is provided, loads state_dict of optimizer assuming it is present in checkpoint.
    Args:
        checkpoint: (string) filename which needs to be loaded
        model: (torch.nn.Module) model for which the parameters are loaded
        optimizer: (torch.optim) optional: resume optimizer from checkpoint
    """
    if not os.path.exists(checkpoint):
        raise("[INFO] Weights file doesn't exist {}".format(checkpoint))
    checkpoint = torch.load(checkpoint)
    model.load_state_dict(checkpoint['state_dict'])

    if optimizer:
        optimizer.load_state_dict(checkpoint['optim_dict'])

    return checkpoint