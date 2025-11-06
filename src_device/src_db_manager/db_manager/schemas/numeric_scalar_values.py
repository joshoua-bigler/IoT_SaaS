def create_numeric_scalar_values_table() -> str:
  return '''create table if not exists numeric_scalar_values (
    metric_id uuid references metrics(id),
    value double precision,
    timestamp timestamp not null
  )
  '''
