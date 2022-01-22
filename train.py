import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import argparse
import os
import time
import torch.optim as optim
import utils
import models.NN

# set up parser for command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d","--data_dir", help = "Data Directory")
parser.add_argument("-o", "--model_output", help = "Directory to save model parameters and output")
parser.add_argument("-e","--num_epochs", type=int, help = "Number of Epochs for Training")
parser.add_argument("-lr","--learning_rate", type=float, help="Learning Rate")

# Example: $ python train.py -d data -o saved_models/benchmark -e 50 -lr 0.01

def train(model, loss_fn, optimizer, X_train, y_train, X_val, y_val, num_epochs, model_output):

    best_val_loss = np.Inf

    train_losses, val_losses = [], []

    t0 = time.time()
    for epoch in range(num_epochs):

        utils.log_progress('[INFO] Training Epoch {}/{}'.format(epoch + 1, num_epochs), model_output)

        # get predictions and compute loss
        pred = model(X_train.float())
        train_loss = loss_fn(pred, y_train.float())

        pred_val = model(X_val.float())
        val_loss = loss_fn(pred_val, y_val.float())

        # update weights
        optimizer.zero_grad()
        train_loss.backward()
        optimizer.step()

        # save loss for plotting
        train_losses.append(train_loss)
        val_losses.append(val_loss)

        # if this is the best model so far, save it
        is_best = val_loss < best_val_loss
        utils.save_checkpoint(model.state_dict(), is_best, model_output)

    utils.log_progress('[INFO] Training runtime: %0.2fs' %(time.time() - t0), model_output)

    # plot learning curve
    utils.plot_loss_curve(train_losses, val_losses, model_output)


if __name__ == '__main__':

    torch.manual_seed(42)

    # get command-line arguments
    args = parser.parse_args()

    # load data
    X_train = utils.load_data(os.path.join(args.data_dir,"X_train_california_2020-2021.csv"),0)
    y_train = utils.load_data(os.path.join(args.data_dir,"y_train_california_2020-2021.csv"),0)

    X_val = utils.load_data(os.path.join(args.data_dir,"X_test_california_2020-2021.csv"),0)
    y_val = utils.load_data(os.path.join(args.data_dir,"y_test_california_2020-2021.csv"),0)

    num_features = X_train.shape[1]
    out_dim = y_train.shape[1]

    # define the model
    model = models.NN.NeuralNet(feat_size=num_features,out_size=out_dim)
    
    # define hyperparameters
    lr = args.learning_rate
    num_epochs = args.num_epochs

    # define loss function and optimizer
    loss_fn = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(),lr=lr)

    log_path = os.path.join(args.model_output, "log.txt")
    print(log_path)
    if (os.path.exists(log_path)):
        os.remove(log_path)

    # run training
    utils.log_progress('[MODEL INFO] Training with {} epochs, lr={}'.format(num_epochs,lr), args.model_output)
    train(model, loss_fn, optimizer, X_train, y_train, X_val, y_val, num_epochs, args.model_output)