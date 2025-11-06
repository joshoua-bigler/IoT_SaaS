export interface Device {
  deviceIdentifier: string;
  description?: string;
  city?: string;
  country?: string;
  status?: string;
  latestAliveLocal?: string;
  timezone?: string;
  lat?: number;
  long?: number;
}