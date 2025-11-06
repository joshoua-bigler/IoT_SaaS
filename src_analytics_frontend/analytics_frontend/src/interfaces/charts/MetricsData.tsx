export type MetricsData = {
  timestamp: string[];
  metrics: {
    metricIdentifier: string;
    unit: string;
    values: number[];
  }[];
  model: {
    name: string | null;
    prediction: string | null;
    probability: number | null;
  };
};

export type QueryState = {
  loading: boolean;
  error: any;
};


export type MetricsResult = {
  data: MetricsData;
  status: QueryState;
};