def create_metric_paths_table() -> str:
  return '''create table if not exists paths (
    id uuid not null primary key default gen_random_uuid(),
    device_identifier char(6) not null references devices(device_identifier),
    path ltree not null unique,
    constraint unique_device_path unique (device_identifier, path)
  )
  '''
