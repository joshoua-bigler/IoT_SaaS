import mlflow.pytorch
import json
import torch.nn as nn
import torch
import pandas as pd
from mlflow.tracking import MlflowClient
from collections import Counter
# local
from analytics_api.graphql.types.ml import ModelInput, ModelResult
from analytics_api.graphql.enums import ModelType
from analytics_api.gls.gls import logger
_model_cache = {}


def load_model(model_input: ModelInput) -> nn.Module:
  ''' Load a model from MLflow tracking server based on the provided ModelInput.'''
  cache_key = (model_input.name, model_input.version, model_input.model_type)
  if cache_key in _model_cache:
    return _model_cache[cache_key]
  if model_input.model_type == ModelType.PYTORCH:
    model_uri = f'models:/{model_input.name}/{model_input.version}'
    model = mlflow.pytorch.load_model(model_uri=model_uri)
    client = MlflowClient()
    version = client.get_model_version(name=model_input.name, version=model_input.version)
    tags = version.tags
    labels = json.loads(tags['labels']) if 'labels' in tags else {}
    if not labels:
      raise ValueError(f'Labels not found for model {model_input.name} version {model_input.version}.')
    model.labels = labels
    model.analysis = tags.get('analysis', '')
    _model_cache[cache_key] = model
    return model
  raise ValueError(f'Model(name={model_input.name}, model_type={model_input.model_type}) not found!')


def create_prediction(df: pd.DataFrame, model: nn.Module, model_input: ModelInput, model_metrics: set) -> ModelResult:
  ''' Create a prediction using the provided model and input data.'''
  df_model = df[df['metric_identifier'].isin(model_metrics)]
  df_model_filt = df_model.iloc[:2 * model_input.window_size]
  if df_model_filt.empty:
    raise ValueError(f'No data found for model {model_input.name}.')
  elif df_model_filt.shape[0] < 2 * model_input.window_size:
    return ModelResult(name=model_input.name, predicted=None, probability=None)
  df_pivot = df_model_filt.pivot_table(index='timestamp', columns='metric_identifier', values='value')
  df_pivot = df_pivot.sort_index()
  df_pivot_norm = (df_pivot - df_pivot.mean()) / df_pivot.std()
  input_tensor = torch.tensor(df_pivot_norm.values, dtype=torch.float32)
  input_tensor = input_tensor.permute(1, 0).unsqueeze(0)
  model.eval()
  with torch.no_grad():
    logits = model(input_tensor)
  probabilities = torch.softmax(logits, dim=1).numpy()
  _, preds = torch.max(logits, 1)
  label = model.labels[str(int(preds))]
  logger.debug(f'Label: {label}, Probabilities: {probabilities} with {df['metric_identifier'].unique()}')
  return ModelResult(name=model_input.name, predicted=label, probability=float(probabilities[0][int(preds)]))

def voting_prediction(df: pd.DataFrame, model: nn.Module, model_input: ModelInput, model_metrics: set, n_windows: int = 5) -> ModelResult:
  ''' Create a voting prediction using the provided model and input data.'''
  df_model = df[df['metric_identifier'].isin(model_metrics)].copy()
  df_model['timestamp'] = pd.to_datetime(df_model['timestamp'])
  df_model = df_model.sort_values(by='timestamp')
  window_span = int(model_input.window_size)
  stride = int(window_span // 2)
  df_pivot = df_model.pivot_table(index='timestamp', columns='metric_identifier', values='value')
  df_pivot = df_pivot.sort_index()
  df_pivot = df_pivot.dropna(axis=0, how='any')  # Ensure no missing values per row
  max_possible_windows = max(1, (df_pivot.shape[0] - window_span) // stride + 1)
  actual_windows = min(n_windows, max_possible_windows)
  if actual_windows == 0:
    return ModelResult(name=model_input.name, predicted=None, probability=None)
  predictions = []
  probabilities = []
  model.eval()
  with torch.no_grad():
    for i in range(actual_windows):
      start = -(window_span + i * stride)
      end = None if i == 0 else -(i * stride)
      window = df_pivot.iloc[start:end]
      if window.shape[0] < window_span:
        continue
      window_norm = (window - window.mean()) / window.std()
      input_tensor = torch.tensor(window_norm.values, dtype=torch.float32)
      input_tensor = input_tensor.permute(1, 0).unsqueeze(0)
      logits = model(input_tensor)
      probs = torch.softmax(logits, dim=1).numpy()[0]
      pred_idx = int(torch.argmax(logits, dim=1))
      label = model.labels[str(pred_idx)]
      predictions.append(label)
      probabilities.append(probs)
  if not predictions:
    return ModelResult(name=model_input.name, predicted=None, probability=None)
  final_label = Counter(predictions).most_common(1)[0][0]
  label_index = int([k for k, v in model.labels.items() if v == final_label][0])
  avg_prob = float(sum(p[label_index] for p in probabilities) / len(probabilities))
  logger.debug(f'Voting labels: {predictions}, Final: {final_label}, Avg prob: {avg_prob:.4f}')
  return ModelResult(name=model_input.name, predicted=final_label, probability=avg_prob)