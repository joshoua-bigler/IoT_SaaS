import re
import pandas as pd
import wandb
import seaborn as sns
import mlflow
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


def timedelta_to_str(td: pd.Timedelta) -> str:
  if td.microseconds > 0:
    return f'{td.microseconds}us'
  elif td.seconds > 0:
    return f'{td.seconds}s'
  elif td.days > 0:
    return f'{td.days * 24 * 3600}s'
  else:
    raise ValueError('Unsupported Timedelta format')


def ts_to_frequency(ts: str) -> float:
  ''' Converts a time interval string to frequency in Hz.
      Supported units:
        - s   (seconds)
        - ms  (milliseconds)
        - us  (microseconds)
        - ns  (nanoseconds)
        
      Example
      -------
      ts_to_frequency('10ms') returns 100.0 Hz
  '''
  if isinstance(ts, pd.Timedelta):
    ts = timedelta_to_str(td=ts)
  pattern = r'([0-9]*\.?[0-9]+)\s*(s|ms|us|ns)?'
  match = re.match(pattern, ts.strip())
  if not match:
    raise ValueError('Invalid time interval format')
  value, unit = match.groups()
  value = float(value)
  if not unit:
    raise ValueError('Time unit not specified')
  if unit == 's':
    seconds = value
  elif unit == 'ms':
    seconds = value / 1000.0
  elif unit == 'us':
    seconds = value / 1e6
  elif unit == 'ns':
    seconds = value / 1e9
  else:
    raise ValueError('Unsupported time unit')
  frequency = 1 / seconds
  return frequency


def check_data_gaps(df: pd.DataFrame, milliseconds: int) -> pd.DataFrame:
  df = df.sort_values('timestamp').reset_index(drop=True)
  df['time_diff'] = df['timestamp'].diff()
  expected_interval = pd.Timedelta(milliseconds=milliseconds)
  gaps = df[df['time_diff'] > expected_interval]
  return gaps


def log_wandb_metrics(y_test, y_pred):
  classification_dict = classification_report(y_test, y_pred, output_dict=True)
  classes = sorted(np.unique(y_test))
  accuracy = accuracy_score(y_test, y_pred)
  cm_svm = confusion_matrix(y_test, y_pred)
  macro = classification_dict['macro avg']
  weighted = classification_dict['weighted avg']
  metrics = {
      'accuracy': accuracy,
      'precision_macro': macro['precision'],
      'recall_macro': macro['recall'],
      'f1_macro': macro['f1-score'],
      'precision_weighted': weighted['precision'],
      'recall_weighted': weighted['recall'],
      'f1_weighted': weighted['f1-score']
  }
  wandb.log(metrics)
  plt.figure(figsize=(6, 4))
  sns.heatmap(cm_svm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
  plt.xlabel('Predicted Label')
  plt.ylabel('True Label')
  plt.title('Confusion Matrix - SVM')
  wandb.log({'confusion_matrix': wandb.Image(plt)})
  return metrics


def log_metrics_mlflow(y_test, y_pred, model_name: str, run_id: str):
  with mlflow.start_run(run_id=run_id):
    classification_dict = classification_report(y_test, y_pred, output_dict=True)
    classes = sorted(np.unique(y_test))
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    macro = classification_dict['macro avg']
    weighted = classification_dict['weighted avg']
    metrics = {
        'accuracy': accuracy,
        'precision_macro': macro['precision'],
        'recall_macro': macro['recall'],
        'f1_macro': macro['f1-score'],
        'precision_weighted': weighted['precision'],
        'recall_weighted': weighted['recall'],
        'f1_weighted': weighted['f1-score']
    }
    mlflow.log_metrics(metrics)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title(f'Confusion Matrix - {model_name}')
    plt.tight_layout()
  return metrics
