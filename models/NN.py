import torch.nn as nn

class NeuralNet(nn.Module):
    """
    Define the model to train the concatenated features.
    """

    def __init__(self, feat_size=38, out_size=312):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(

            # Layer 1
            nn.Linear(in_features=38, out_features=64),
            nn.ReLU(),

            # Layer 2
            nn.Linear(in_features=64, out_features=128),
            nn.ReLU(),

            # Layer 3
            nn.Linear(in_features=128, out_features=256),
            nn.ReLU(),

            # Layer 4
            nn.Linear(in_features=256, out_features=out_size)
        )

    def forward(self, x):
        return self.model(x)