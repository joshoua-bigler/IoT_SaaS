import { DocumentNode } from '@apollo/client';
import { SELECT_NUMERIC_SCALAR_MODEL } from './../graphQl/queries/selectNumericScalarModel';
import { SELECT_NUMERIC_SCALAR } from './../graphQl/queries/selectNumericScalar';
import { MetricProps } from '../../interfaces/graphql/GetMetrics';

export function getMetricQueryConfig(metrics: MetricProps): {
  query: DocumentNode | null;
  variables: Record<string, any>;
} {
  switch (metrics.type) {
    case 'numeric_scalar_model': {
      const variables: Record<string, any> = {
        tenantIdentifier: metrics.tenantIdentifier,
        deviceIdentifier: metrics.deviceIdentifier,
        start: metrics.start,
        end: metrics.end,
        metricIdentifier: metrics.metricIdentifier,
        model: metrics.model,
        path: metrics.path ?? '',
      };
      if (metrics.grouping !== undefined && metrics.grouping !== null) {
        variables.grouping = metrics.grouping;
      }
      if (metrics.aggregation !== undefined && metrics.aggregation !== null) {
        variables.aggregation = metrics.aggregation;
      }
      return {
        query: SELECT_NUMERIC_SCALAR_MODEL,
        variables,
      };
    }

    case 'numeric_scalar': {
      const variables: Record<string, any> = {
        tenantIdentifier: metrics.tenantIdentifier,
        deviceIdentifier: metrics.deviceIdentifier,
        start: metrics.start,
        end: metrics.end,
        metricIdentifier: metrics.metricIdentifier,
        path: metrics.path ?? '',
      };
      if (metrics.aggregation !== undefined && metrics.aggregation !== null) {
        variables.aggregation = metrics.aggregation;
      }
      if (metrics.grouping !== undefined && metrics.grouping !== null) {
        variables.grouping = metrics.grouping;
      }
      return {
        query: SELECT_NUMERIC_SCALAR,
        variables,
      };
    }
  }
}
