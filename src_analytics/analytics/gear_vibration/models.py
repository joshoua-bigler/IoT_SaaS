import torch.nn as nn
import torch


class LstmClassifier(nn.Module):

  def __init__(self, input_size: int, hidden_size: int, num_layers: int, out_features: int):
    super().__init__()
    self.lstm = nn.LSTM(input_size=input_size,
                        hidden_size=hidden_size,
                        num_layers=num_layers,
                        batch_first=True,
                        bidirectional=True)
    self.dropout = nn.Dropout(0.3)
    self.fc = nn.Linear(hidden_size * 2, out_features)

  def forward(self, x):
    out, _ = self.lstm(x)
    out = out[:, -1, :]
    out = self.dropout(out)
    return self.fc(out)


class NnClassifier(nn.Module):
  ''' Fully connected neural network for time series classification.'''

  def __init__(self, input_dim: int, output_dim: int, dropout: float = 0.3):
    super().__init__()
    self.model = nn.Sequential(
        nn.Linear(input_dim, 128),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(128, 128),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(64, output_dim),
    )

  def forward(self, x: torch.Tensor) -> torch.Tensor:
    return self.model(x)


class CnnClassifier(nn.Module):
  ''' Convolutional Neural Network for time series classification.'''

  def __init__(self, in_channels: int, out_features: int, input_length: int):
    super().__init__()
    self.features = nn.Sequential(
        nn.Conv1d(in_channels, 64, kernel_size=5, padding=2),
        nn.BatchNorm1d(64),
        nn.ReLU(),
        nn.MaxPool1d(2),
        nn.Dropout(0.2),
        nn.Conv1d(64, 128, kernel_size=3, padding=1),
        nn.BatchNorm1d(128),
        nn.ReLU(),
        nn.MaxPool1d(2),
        nn.Dropout(0.2),
        nn.Conv1d(128, 256, kernel_size=3, padding=1),
        nn.BatchNorm1d(256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Conv1d(256, 256, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool1d(1),
    )
    self.classifier = nn.Sequential(nn.Flatten(), nn.Dropout(0.3), nn.Linear(256, out_features))

  def forward(self, x):
    x = self.features(x)
    return self.classifier(x)
