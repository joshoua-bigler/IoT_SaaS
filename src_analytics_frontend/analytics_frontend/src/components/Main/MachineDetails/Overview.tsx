// local
import LineChartRender from '../../charts/LineChartRender';
import { lineCharDataLoader } from './../../dataLoaders/lineDataChartLoader';
import { MetricProps } from '../../../interfaces/graphql/GetMetrics';
interface OverviewProps {
  tenantIdentifier: string;
  deviceIdentifier: string | null;
}

const Overview = ({ tenantIdentifier, deviceIdentifier }: OverviewProps) => {
  if (!deviceIdentifier) {
    return <div>No device selected</div>;
  }

  if (!tenantIdentifier) {
    return <div>No tenant selected</div>;
  }

  const vibrationGear1: MetricProps = {
    type: 'numeric_scalar_model',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['vibration.gear1.x_axis', 'vibration.gear1.y_axis'],
    model: {
      name: 'gear_vibration_cnn_w_256',
      modelType: 'PYTORCH',
      windowSize: 256,
      version: '1',
    },
  };

  const vibrationGear2: MetricProps = {
    type: 'numeric_scalar_model',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['vibration.gear2.x_axis', 'vibration.gear2.y_axis'],
    model: {
      name: 'gear_vibration_cnn_w_256',
      modelType: 'PYTORCH',
      windowSize: 256,
      version: '1',
    },
  };

  const vibrationGear3: MetricProps = {
    type: 'numeric_scalar_model',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['vibration.gear3.x_axis', 'vibration.gear3.y_axis'],
    model: {
      name: 'gear_vibration_cnn_w_256',
      modelType: 'PYTORCH',
      windowSize: 256,
      version: '1',
    },
  };

  const vibrationGear4: MetricProps = {
    type: 'numeric_scalar_model',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['vibration.gear4.x_axis', 'vibration.gear4.y_axis'],
    model: {
      name: 'gear_vibration_cnn_w_256',
      modelType: 'PYTORCH',
      windowSize: 256,
      version: '1',
    },
  };

  const vibrationGear5: MetricProps = {
    type: 'numeric_scalar_model',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['vibration.gear5.x_axis', 'vibration.gear5.y_axis'],
    model: {
      name: 'gear_vibration_cnn_w_256',
      modelType: 'PYTORCH',
      windowSize: 256,
      version: '1',
    },
  };

  const vibrationGear6: MetricProps = {
    type: 'numeric_scalar_model',
    tenantIdentifier: tenantIdentifier,
    deviceIdentifier: deviceIdentifier,
    start: '2025-07-09',
    end: '2025-07-10',
    metricIdentifier: ['vibration.gear6.x_axis', 'vibration.gear6.y_axis'],
    model: {
      name: 'gear_vibration_cnn_w_256',
      modelType: 'PYTORCH',
      windowSize: 256,
      version: '1',
    },
  };

  const { data: vibrationGear1Data, status: vibrationGear1Status } = lineCharDataLoader(vibrationGear1, deviceIdentifier);
  const { data: vibrationGear2Data, status: vibrationGear2Status } = lineCharDataLoader(vibrationGear2, deviceIdentifier);
  const { data: vibrationGear3Data, status: vibrationGear3Status } = lineCharDataLoader(vibrationGear3, deviceIdentifier);
  const { data: vibrationGear4Data, status: vibrationGear4Status } = lineCharDataLoader(vibrationGear4, deviceIdentifier);
  const { data: vibrationGear5Data, status: vibrationGear5Status } = lineCharDataLoader(vibrationGear5, deviceIdentifier);
  const { data: vibrationGear6Data, status: vibrationGear6Status } = lineCharDataLoader(vibrationGear6, deviceIdentifier);

  return (
    <div className="grid grid-cols-2 gap-4 bg-gray-100 p-4 shadow-md">
      <div className="col-span-2">
        <LineChartRender data={vibrationGear1Data} height={300} />
      </div>
      <div className="col-span-2">
        <LineChartRender data={vibrationGear2Data} height={300} />
      </div>
      <div className="col-span-2">
        <LineChartRender data={vibrationGear3Data} height={300} />
      </div>
      <div className="col-span-2">
        <LineChartRender data={vibrationGear4Data} height={300} />
      </div>
      <div className="col-span-2">
        <LineChartRender data={vibrationGear5Data} height={300} />
      </div>
      <div className="col-span-2">
        <LineChartRender data={vibrationGear6Data} height={300} />
      </div>
    </div >
  );
};

export default Overview;