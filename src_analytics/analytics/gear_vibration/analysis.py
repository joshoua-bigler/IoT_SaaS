import numpy as np
import pandas as pd
from scipy.signal import welch
from sklearn.preprocessing import StandardScaler
# local
from analytics.utils import ts_to_frequency


def normalize_features(df: pd.DataFrame) -> pd.DataFrame:
  ''' Normalize the features in the DataFrame using StandardScaler. '''
  scaler = StandardScaler()
  feature_names = list(df.columns)
  df = scaler.fit_transform(df)
  df = pd.DataFrame(df, columns=feature_names)
  return df


def normalize_train_test(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
  ''' Normalize the training and testing features using StandardScaler. '''
  scaler = StandardScaler()
  feature_names = list(X_train.columns)
  X_train = scaler.fit_transform(X_train)
  X_test = scaler.transform(X_test)
  X_train = pd.DataFrame(X_train, columns=feature_names)
  X_test = pd.DataFrame(X_test, columns=feature_names)
  return X_train, X_test


def compute_freq_features(signal_data: np.ndarray, fs: float) -> dict:
  ''' Compute frequency domain features for the given signal data.

      Parameters
      ----------
      signal_data:  1D numpy array of signal data
      fs:           Sampling frequency in Hz

      Returns
      -------
      Dictionary containing frequency domain features:
      - peak_freq:          Frequency of the peak in the FFT spectrum
      - spectral_centroid:  Spectral centroid of the signal
      - energy:             Energy of the signal
      - peak_power:         Peak power of the signal
      - spectral_bandwidth: Spectral bandwidth of the signal
  '''
  signal_adjusted = signal_data - np.mean(signal_data)
  fft_vals = np.fft.fft(signal_adjusted)
  fft_freq = np.fft.fftfreq(len(signal_adjusted), d=1 / fs)
  pos_mask = fft_freq >= 0
  fft_vals = fft_vals[pos_mask]
  fft_freq = fft_freq[pos_mask]
  magnitude = np.abs(fft_vals)
  peak_freq = fft_freq[np.argmax(magnitude)]
  spectral_centroid = np.sum(fft_freq * magnitude) / np.sum(magnitude)
  energy = np.sum(magnitude**2) / len(magnitude)
  f, Pxx = welch(signal_adjusted, fs=fs, nperseg=len(signal_adjusted))
  peak_power = f[np.argmax(Pxx)]
  spectral_bandwidth = np.sqrt(np.sum(((f - spectral_centroid)**2) * Pxx) / np.sum(Pxx))
  top5_indices = np.argsort(Pxx)[-5:]
  top5_freqs = np.sort(f[top5_indices])
  features = {
      'peak_freq': peak_freq,
      'spectral_centroid': spectral_centroid,
      'energy': energy,
      'peak_power': peak_power,
      'spectral_bandwidth': spectral_bandwidth
  }
  for i, freq in enumerate(top5_freqs, 1):
    features[f'top_freq_{i}'] = freq
  return features


def compute_stats(df: pd.DataFrame, fs: float) -> pd.DataFrame:
  ''' Compute time domain and frequency domain features for the given DataFrame.
      The DataFrame should contain 'sensor1', 'sensor2', 'load', and 'speed' columns.

      Parameters
      ----------
      df: Data
      fs: Sampling frequency in Hz
  '''
  sensor1_mean = df['sensor1'].mean()
  sensor1_std = df['sensor1'].std()
  sensor1_skew = df['sensor1'].skew()
  sensor1_kurt = df['sensor1'].kurt()
  sensor1_rms = (df['sensor1']**2).mean()**0.5
  sensor1_ptp = df['sensor1'].max() - df['sensor1'].min()
  sensor2_mean = df['sensor2'].mean()
  sensor2_std = df['sensor2'].std()
  sensor2_skew = df['sensor2'].skew()
  sensor2_kurt = df['sensor2'].kurt()
  sensor2_mean = (df['sensor2']**2).mean()**0.5
  sensor2_rms = (df['sensor2']**2).mean()**0.5
  sensor2_ptp = df['sensor2'].max() - df['sensor2'].min()
  freq_features_sensor1 = compute_freq_features(df['sensor1'].values, fs)
  freq_features_sensor2 = compute_freq_features(df['sensor2'].values, fs)
  features = pd.DataFrame({
      # time domain features
      'sensor1_mean': [sensor1_mean],
      'sensor1_std': [sensor1_std],
      'sensor1_skew': [sensor1_skew],
      'sensor1_kurt': [sensor1_kurt],
      'sensor1_rms': [sensor1_rms],
      'sensor1_ptp': [sensor1_ptp],
      'sensor2_mean': [sensor2_mean],
      'sensor2_std': [sensor2_std],
      'sensor2_skew': [sensor2_skew],
      'sensor2_kurt': [sensor2_kurt],
      'sensor2_rms': [sensor2_rms],
      'sensor2_ptp': [sensor2_ptp],
      # frequecy domain features
      'sensor1_peak_freq': [freq_features_sensor1['peak_freq']],
      'sensor1_spectral_centroid': [freq_features_sensor1['spectral_centroid']],
      'sensor1_energy': [freq_features_sensor1['energy']],
      'sensor1_peak_power': [freq_features_sensor1['peak_power']],
      'sensor1_spectral_bandwidth': [freq_features_sensor1['spectral_bandwidth']],
      'sensor2_peak_freq': [freq_features_sensor2['peak_freq']],
      'sensor2_spectral_centroid': [freq_features_sensor2['spectral_centroid']],
      'sensor2_energy': [freq_features_sensor2['energy']],
      'sensor2_peak_power': [freq_features_sensor2['peak_power']],
      'sensor2_spectral_bandwidth': [freq_features_sensor2['spectral_bandwidth']],
      # categorical features
      'load': df['load'].iloc[0],
      'speed': df['speed'].iloc[0]
  })
  for i in range(1, 6):
    features[f'sensor1_top_freq_{i}'] = freq_features_sensor1.get(f'top_freq_{i}', np.nan)
    features[f'sensor2_top_freq_{i}'] = freq_features_sensor2.get(f'top_freq_{i}', np.nan)
  return features


def sliding_window(df: pd.DataFrame, window_size: int, step_size: int, features: list[str]) -> tuple:
  ''' Group the DataFrame first by 'fault', then by 'load', and then by 'speed'.
      For each group, apply a sliding window and store the corresponding fault, load, and speed values.
  '''
  windows = []
  labels_list = []
  grouped = df.groupby(['fault'])
  for fault, group in grouped:
    group = group.sort_values('timestamp')
    if len(group) < window_size:
      continue
    for start in range(0, len(group) - window_size + 1, step_size):
      window = group.iloc[start:start + window_size][features].to_numpy()
      windows.append(window)
      labels_list.append({'fault': fault})
  labels_df = pd.DataFrame(labels_list)
  return np.array(windows), labels_df


def sliding_window_features(df: pd.DataFrame, window_size: int, step_size: int):
  ''' Group the DataFrame first by 'fault', then by 'load', and then by 'speed'.
      For each group, apply a sliding window, compute features for each window using compute_stats,
      and store the corresponding fault, load, and speed values.
  '''
  features_list = []
  labels_list = []
  grouped = df.groupby(['fault'])
  for fault, group in grouped:
    group = group.sort_values('timestamp')
    if len(group) < window_size:
      continue
    ts = group['timestamp'].iloc[1] - group['timestamp'].iloc[0]
    fs = ts_to_frequency(ts)
    for start in range(0, len(group) - window_size + 1, step_size):
      window = group.iloc[start:start + window_size]
      feat = compute_stats(window, fs)
      features_list.append(feat)
      labels_list.append({'fault': fault})
  features_df = pd.concat(features_list, ignore_index=True)
  labels_df = pd.DataFrame(labels_list)
  return features_df, labels_df


def check_correlation(correlation_matrix: pd.DataFrame, threshold: float = 0.95) -> tuple[set, list[tuple]]:
  ''' Check for highly correlated features in the correlation matrix.
      Returns a set of correlated features and a list of tuples containing the feature pairs and their correlation values.
  '''
  correlated_features = set()
  correlated_pairs = []
  for i in range(correlation_matrix.shape[0]):
    for j in range(i):
      if abs(correlation_matrix.iloc[i, j]) > threshold:
        feature1 = correlation_matrix.columns[i]
        feature2 = correlation_matrix.columns[j]
        correlation_value = correlation_matrix.iloc[i, j]
        correlated_features.add(feature1)
        correlated_pairs.append((feature1, feature2, correlation_value))
  return correlated_features, correlated_pairs


def drop_features(df: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
  ''' Drop highly correlated features from the DataFrame.
      The correlation matrix is computed, and features with a correlation value above the threshold are dropped.
  '''
  correlation_matrix = df.corr()
  correlated_features, correlated_pairs = check_correlation(correlation_matrix=correlation_matrix, threshold=threshold)
  print(f'Number of correlated features: {len(correlated_features)}')
  print(f'Correlated features: {correlated_features}')
  print('\nHighly correlated feature pairs:')
  for feature1, feature2, corr_value in correlated_pairs:
    print(f'{feature1} and {feature2}: {corr_value:.2f}')
  print('Drop highly correlated features!')
  df = df.drop(correlated_features, axis=1)
  return df
