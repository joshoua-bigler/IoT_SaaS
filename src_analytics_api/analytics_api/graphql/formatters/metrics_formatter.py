import pandas as pd
# local
from analytics_api.graphql.types.metrics import MetricsBase, Value, MetricsModel
from analytics_api.graphql.types.ml import ModelResult


def format_base_metrics(df: pd.DataFrame) -> list[MetricsBase]:
  grouped = df.groupby(['device_identifier', 'metric_identifier'])
  metrics_list = []
  for (device_id, metric_id), group in grouped:
    unit = group['unit'].iloc[0]
    values = [Value(value=row['value'], timestamp_local=row['timestamp_local'].isoformat()) for _, row in group.iterrows()] # yapf: disable
    metric = MetricsBase(device_identifier=device_id, metric_identifier=metric_id, unit=unit, values=values)
    metrics_list.append(metric)
  return metrics_list


def format_model_metrics(df: pd.DataFrame, model_metrics: set, model_result: ModelResult) -> list[MetricsModel]:
  model_metrics = model_metrics or set()
  grouped = df.groupby(['device_identifier', 'metric_identifier'])
  metrics_list = []
  for (device_id, metric_id), group in grouped:
    unit = group['unit'].iloc[0]
    values = [Value(value=row['value'], timestamp_local=row['timestamp_local'].isoformat()) for _, row in group.iterrows()] # yapf: disable
    metric = MetricsModel(device_identifier=device_id,
                          metric_identifier=metric_id,
                          unit=unit,
                          values=values,
                          model=model_result if metric_id in model_metrics else None)
    metrics_list.append(metric)
  return metrics_list
