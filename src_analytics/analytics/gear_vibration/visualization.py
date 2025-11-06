import io
import pandas as pd
import torch.nn as nn
import seaborn as sns
import wandb
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import torch
from torch.utils.data import Dataset
from scipy.signal import welch
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.decomposition import PCA


def plot_feature_importance(features: np.ndarray,
                            importance: np.ndarray,
                            model_name: str = '',
                            log: bool = True,
                            figsize: tuple = (8, 8)) -> plt.figure:
  features = features[np.argsort(importance)]
  importance = importance[np.argsort(importance)]
  df_fi = pd.DataFrame({'feature': features, 'importance': importance})
  fig = plt.figure(figsize=figsize)
  ax = fig.add_subplot(1, 1, 1)
  plt.title(f'Feature Importances: {model_name}')
  plt.barh(range(len(importance)), importance)
  plt.yticks(range(len(importance)), features)
  plt.xlabel('Relative Importance')
  plt.grid()
  if log:
    wandb.log({'feature_importance_plot': wandb.Image(plt), 'feature_importance_table': wandb.Table(dataframe=df_fi)})
  return plt


def confusion_matrix_nn(model: nn.Module,
                        dataloader: Dataset,
                        class_names: list[tuple],
                        device: str = 'cpu',
                        figsize: tuple = (8, 6)) -> plt.Figure:
  class_names = [label[0] if isinstance(label, tuple) else label for label in class_names]
  model.eval()
  all_preds = []
  all_labels = []
  with torch.no_grad():
    for inputs, labels in dataloader:
      inputs = inputs.to(device)
      labels = labels.to(device)
      outputs = model(inputs)
      _, preds = torch.max(outputs, 1)
      all_preds.extend(preds.cpu().numpy())
      all_labels.extend(labels.cpu().numpy())
  cm = confusion_matrix(all_labels, all_preds, labels=range(len(class_names)))
  disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
  fig = plt.figure(figsize=figsize)
  disp.plot(cmap='Blues', xticks_rotation=45)
  plt.title('Confusion Matrix')
  plt.tight_layout()
  return plt


def plot_confusion_matrix(y_test: np.ndarray,
                          y_pred: np.ndarray,
                          fault_code: pd.Index,
                          model_name: str = '',
                          log: bool = True,
                          figsize=(6, 4)) -> plt.figure:
  classes = [label[0] if isinstance(label, tuple) else label for label in fault_code]
  cm_svm = confusion_matrix(y_test, y_pred)
  plt.figure(figsize=figsize)
  sns.heatmap(cm_svm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
  plt.xlabel('Predicted Label')
  plt.ylabel('True Label')
  plt.title(f'Confusion Matrix: {model_name}')
  if log:
    wandb.log({'accuracy': accuracy_score(y_test, y_pred)})
    classification_dict = classification_report(y_test, y_pred, output_dict=True)
    for label, scores in classification_dict.items():
      if isinstance(scores, dict):
        for metric, value in scores.items():
          wandb.log({f'class_report/{label}/{metric}': value})
      else:
        wandb.log({f'class_report/{label}': scores})
    wandb.log({'confusion_matrix': wandb.Image(plt)})
  return plt


def bar_plot(df: pd.DataFrame, height: int = 4, aspect: int = 2):
  df_sorted = df.sort_values('speed')
  plot = sns.catplot(x='speed',
                     y='sensor1',
                     hue='fault',
                     row='load',
                     data=df_sorted,
                     kind='box',
                     height=height,
                     aspect=aspect)
  plot = sns.catplot(x='speed',
                     y='sensor2',
                     hue='fault',
                     row='load',
                     data=df_sorted,
                     kind='box',
                     height=height,
                     aspect=aspect)
  plot.set_titles('Sensor1 Distribution by Speed, Load, and Fault')


def bar_plot_adv(df: pd.DataFrame, height: int = 4, aspect: int = 2):
  df_sorted = df.sort_values('speed')
  df_melt = pd.melt(df_sorted,
                    id_vars=['speed', 'load', 'fault'],
                    value_vars=['sensor1', 'sensor2'],
                    var_name='sensor',
                    value_name='measurement')

  df_melt['speed'] = df_melt['speed'].astype(str)
  df_melt['load'] = df_melt['load'].astype(str)
  sns.set_style('whitegrid')
  g = sns.catplot(x='speed',
                  y='measurement',
                  hue='fault',
                  col='sensor',
                  row='load',
                  data=df_melt,
                  kind='box',
                  height=height,
                  aspect=aspect,
                  palette='Set2')
  g.set_axis_labels('Speed [rev/sec]', 'Vibration [mm]')
  g.set_titles('{row_name} Load - {col_name}')
  g.figure.suptitle('Sensor Distribution by Speed, Load, and Fault', fontsize=16)


def distribution(data: pd.Series, ax: plt.Axes, title: str = None, xlim: tuple = (2.3, 2.6)) -> plt.Axes:
  mean = data.mean()
  median = data.median()
  skewness = data.skew()
  kurtosis = data.kurtosis()
  sns.histplot(data, kde=True, stat='density', bins=30, color='skyblue', edgecolor='black', alpha=0.5, ax=ax)
  sns.kdeplot(data, fill=True, alpha=0.3, linewidth=2, ax=ax)
  if xlim:
    ax.set_xlim(xlim)
  if title:
    ax.set_title(title, fontsize=12)
  ax.set_xlabel('Vibration Amplitude (mm)', fontsize=11)
  ax.set_ylabel('Density', fontsize=11)
  stats_text = (f'Mean: {mean:.2f}\n'
                f'Median: {median:.2f}\n'
                f'Skewness: {skewness:.2f}\n'
                f'Kurtosis: {kurtosis:.2f}')
  ax.text(0.95,
          0.95,
          stats_text,
          transform=ax.transAxes,
          fontsize=11,
          verticalalignment='top',
          horizontalalignment='right',
          bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
  return ax


def plot_distributions(df: pd.DataFrame, speed: float, load: float) -> plt:
  faults = df['fault'].unique()
  sensors = ['sensor1', 'sensor2']
  num_faults = len(faults)
  subset = df[(df['speed'] == speed) & (df['load'] == load)]
  xlims = {sensor: (subset[sensor].min(), subset[sensor].max()) for sensor in sensors}
  _, axes = plt.subplots(nrows=num_faults, ncols=2, figsize=(12, 2.5 * num_faults))
  for row_index, fault in enumerate(faults):
    for col_idx, sensor in enumerate(sensors):
      data = subset[subset['fault'] == fault][sensor]
      title = f'{sensor.capitalize()}\nFault: {fault}, {speed} rev/sec, {load} Nm'
      distribution(data, ax=axes[row_index, col_idx], title=title, xlim=xlims[sensor])
  plt.tight_layout()
  return plt


def time_series_plot(df: pd.DataFrame,
                     fault: str,
                     speed: float,
                     figsize=(8, 4),
                     window_size: int = 100) -> list[plt.axis]:
  ''' Plot time series data for a given fault type, speed and window size

      Parameters
      ----------
      df: Time series data
      fault: Fault type
      speed: Speed value
      figsize: Figure size
      window_size: Window size in milliseconds
  '''
  axes = []
  for load_value, group in df.groupby('load'):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    group = group.set_index('timestamp')
    group.index = pd.to_datetime(group.index)
    start_time = group.index.min()
    end_time = start_time + pd.Timedelta(milliseconds=window_size)
    group_filt = group[start_time:end_time]
    ax.plot(group_filt.index, group_filt['sensor1'], label='sensor1')
    ax.plot(group_filt.index, group_filt['sensor2'], label='sensor2')
    ax.set_ylabel('Vibration [mm]')
    ax.set_xlabel('Time')
    ax.set_title(f'{fault}/ Load: {load_value} / Speed: {speed}')
    ax.grid(True)
    ax.legend()
    axes.append(ax)
  return axes


def plot_mutual_information(df: pd.DataFrame):
  X = df[['sensor1', 'sensor2', 'speed', 'load']]
  y = df['fault']
  mutual_info = mutual_info_classif(X, y, discrete_features=False)
  feature_importance = pd.Series(mutual_info, index=X.columns)
  plt.figure(figsize=(5, 2))
  feature_importance.plot(kind='barh', color='skyblue')
  plt.xlabel('Mutual Information')
  plt.title('Mutual Information between Features and Fault')
  plt.tight_layout()
  plt.show()


def plot_fft(df: pd.DataFrame, fault: str, speed: float, figsize=(12, 4)):
  df = df.sort_values(by='timestamp')
  ts = (df['timestamp'].iloc[1] - df['timestamp'].iloc[0]).total_seconds()
  fs = 1 / ts
  for load_value, group in df.groupby('load'):
    fig, axs = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(f'FFT (fault={fault}, speed={speed} rev/sec, Load={load_value} Nm)', fontsize=14)
    for ax, sensor in zip(axs, ['sensor1', 'sensor2']):
      signal = group[sensor] - np.mean(group[sensor])
      n = len(signal)
      fft_vals = np.fft.fft(signal)
      freqs = np.fft.fftfreq(n, d=1 / fs)
      mask = freqs >= 0
      freqs = freqs[mask]
      magnitude = np.abs(fft_vals[mask])
      max_freq = freqs[np.argmax(magnitude)]
      ax.axvline(max_freq, color='red', linestyle='--', label=f'Peak Frequency: {max_freq:.2f} Hz')
      ax.legend()
      ax.plot(freqs, magnitude, color='royalblue', lw=1.5)
      ax.set_xlabel('Frequency (Hz)', fontsize=11)
      ax.set_ylabel('Magnitude', fontsize=11)
      ax.set_title(sensor, fontsize=11)
      ax.grid(True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def plot_psd(df: pd.DataFrame, speed: float, figsize=(12, 4), sensors: list[str] = None):
  sensors = ['sensor1', 'sensor2'] if sensors is None else sensors
  df_filt = df[df['speed'] == speed]
  if df_filt.empty:
    print(f'No data found for the given speed={speed}')
    return
  loads = sorted(df_filt['load'].unique())
  n_loads = len(loads)
  _, axs = plt.subplots(n_loads, len(sensors), figsize=(figsize[0], figsize[1] * n_loads), sharex=True, sharey=True)
  if n_loads == 1:
    axs = axs.reshape(1, -1)
  for i, load in enumerate(loads):
    df_load = df_filt[df_filt['load'] == load]
    for j, sensor in enumerate(sensors):
      ax = axs[i, j]
      for fault, group in df_load.groupby('fault'):
        group = group.sort_values(by='timestamp')
        sensor_signal = group[sensor] - np.mean(group[sensor])
        ts = (group['timestamp'].iloc[1] - group['timestamp'].iloc[0]).total_seconds()
        fs = 1 / ts
        f_psd, psd_values = welch(sensor_signal, fs=fs, nperseg=1024, average='median')
        ax.semilogy(f_psd, psd_values, label=f'Fault: {fault}')
      ax.set_title(f'{sensor} (Load: {load} Nm, Speed: {speed} rev/sec)')
      ax.legend()
      ax.grid(True)
      if i == n_loads - 1:
        ax.set_xlabel('Frequency [Hz]')
      if j == 0:
        ax.set_ylabel('PSD [mm^2/Hz]')
  plt.tight_layout()
  plt.show()


def plot_pca_2d(df: pd.DataFrame, labels: pd.Series, figsize: tuple = (12, 8)) -> plt.figure:
  colormap = plt.cm.get_cmap('tab10', len(labels.unique()))
  pca = PCA(n_components=2)
  pca_components = pca.fit_transform(df)
  df_pca = pd.DataFrame(pca_components, columns=['PC1', 'PC2'])
  plt.figure(figsize=figsize)
  for i, label in enumerate(labels.unique()):
    indices = labels == label
    plt.scatter(df_pca.loc[indices, 'PC1'], df_pca.loc[indices, 'PC2'], c=colormap(i), label=label, alpha=0.5)
  plt.title('PCA Analysis (2D)')
  plt.xlabel('PC 1')
  plt.ylabel('PC 2')
  handles = [mlines.Line2D([], [], marker='o', color='w', markerfacecolor=colormap(i), markersize=10, label=label) for i, label in enumerate(labels.unique())] # yapf: disable
  plt.legend(handles=handles, title='Fault Type')
  plt.grid()
  return plt


def plot_pca_3d(df: pd.DataFrame, labels: pd.Series, figsize: tuple = (12, 12)) -> plt.axis:
  colormap = plt.cm.get_cmap('tab10', len(labels.unique()))
  pca = PCA(n_components=3)
  pca_components = pca.fit_transform(df)
  print(f'Explained variance ratio: {pca.explained_variance_ratio_}')
  df_pca = pd.DataFrame(pca_components, columns=['PC1', 'PC2', 'PC3'])
  fig = plt.figure(figsize=figsize)
  ax = fig.add_subplot(111, projection='3d')
  for i, label in enumerate(labels.unique()):
    indices = labels == label
    ax.scatter(df_pca.loc[indices, 'PC1'],
               df_pca.loc[indices, 'PC2'],
               df_pca.loc[indices, 'PC3'],
               c=[colormap(i)],
               label=label,
               alpha=0.5)
  ax.set_title('PCA Analysis (3D)')
  ax.set_xlabel('PC 1')
  ax.set_ylabel('PC 2')
  ax.set_zlabel('PC 3')
  handles = [mlines.Line2D([], [], marker='o', color='w', markerfacecolor=colormap(i), markersize=10, label=label)for i, label in enumerate(labels.unique())] # yapf: disable
  ax.legend(handles=handles, title='Fault Type')
  return ax
