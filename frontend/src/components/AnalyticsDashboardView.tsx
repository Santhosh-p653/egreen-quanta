"use client";

import React, { useState } from "react";
import {
  TrendingDown,
  Clock,
  Leaf,
  Activity,
  FileText,
  BarChart3,
  Layers,
  Sparkles,
  Zap,
  SlidersHorizontal,
} from "lucide-react";
import CompareView, { AlgorithmResult } from "@/components/CompareView";
import RouteExplanationCard, { RouteExplanationData } from "@/components/RouteExplanationCard";
import ConvergenceChart from "@/components/ConvergenceChart";

interface MetricsData {
  beforeDistance: number;
  afterDistance: number;
  beforeTime: number;
  afterTime: number;
  beforeCongestion: number;
  afterCongestion: number;
  timeSavedMin: number;
  timeImprovementPct: number;
  distanceImprovementPct: number;
  runtimeMs: number;
  iterationCount: number;
}

interface AnalyticsDashboardViewProps {
  metrics: MetricsData;
  compareResults: AlgorithmResult[];
  isComparing: boolean;
  onRefreshCompare: () => void;
  routeExplanation: RouteExplanationData | null;
  convergenceHistory: number[];
  baselineCost: number;
  crossoverIteration: number | null;
  tabSize?: "compact" | "comfortable" | "large";
  onTabSizeChange?: (size: "compact" | "comfortable" | "large") => void;
}

export default function AnalyticsDashboardView({
  metrics,
  compareResults,
  isComparing,
  onRefreshCompare,
  routeExplanation,
  convergenceHistory,
  baselineCost,
  crossoverIteration,
  tabSize = "comfortable",
  onTabSizeChange,
}: AnalyticsDashboardViewProps) {
  const [activeDashboardTab, setActiveDashboardTab] = useState<"comparison" | "explanation" | "convergence">("comparison");

  // Environmental calculation
  const distanceSavedKm = Math.max(0, metrics.beforeDistance - metrics.afterDistance);
  const estCarbonSavedKg = distanceSavedKm * 0.21 * 1.15; // 0.21 kg/km with idling factor
  const estFuelSavedL = distanceSavedKm * 0.11; // ~11 liters per 100km

  const isOptimal = metrics.timeSavedMin > 0.01;

  // Density styles for tab buttons
  const tabBtnClass =
    tabSize === "compact"
      ? "px-3 py-1.5 text-xs"
      : tabSize === "large"
      ? "px-5 py-3 text-base font-bold"
      : "px-4 py-2.5 text-sm font-semibold";

  return (
    <div className="w-full min-h-full flex flex-col gap-6 p-6 overflow-y-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-text-primary tracking-tight">
            Performance & Analytics Dashboard
          </h1>
          <p className="text-sm sm:text-base text-text-secondary mt-1">
            Executive telemetry, truthful algorithmic benchmarking, deterministic explainability audit, and carbon savings.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Tab Size Customizer Controls */}
          {onTabSizeChange && (
            <div className="flex items-center gap-1 bg-bg-surface border border-border p-1 rounded-xl text-xs font-semibold shadow-sm">
              <span className="text-text-secondary px-2 flex items-center gap-1">
                <SlidersHorizontal size={13} />
                <span>Tab Size:</span>
              </span>
              <button
                onClick={() => onTabSizeChange("compact")}
                className={`px-2.5 py-1 rounded-lg transition-colors ${
                  tabSize === "compact"
                    ? "bg-bg-base text-text-primary font-bold shadow-sm"
                    : "text-text-secondary hover:text-text-primary"
                }`}
              >
                Compact
              </button>
              <button
                onClick={() => onTabSizeChange("comfortable")}
                className={`px-2.5 py-1 rounded-lg transition-colors ${
                  tabSize === "comfortable"
                    ? "bg-bg-base text-text-primary font-bold shadow-sm"
                    : "text-text-secondary hover:text-text-primary"
                }`}
              >
                Normal
              </button>
              <button
                onClick={() => onTabSizeChange("large")}
                className={`px-2.5 py-1 rounded-lg transition-colors ${
                  tabSize === "large"
                    ? "bg-bg-base text-text-primary font-bold shadow-sm"
                    : "text-text-secondary hover:text-text-primary"
                }`}
              >
                Large
              </button>
            </div>
          )}

          {/* Dynamic Status Badge (Truthful) */}
          <div
            className={`px-3.5 py-1.5 rounded-lg border text-sm font-semibold font-mono flex items-center gap-2 ${
              isOptimal
                ? "border-signal-green/30 bg-signal-green/10 text-signal-green"
                : "border-signal-amber/30 bg-signal-amber/10 text-signal-amber"
            }`}
          >
            <Zap size={15} />
            <span>
              {isOptimal
                ? `Optimal Routing Discovered (-${metrics.timeImprovementPct.toFixed(1)}%)`
                : "Baseline Equivalent Solution"}
            </span>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TOP EXECUTIVE KPI METRICS (LARGE READABLE TYPOGRAPHY) */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: TRAVEL TIME */}
        <div className="p-5 rounded-xl bg-bg-surface border border-border shadow-sm flex flex-col gap-3">
          <div className="flex items-center justify-between text-sm text-text-secondary">
            <span className="flex items-center gap-2 font-medium">
              <Clock size={16} className={isOptimal ? "text-signal-green" : "text-signal-amber"} />
              <span>Total Transit Time</span>
            </span>
            <span
              className={`px-2 py-0.5 rounded font-mono font-bold text-xs border ${
                isOptimal
                  ? "bg-signal-green/15 text-signal-green border-signal-green/30"
                  : "bg-signal-amber/15 text-signal-amber border-signal-amber/30"
              }`}
            >
              {isOptimal ? `-${metrics.timeImprovementPct.toFixed(1)}%` : "0.0%"}
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span
              className={`text-3xl font-bold font-mono ${
                isOptimal ? "text-signal-green" : "text-text-primary"
              }`}
            >
              {metrics.afterTime.toFixed(1)}
            </span>
            <span className="text-sm font-semibold text-text-secondary">minutes</span>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-border/70 text-xs text-text-secondary">
            <span>Baseline: <strong className="text-signal-red font-mono">{metrics.beforeTime.toFixed(1)} min</strong></span>
            <span>Saved: <strong className="text-signal-green font-mono">+{metrics.timeSavedMin.toFixed(1)} min</strong></span>
          </div>
        </div>

        {/* KPI 2: TOTAL DISTANCE */}
        <div className="p-5 rounded-xl bg-bg-surface border border-border shadow-sm flex flex-col gap-3">
          <div className="flex items-center justify-between text-sm text-text-secondary">
            <span className="flex items-center gap-2 font-medium">
              <TrendingDown size={16} className="text-signal-green" />
              <span>Road Distance</span>
            </span>
            <span className="px-2 py-0.5 rounded font-mono font-bold text-xs bg-signal-green/15 text-signal-green border border-signal-green/30">
              -{metrics.distanceImprovementPct.toFixed(1)}%
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-signal-green">
              {metrics.afterDistance.toFixed(1)}
            </span>
            <span className="text-sm font-semibold text-text-secondary">kilometers</span>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-border/70 text-xs text-text-secondary">
            <span>Baseline: <strong className="text-signal-red font-mono">{metrics.beforeDistance.toFixed(1)} km</strong></span>
            <span>Saved: <strong className="text-signal-green font-mono">+{distanceSavedKm.toFixed(1)} km</strong></span>
          </div>
        </div>

        {/* KPI 3: GREEN FLEET CARBON SAVINGS */}
        <div className="p-5 rounded-xl bg-bg-surface border border-border shadow-sm flex flex-col gap-3">
          <div className="flex items-center justify-between text-sm text-text-secondary">
            <span className="flex items-center gap-2 font-medium">
              <Leaf size={16} className="text-signal-green" />
              <span>CO₂ Carbon Offset</span>
            </span>
            <span className="px-2 py-0.5 rounded font-mono font-bold text-xs bg-signal-green/15 text-signal-green border border-signal-green/30">
              Eco-Friendly
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-signal-green">
              {estCarbonSavedKg.toFixed(1)}
            </span>
            <span className="text-sm font-semibold text-text-secondary">kg CO₂ saved</span>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-border/70 text-xs text-text-secondary">
            <span>Fuel Saved: <strong className="text-text-primary font-mono">{estFuelSavedL.toFixed(1)} Liters</strong></span>
            <span>Congestion Avoided</span>
          </div>
        </div>

        {/* KPI 4: SOLVER PERFORMANCE & CONVERGENCE */}
        <div className="p-5 rounded-xl bg-bg-surface border border-border shadow-sm flex flex-col gap-3">
          <div className="flex items-center justify-between text-sm text-text-secondary">
            <span className="flex items-center gap-2 font-medium">
              <Activity size={16} className="text-signal-amber" />
              <span>Engine Latency</span>
            </span>
            <span className="px-2 py-0.5 rounded font-mono font-bold text-xs bg-signal-amber/15 text-signal-amber border border-signal-amber/30">
              {crossoverIteration !== null && isOptimal ? `Iter #${crossoverIteration}` : "Iter 0"}
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-text-primary">
              {metrics.runtimeMs.toFixed(1)}
            </span>
            <span className="text-sm font-semibold text-text-secondary">milliseconds</span>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-border/70 text-xs text-text-secondary">
            <span>Iterations: <strong className="text-text-primary font-mono">{metrics.iterationCount}</strong></span>
            <span>{isOptimal ? "Beat Baseline" : "Within Baseline"}</span>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SECTION TABS FOR DASHBOARD VIEWS WITH ADJUSTABLE TAB SIZE */}
      {/* ========================================================================= */}
      <div className="flex items-center gap-2 bg-bg-surface border border-border p-1.5 rounded-xl text-sm w-fit">
        <button
          onClick={() => setActiveDashboardTab("comparison")}
          className={`flex items-center gap-2 rounded-lg transition-all ${tabBtnClass} ${
            activeDashboardTab === "comparison"
              ? "bg-bg-base text-text-primary shadow-sm border border-border"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          <BarChart3 size={17} className="text-signal-green" />
          <span>Algorithmic Comparison & Graphs</span>
        </button>

        <button
          onClick={() => setActiveDashboardTab("explanation")}
          className={`flex items-center gap-2 rounded-lg transition-all ${tabBtnClass} ${
            activeDashboardTab === "explanation"
              ? "bg-bg-base text-text-primary shadow-sm border border-border"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          <FileText size={17} className="text-signal-amber" />
          <span>Deterministic Reasoning & Audit</span>
        </button>

        <button
          onClick={() => setActiveDashboardTab("convergence")}
          className={`flex items-center gap-2 rounded-lg transition-all ${tabBtnClass} ${
            activeDashboardTab === "convergence"
              ? "bg-bg-base text-text-primary shadow-sm border border-border"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          <Layers size={17} className="text-signal-green" />
          <span>Convergence Dynamics</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* ACTIVE DASHBOARD TAB CONTENT */}
      {/* ========================================================================= */}
      <div className="w-full">
        {activeDashboardTab === "comparison" && (
          <CompareView
            results={compareResults}
            isLoading={isComparing}
            onRefresh={onRefreshCompare}
            tabSize={tabSize}
          />
        )}

        {activeDashboardTab === "explanation" && (
          <div className="w-full max-w-5xl">
            <RouteExplanationCard explanation={routeExplanation} />
          </div>
        )}

        {activeDashboardTab === "convergence" && (
          <div className="w-full max-w-4xl">
            <ConvergenceChart
              history={convergenceHistory}
              baselineCost={baselineCost}
              crossoverIteration={crossoverIteration}
              algorithmName="Quantum-behaved PSO"
            />
          </div>
        )}
      </div>
    </div>
  );
}
