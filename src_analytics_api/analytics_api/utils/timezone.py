import pandas as pd


def convert_to_local_time(timestamp: pd.Series, timezone: pd.Series | str) -> pd.Series | str:
  utc_time = pd.to_datetime(timestamp).dt.tz_localize('UTC')
  if isinstance(timezone, str):
    return utc_time.dt.tz_convert(timezone).dt.tz_localize(None)
  return pd.Series([t.tz_convert(tz).tz_localize(None) if pd.notnull(t) and pd.notnull(tz) else pd.NaT for t, tz in zip(utc_time, timezone)], index=timestamp.index) # yapf: disable
