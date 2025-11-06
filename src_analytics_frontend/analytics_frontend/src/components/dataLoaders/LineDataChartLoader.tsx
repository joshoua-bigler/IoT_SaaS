import { useQuery } from '@apollo/client';
import { useEffect, useState, useMemo } from 'react';
import { MetricProps } from '../../interfaces/graphql/GetMetrics';
import { getMetricQueryConfig } from '../../services/charts/getMetricQueryConfig';
import { MetricsResult } from '../../interfaces/charts/MetricsData';

export function lineCharDataLoader(metricsProps: MetricProps, deviceIdentifier: string): MetricsResult {
  const [metricsData, setMetricsData] = useState<any[]>([]);
  const { query, variables } = useMemo(() => {
    console.log('metricsProps', metricsProps);
    return getMetricQueryConfig(metricsProps);
  }, [metricsProps]);
  // console.log('query', query);
  // console.log('variables', variables);
  const {
    data: metrics_data,
    loading,
    error,
  } = useQuery(query!, {
    variables,
    skip: !query,
  });

  useEffect(() => {
    if (!metrics_data) return;
    if (metricsProps.type === 'numeric_scalar_model') {
      setMetricsData(metrics_data.numericScalarModel);
    } else if (metricsProps.type === 'numeric_scalar') {
      setMetricsData(metrics_data.numericScalar);
    }
  }, [metrics_data, deviceIdentifier, metricsProps.type]);

  const timestamp = metricsData[0]?.values
    ? metricsData[0].values.map((v: any) => v.timestampLocal)
    : [];
  const metrics = metricsData.map((entry: any) => ({
    metricIdentifier: entry.metricIdentifier,
    unit: entry.unit,
    values: entry.values.map((v: any) => v.value),
  }));

  const prediction = metricsData[0]?.model?.predicted;
  const probability = metricsData[0]?.model?.probability;

  return {
    data: {
      timestamp,
      metrics,
      ...(metricsData[0]?.model && {
        model: {
          name: metricsData[0]?.model?.name || null,
          prediction,
          probability,
        }
      }),
    },
    status: {
      loading,
      error,
    },
  };
}
