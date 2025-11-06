def enable_timescale() -> str:
  return 'create extension if not exists timescaledb'


def create_hypertable(table: str) -> str:
  return f"select create_hypertable('{table}', 'timestamp')"


def create_index(table: str) -> str:
  return f"create index ix_metric_id_time on {table} (metric_id, timestamp)"
