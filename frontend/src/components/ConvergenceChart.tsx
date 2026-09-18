"use client";

import React from "react";

interface ConvergenceChartProps {
  history: number[];
  baselineCost: number;
  crossoverIteration: number | null;
  algorithmName?: string;
  isStreaming?: boolean;
  currentIteration?: number;
}

export default function ConvergenceChart({
  history,
  baselineCost,
  crossoverIteration,
  algorithmName = "QPSO",
  isStreaming = false,
  currentIteration,
}: ConvergenceChartProps) {
  if (!history || history.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center border border-border rounded-xl bg-bg-surface text-text-secondary text-sm">
        Run optimization to view convergence history.
      </div>
    );
  }

  // Determine bounds
  const allValues = [...history, baselineCost];
  const minVal = Math.min(...allValues) * 0.95;
  const maxVal = Math.max(...allValues) * 1.05;
  const valRange = maxVal - minVal > 0 ? maxVal - minVal : 1;

  const width = 640;
  const height = 300;
  const padding = { top: 30, right: 80, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const getX = (index: number) => {
    if (history.length <= 1) return padding.left;
    return padding.left + (index / (history.length - 1)) * chartWidth;
  };

  const getY = (val: number) => {
    return padding.top + chartHeight - ((val - minVal) / valRange) * chartHeight;
  };

  // Generate SVG path for convergence curve
  const points = history.map((val, idx) => `${getX(idx)},${getY(val)}`);
  const pathD = `M ${points.join(" L ")}`;

  // Baseline Y position
  const baselineY = getY(baselineCost);

  // Final Point
  const lastIdx = history.length - 1;
  const lastVal = history[lastIdx];
  const lastX = getX(lastIdx);
  const lastY = getY(lastVal);

  // Check if algorithm actually beat the baseline
  const beatBaseline = lastVal < baselineCost - 0.05;
  const curveColor = beatBaseline ? "#2ECC71" : "#F5A623";

  // Crossover Point: Only valid if it genuinely beat the baseline
  let crossoverX: number | null = null;
  let crossoverY: number | null = null;
  if (beatBaseline && crossoverIteration !== null && crossoverIteration < history.length) {
    crossoverX = getX(crossoverIteration);
    crossoverY = getY(history[crossoverIteration]);
  }

  // Y-axis ticks
  const yTicks = [
    minVal,
    minVal + valRange * 0.33,
    minVal + valRange * 0.66,
    maxVal,
  ];

  return (
    <div className="w-full bg-bg-surface border border-border rounded-xl p-5 flex flex-col gap-3 shadow-sm">
      {/* Chart Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h4 className="text-sm sm:text-base font-bold text-text-primary">
            {algorithmName} Convergence Trajectory vs. Baseline
          </h4>
          <p className="text-xs text-text-secondary mt-0.5">
            X-Axis: Iterations &bull; Y-Axis: Route Travel Cost (Minutes)
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-signal-red inline-block"></span>
            <span className="text-text-secondary">Baseline:</span>
            <span className="font-semibold text-text-primary">{baselineCost.toFixed(1)}m</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="w-3 h-0.5 inline-block"
              style={{ backgroundColor: curveColor }}
            ></span>
            <span className="text-text-secondary">Converged:</span>
            <span
              className="font-bold font-mono"
              style={{ color: curveColor }}
            >
              {lastVal.toFixed(1)}m
            </span>
          </div>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto min-w-[500px] select-none"
        >
          {/* Horizontal Gridlines & Y-Axis labels */}
          {yTicks.map((tick, i) => {
            const yPos = getY(tick);
            return (
              <g key={i}>
                <line
                  x1={padding.left}
                  y1={yPos}
                  x2={width - padding.right}
                  y2={yPos}
                  stroke="var(--border-color)"
                  strokeDasharray="3 3"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 10}
                  y={yPos + 4}
                  textAnchor="end"
                  className="font-mono text-[11px] fill-text-secondary"
                >
                  {tick.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* X-Axis bottom line */}
          <line
            x1={padding.left}
            y1={height - padding.bottom}
            x2={width - padding.right}
            y2={height - padding.bottom}
            stroke="var(--border-color)"
            strokeWidth="1"
          />

          {/* X-Axis Ticks & Labels */}
          <text
            x={padding.left}
            y={height - padding.bottom + 18}
            textAnchor="start"
            className="font-mono text-[11px] fill-text-secondary"
          >
            Iter 0
          </text>
          <text
            x={width - padding.right}
            y={height - padding.bottom + 18}
            textAnchor="end"
            className="font-mono text-[11px] fill-text-secondary"
          >
            Iter {history.length - 1}
          </text>

          <defs>
            <linearGradient id="convergenceCurveGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={curveColor} stopOpacity="0.25" />
              <stop offset="100%" stopColor={curveColor} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* 1. Flat Reference Line in Red (Baseline Cost) */}
          <line
            x1={padding.left}
            y1={baselineY}
            x2={width - padding.right}
            y2={baselineY}
            stroke="#E5484D"
            strokeWidth="2"
            strokeDasharray="6 4"
          />
          <text
            x={width - padding.right + 6}
            y={baselineY + 4}
            className="font-mono text-[11px] fill-signal-red font-bold"
          >
            Baseline ({baselineCost.toFixed(1)}m)
          </text>

          {/* Area Fill beneath Convergence Curve */}
          <path
            d={`${pathD} L ${lastX},${height - padding.bottom} L ${padding.left},${height - padding.bottom} Z`}
            fill="url(#convergenceCurveGrad)"
          />

          {/* 2. Convergence Curve */}
          <path
            d={pathD}
            fill="none"
            stroke={curveColor}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="transition-all duration-500 ease-out"
          />

          {/* 3. Crossover Point (Only displayed when algorithm beat baseline) */}
          {crossoverX !== null && crossoverY !== null && (
            <g>
              <circle
                cx={crossoverX}
                cy={crossoverY}
                r="10"
                fill="#F5A623"
                className="animate-ping opacity-60"
              />
              <circle
                cx={crossoverX}
                cy={crossoverY}
                r="5"
                fill="#F5A623"
                stroke="#0B0F14"
                strokeWidth="1.5"
              />
              <line
                x1={crossoverX}
                y1={crossoverY}
                x2={crossoverX}
                y2={padding.top + 5}
                stroke="#F5A623"
                strokeWidth="1"
                strokeDasharray="2 2"
              />
              <rect
                x={crossoverX - 60}
                y={padding.top - 18}
                width="120"
                height="18"
                rx="4"
                fill="var(--bg-surface)"
                stroke="#F5A623"
                strokeWidth="1"
              />
              <text
                x={crossoverX}
                y={padding.top - 6}
                textAnchor="middle"
                className="font-mono text-[10px] fill-signal-amber font-bold"
              >
                Beat baseline @ Iter #{crossoverIteration}
              </text>
            </g>
          )}

          {/* 4. Final Converged Point */}
          <circle
            cx={lastX}
            cy={lastY}
            r="8"
            fill={curveColor}
            className="animate-pulse opacity-40"
          />
          <circle
            cx={lastX}
            cy={lastY}
            r="4.5"
            fill={curveColor}
            stroke="#0B0F14"
            strokeWidth="1.5"
          />
          <text
            x={lastX + 8}
            y={lastY + 4}
            className="font-mono text-[11px] font-bold"
            fill={curveColor}
          >
            {lastVal.toFixed(1)}m
          </text>
        </svg>
      </div>

      {/* Operational Diagnostic Footer */}
      <div className="text-xs text-text-secondary flex flex-col sm:flex-row sm:items-center justify-between border-t border-border pt-2.5 gap-1">
        <span>
          {beatBaseline && crossoverIteration !== null
            ? `${algorithmName} crossed classical baseline at iteration #${crossoverIteration} (-${(baselineCost - lastVal).toFixed(1)} min saved).`
            : beatBaseline
            ? `${algorithmName} outperformed baseline without early crossover recording.`
            : `${algorithmName} converged within baseline boundary (${lastVal.toFixed(1)} min vs baseline ${baselineCost.toFixed(1)} min).`}
        </span>
        <span className="font-mono text-text-primary font-semibold">
          Evaluated {history.length - 1} iterations
        </span>
      </div>
    </div>
  );
}
