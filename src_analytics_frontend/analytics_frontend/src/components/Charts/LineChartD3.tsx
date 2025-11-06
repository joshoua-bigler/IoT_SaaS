import * as d3 from 'd3';
import { useEffect, useRef } from 'react';
// local
import { MetricsData } from '../../interfaces/charts/MetricsData';

type LineChartD3 = {
  data: MetricsData
  height?: number;
  width?: number;
  prediction?: string;
  probability?: number | null;
};

export default function LineChartD3({ data, height = 300, width = 800 }: LineChartD3) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!data.timestamp.length || !data.metrics.length) return;

    const longestLabel = Math.max(...data.metrics.map((s) => s.metricIdentifier.length));
    const margin = { top: 20, right: longestLabel * 8 + 60, bottom: 30, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'd3-tooltip')
      .style('position', 'absolute')
      .style('pointer-events', 'none')
      .style('padding', '6px 10px')
      .style('background', 'rgba(0, 0, 0, 0.7)')
      .style('color', '#fff')
      .style('border-radius', '6px')
      .style('font-size', '12px')
      .style('display', 'none');

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    svg.append('defs').append('clipPath')
      .attr('id', 'clip')
      .append('rect')
      .attr('width', innerWidth)
      .attr('height', innerHeight);

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    const chartArea = g.append('g').attr('clip-path', 'url(#clip)');

    const parseTime = d3.isoParse;
    const xValues = data.timestamp.map(parseTime) as Date[];

    const x = d3.scaleTime()
      .domain(d3.extent(xValues) as [Date, Date])
      .range([0, innerWidth]);

    const allValues = data.metrics.flatMap((s) => s.values.filter((v) => v !== null));
    const maxY = d3.max(allValues) || 1;
    const minY = d3.min(allValues) || 0;

    const y = d3.scaleLinear()
      .domain([minY - (minY / 100), maxY])
      .range([innerHeight, 0])
      .nice();

    const xAxisG = g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0, ${innerHeight})`)
      .call(d3.axisBottom(x))
      .style('font-size', '11px');

    g.append('g')
      .attr('class', 'y-axis')
      .call(d3.axisLeft(y));

    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const paths: d3.Selection<SVGPathElement, any[], SVGGElement, unknown>[] = [];

    data.metrics.forEach((series, idx) => {
      const colorValue = color(idx.toString());
      const values = series.values;

      const parsedPoints = values.map((value, i) => ({
        value,
        date: xValues[i],
      })).filter(d => d.value !== null);

      const line = d3.line<any>()
        .defined(d => d.value !== null)
        .x(d => x(d.date))
        .y(d => y(d.value as number));

      const path = chartArea.append('path')
        .datum(parsedPoints)
        .attr('fill', 'none')
        .attr('stroke', colorValue)
        .attr('stroke-width', 2)
        .attr('d', line);

      paths.push(path);

      chartArea.selectAll(`.dot-${idx}`)
        .data(parsedPoints)
        .enter()
        .append('circle')
        .attr('cx', d => x(d.date))
        .attr('cy', d => y(d.value as number))
        .attr('r', 2)
        .attr('fill', colorValue)
        .on('mouseover', (event, d) => {
          tooltip.html(
            `<strong>${series.metricIdentifier}</strong><br/>
             Time: ${d.date.toLocaleString()}<br/>
             Value: ${(d.value as number).toFixed(2)}`
          )
            .style('left', `${event.pageX + 10}px`)
            .style('top', `${event.pageY - 28}px`)
            .style('display', 'block');
        })
        .on('mousemove', (event) => {
          tooltip
            .style('left', `${event.pageX + 10}px`)
            .style('top', `${event.pageY - 28}px`);
        })
        .on('mouseout', () => {
          tooltip.style('display', 'none');
        });
    });

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([1, 10])
      .translateExtent([[0, 0], [width, height]])
      .extent([[0, 0], [width, height]])
      .on('zoom', (event) => {
        const newX = event.transform.rescaleX(x);
        xAxisG.call(d3.axisBottom(newX));

        paths.forEach((path) => {
          const parsedPoints = path.datum() as any[];
          const newLine = d3.line<any>()
            .defined(d => d.value !== null)
            .x(d => newX(d.date))
            .y(d => y(d.value as number));

          path.attr('d', newLine(parsedPoints));
        });

        chartArea.selectAll('circle')
          .attr('cx', d => newX((d as any).date));
      });

    svg.call(zoom as any);
  }, [data, height, width]);

  const legendItems = data.metrics.map((series, idx) => ({
    label: series.metricIdentifier,
    color: d3.schemeCategory10[idx % 10],
  }));

  const prediction = data.model?.prediction;
  const probability = data.model?.probability;

  return (
    <div className='flex gap-4 items-start'>
      <svg ref={svgRef} width={width} height={height} />
      <div className='flex flex-col gap-2 mt-4 text-black'>
        {prediction != null && (
          <div>
            <div className='font-bold'>Model Prediction</div>
            <div>
              {prediction}
              {probability != null && ` (${(probability * 100).toFixed(1)}%)`}
            </div>
          </div>
        )}
        <div className='h-px bg-gray-300 my-2' />
        {legendItems.map((item, i) => (
          <div key={i} className='flex items-center gap-2'>
            <span className='w-4 h-2 rounded-sm' style={{ backgroundColor: item.color }} />
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
