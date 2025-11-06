import { useState, useEffect, useRef } from 'react';
// local
import LineChartD3 from './LineChartD3';
import { MetricsData } from '../../interfaces/charts/MetricsData';


type LineChartRenderProps = {
  data: MetricsData;
  height: number;
};

export default function LineChartRender({ data, height = 300 }: LineChartRenderProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [chartWidth, setChartWidth] = useState(500);
  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        const w = containerRef.current.offsetWidth;
        setChartWidth(w);
      }
    };
    window.addEventListener('resize', updateWidth);
    updateWidth();
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  return (
    <div>
      <div ref={containerRef} className="w-full p-2 bg-white rounded shadow">
        <LineChartD3 data={data} height={height} width={chartWidth} />
      </div>

    </div>
  );
}
