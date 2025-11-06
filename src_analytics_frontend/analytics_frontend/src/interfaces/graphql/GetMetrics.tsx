// local
import { Grouping, Aggregation } from './Enums';

export interface GetBaseMetric {
  type: 'numeric_scalar_model' | 'numeric_scalar';
  tenantIdentifier: string;
  deviceIdentifier: string;
  start: string;
  end: string;
  metricIdentifier?: string[];
  unit?: string;
  path?: string;
  aggregation?: Aggregation;
  grouping?: Grouping
}

export interface GetNumericScalarModel extends GetBaseMetric {
  type: 'numeric_scalar_model';
  model: {
    name: string;
    modelType: string;
    windowSize: number;
    version: string;
  };
}

export interface GetNumericScalarMetric extends GetBaseMetric {
  type: 'numeric_scalar';
}

export type MetricProps = GetNumericScalarModel | GetNumericScalarMetric;