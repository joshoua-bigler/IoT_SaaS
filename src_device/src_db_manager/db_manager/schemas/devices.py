def create_devices_table() -> str:
  return '''create table if not exists devices (
    device_identifier char(6) not null primary key,
    description text,
    long double precision,
    lat double precision,
    country varchar(100),
    timezone varchar(100) not null,
    status int,
    latest_alive timestamp
  )
  '''
