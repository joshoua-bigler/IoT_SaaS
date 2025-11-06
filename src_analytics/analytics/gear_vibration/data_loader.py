import pandas as pd
import torch
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset


def load_data(path: Path) -> tuple[dict, pd.DataFrame]:
  ''' Load vibration dataset from CSV files in the given path. 
  
      Data Source 
      -----------
      https://www.kaggle.com/datasets/hieudaotrung/gear-vibration/data
  '''
  csv_files = list(path.glob('*.csv'))
  data = {}
  for file in csv_files:
    df = pd.read_csv(file)
    df.rename(columns={'time_x': 'timestamp'}, inplace=True)
    df.rename(columns={'gear_fault_desc': 'fault'}, inplace=True)
    df.rename(columns={'load_value': 'load'}, inplace=True)
    df.rename(columns={'speedSet': 'speed'}, inplace=True)
    df['speed'] = df['speed'].round(2)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.dropna()
    df.set_index('timestamp', inplace=True)
    df = df.dropna().reset_index()
    df = df.sort_values(by='timestamp').reset_index(drop=True)
    data[df['fault'][0]] = df
  df = pd.concat(data.values())
  df = df.sort_values(by='timestamp').reset_index(drop=True)
  return data, df


class GearVibrationDataset(Dataset):

  def __init__(self, features: pd.DataFrame | np.ndarray, labels: np.ndarray):
    if isinstance(features, pd.DataFrame):
      self.features = torch.tensor(features.to_numpy(), dtype=torch.float32)
    elif isinstance(features, np.ndarray):
      self.features = torch.tensor(features, dtype=torch.float32)
    self.labels = torch.tensor(labels, dtype=torch.long)

  def __len__(self):
    return len(self.features)

  def __getitem__(self, idx) -> tuple[torch.Tensor, torch.Tensor]:
    x = self.features[idx]
    y = self.labels[idx]
    return x.permute(1, 0), y

class GearVibrationLstmDataset(Dataset):

  def __init__(self, features: pd.DataFrame | np.ndarray, labels: np.ndarray):
    if isinstance(features, pd.DataFrame):
      self.features = torch.tensor(features.to_numpy(), dtype=torch.float32)
    elif isinstance(features, np.ndarray):
      self.features = torch.tensor(features, dtype=torch.float32)
    self.labels = torch.tensor(labels, dtype=torch.long)

  def __len__(self):
    return len(self.features)

  def __getitem__(self, idx) -> tuple[torch.Tensor, torch.Tensor]:
    x = self.features[idx]
    y = self.labels[idx]
    return x, y
