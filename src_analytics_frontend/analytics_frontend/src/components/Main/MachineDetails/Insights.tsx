// local
import LineChartRender from '../../charts/LineChartRender';
import { lineCharDataLoader } from './../../dataLoaders/lineDataChartLoader';
import { MetricProps } from '../../../interfaces/graphql/GetMetrics';

interface InsightsProps {
  tenantIdentifier: string;
  deviceIdentifier: string | null;
}

const Insights = ({ deviceIdentifier, tenantIdentifier }: InsightsProps) => {
  if (!deviceIdentifier) {
    return <div>No device selected</div>;
  }

  if (!tenantIdentifier) {
    return <div>No tenant selected</div>;
  }

  const humidity: MetricProps = {
    type: 'numeric_scalar',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['humidity.ambient'],
  };

  const temperature: MetricProps = {
    type: 'numeric_scalar',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['temperature.ambient'],
  };

  const temperatureEngine: MetricProps = {
    type: 'numeric_scalar',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['temperature.engine'],
  };

  const { data: humidityData, status: humidityStatus } = lineCharDataLoader(humidity, deviceIdentifier);
  const { data: temperatureData, status: temperatureStatus } = lineCharDataLoader(temperature, deviceIdentifier);
  const { data: temperatureEngineData, status: temperatureEngineStatus } = lineCharDataLoader(temperatureEngine, deviceIdentifier);

  return (
    <div className='grid grid-cols-2 gap-4 bg-gray-100 p-4 shadow-md'>
      <div className="col-span-2">
        <LineChartRender data={humidityData} height={300} />
      </div>
      <div className="col-span-2">
        <LineChartRender data={temperatureData} height={300} />
      </div>
      <div className="col-span-2">
        <LineChartRender data={temperatureEngineData} height={300} />
      </div>
    </div>
  );
};

export default Insights;
