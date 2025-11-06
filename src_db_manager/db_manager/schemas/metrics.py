def create_metrics_table() -> str:
  return '''create table if not exists metrics (
    id uuid not null primary key default gen_random_uuid(),
    device_identifier char(6) references devices(device_identifier),
    path_id uuid references paths(id),
    metric_identifier text not null ,
    unit varchar(50),
    display_name text,
    metric_type varchar(50) not null check (metric_type in ('numeric_scalar', 'numeric_array', 'text')),
    unique(device_identifier, metric_identifier)
  )
  '''
