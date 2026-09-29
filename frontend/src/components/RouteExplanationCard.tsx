"use client";

import React, { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  TrendingDown,
  Clock,
  Navigation,
  FileText,
  Copy,
  Check,
  Scale,
  GitCompare,
  ShieldCheck,
} from "lucide-react";

export interface ConstraintItem {
  satisfied: boolean;
  used_percent?: number;
  demand_total?: number;
  capacity_limit?: number;
  locations_visited?: number;
  locations_required?: number;
  travel_time_min?: number;
  time_limit_min?: number | null;
}

export interface TradeOffItem {
  type: string;
  statement: string;
  distance_difference_km: number;
  time_difference_min: number;
}

export interface AlternativeItem {
  name: string;
  selected_route: string[];
  metrics: {
    distance_km?: number;
    travel_time_min?: number;
    objective_cost?: number;
    congestion_level?: number;
  };
  reasons_rejected: string[];
}

export interface RouteExplanationData {
  vehicle: string;
  selected_route: string[];
  metrics: {
    distance_km: number;
    travel_time_min: number;
    capacity_used_percent: number;
    objective_cost: number;
    congestion_level?: number;
  };
  reasons: string[];
  constraints: {
    capacity: ConstraintItem;
    all_locations_covered: ConstraintItem;
    time_constraint: ConstraintItem;
  };
  tradeoffs: TradeOffItem[];
  alternative: AlternativeItem | null;
  decision: string;
  human_readable: string;
}

interface RouteExplanationCardProps {
  explanation: RouteExplanationData | null;
  onSelectAlternative?: () => void;
}

export default function RouteExplanationCard({
  explanation,
  onSelectAlternative,
}: RouteExplanationCardProps) {
  const [showRawText, setShowRawText] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!explanation) {
    return (
      <div className="border border-border rounded-xl bg-bg-surface p-6 text-sm text-text-secondary text-center shadow-sm">
        Run route optimization to view the deterministic explainability report.
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(explanation.human_readable);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const reasonLabels: Record<string, string> = {
    lower_travel_time: "Reduced estimated travel time",
    lower_total_distance: "Shorter road transit distance",
    lower_optimization_objective: "Lower global cost objective",
    lower_traffic_penalty: "Avoided congested arterial corridors",
    capacity_satisfied: "Payload capacity strictly satisfied",
    all_locations_covered: "100% delivery waypoints covered",
    time_constraint_satisfied: "Within transit duration limits",
    strictly_dominates_alternative: "Pareto dominates evaluated alternative candidate",
  };

  return (
    <div className="border border-border rounded-xl bg-bg-surface flex flex-col gap-4 p-5 text-sm shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck size={18} className="text-signal-green" />
          <span className="font-bold tracking-tight text-text-primary text-base">
            Deterministic Explainability Layer
          </span>
          <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-signal-green/10 text-signal-green border border-signal-green/30">
            Verified
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setShowRawText(!showRawText)}
            className="px-3 py-1 rounded-lg border border-border text-xs text-text-secondary hover:text-text-primary flex items-center gap-1.5 transition-colors font-medium bg-bg-base"
          >
            <FileText size={13} />
            <span>{showRawText ? "Visual Cards" : "Raw Template"}</span>
          </button>
          <button
            onClick={handleCopy}
            className="px-3 py-1 rounded-lg border border-border text-xs text-text-secondary hover:text-text-primary flex items-center gap-1.5 transition-colors font-medium bg-bg-base"
            title="Copy Report"
          >
            {copied ? <Check size={13} className="text-signal-green" /> : <Copy size={13} />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
        </div>
      </div>

      {showRawText ? (
        /* Render Deterministic Human-Readable Text View */
        <pre className="font-mono text-xs bg-bg-base p-4 rounded-xl border border-border text-text-primary whitespace-pre-wrap leading-relaxed max-h-[450px] overflow-y-auto">
          {explanation.human_readable}
        </pre>
      ) : (
        /* Render Structured Visual Explanation */
        <div className="flex flex-col gap-4">
          {/* Assigned Unit & Route */}
          <div className="flex flex-col gap-1.5 bg-bg-base p-3.5 rounded-xl border border-border">
            <div className="flex items-center justify-between">
              <span className="text-text-secondary font-medium text-xs uppercase tracking-wider">
                Assigned Unit
              </span>
              <span className="font-mono font-bold text-sm text-text-primary">
                {explanation.vehicle}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-1 text-sm text-text-primary overflow-x-auto pb-1">
              <Navigation size={15} className="text-signal-green shrink-0" />
              <span className="font-medium">
                {explanation.selected_route.join(" ➔ ")}
              </span>
            </div>
          </div>

          {/* Why Selected Reasons */}
          <div className="flex flex-col gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-text-secondary">
              Why This Route Was Selected
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {explanation.reasons.map((reason) => (
                <div
                  key={reason}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg bg-bg-base border border-border text-text-primary text-xs sm:text-sm font-medium"
                >
                  <CheckCircle2 size={15} className="text-signal-green shrink-0" />
                  <span>
                    {reasonLabels[reason] || reason.replace(/_/g, " ")}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Key Trade-Off */}
          {explanation.tradeoffs && explanation.tradeoffs.length > 0 && (
            <div className="flex flex-col gap-1.5 border border-signal-amber/30 bg-signal-amber/10 p-3.5 rounded-xl">
              <div className="flex items-center gap-2 text-signal-amber font-bold text-xs uppercase tracking-wide">
                <Scale size={15} />
                <span>Pareto Dominance Trade-Off</span>
              </div>
              <p className="text-text-primary text-sm leading-relaxed">
                {explanation.tradeoffs[0].statement}
              </p>
            </div>
          )}

          {/* Constraint Verification */}
          <div className="flex flex-col gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-text-secondary">
              Hard Constraint Verification
            </span>
            <div className="grid grid-cols-3 gap-3">
              {/* Capacity */}
              <div
                className={`p-3 rounded-xl border text-center flex flex-col items-center justify-center gap-1 ${
                  explanation.constraints.capacity.satisfied
                    ? "border-signal-green/30 bg-signal-green/5 text-signal-green"
                    : "border-signal-red/30 bg-signal-red/5 text-signal-red"
                }`}
              >
                {explanation.constraints.capacity.satisfied ? (
                  <CheckCircle2 size={18} />
                ) : (
                  <XCircle size={18} />
                )}
                <span className="text-xs font-bold text-text-primary">Payload Capacity</span>
                <span className="font-mono text-xs font-semibold opacity-90">
                  {explanation.metrics.capacity_used_percent}% utilized
                </span>
              </div>

              {/* Waypoint Coverage */}
              <div
                className={`p-3 rounded-xl border text-center flex flex-col items-center justify-center gap-1 ${
                  explanation.constraints.all_locations_covered.satisfied
                    ? "border-signal-green/30 bg-signal-green/5 text-signal-green"
                    : "border-signal-red/30 bg-signal-red/5 text-signal-red"
                }`}
              >
                {explanation.constraints.all_locations_covered.satisfied ? (
                  <CheckCircle2 size={18} />
                ) : (
                  <XCircle size={18} />
                )}
                <span className="text-xs font-bold text-text-primary">Stop Coverage</span>
                <span className="font-mono text-xs font-semibold opacity-90">
                  {explanation.constraints.all_locations_covered.locations_visited} /{" "}
                  {explanation.constraints.all_locations_covered.locations_required} stops
                </span>
              </div>

              {/* Time Window */}
              <div
                className={`p-3 rounded-xl border text-center flex flex-col items-center justify-center gap-1 ${
                  explanation.constraints.time_constraint.satisfied
                    ? "border-signal-green/30 bg-signal-green/5 text-signal-green"
                    : "border-signal-red/30 bg-signal-red/5 text-signal-red"
                }`}
              >
                {explanation.constraints.time_constraint.satisfied ? (
                  <CheckCircle2 size={18} />
                ) : (
                  <XCircle size={18} />
                )}
                <span className="text-xs font-bold text-text-primary">Duration Limit</span>
                <span className="font-mono text-xs font-semibold opacity-90">
                  {explanation.metrics.travel_time_min.toFixed(1)} min
                </span>
              </div>
            </div>
          </div>

          {/* Alternative Route Candidate */}
          {explanation.alternative && (
            <div className="flex flex-col gap-2 border border-[#F5A623]/40 bg-[#F5A623]/10 p-3.5 rounded-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-[#F5A623] font-bold text-xs uppercase tracking-wide">
                  <GitCompare size={15} />
                  <span>Evaluated Alternative: {explanation.alternative.name}</span>
                </div>
                <span className="px-2 py-0.5 rounded text-xs font-bold bg-[#F5A623]/20 text-[#F5A623] border border-[#F5A623]/40">
                  Yellow Candidate
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 pt-1 font-mono text-xs text-text-secondary">
                <div>
                  Distance:{" "}
                  <strong className="text-text-primary">
                    {explanation.alternative.metrics.distance_km?.toFixed(1) || "N/A"} km
                  </strong>
                </div>
                <div>
                  Travel Time:{" "}
                  <strong className="text-text-primary">
                    {explanation.alternative.metrics.travel_time_min?.toFixed(1) || "N/A"} min
                  </strong>
                </div>
                <div>
                  Objective Cost:{" "}
                  <strong className="text-text-primary">
                    {explanation.alternative.metrics.objective_cost?.toFixed(1) || "N/A"}
                  </strong>
                </div>
              </div>

              <div className="text-xs text-text-secondary mt-1">
                Primary Rejection Factor:{" "}
                <span className="font-semibold text-text-primary">
                  {explanation.alternative.reasons_rejected
                    .map((r) => r.replace(/_/g, " "))
                    .join(", ")}
                </span>
              </div>
            </div>
          )}

          {/* Decision Statement */}
          <div className="bg-bg-base p-3.5 rounded-xl border border-border text-sm text-text-secondary leading-relaxed">
            <strong className="text-text-primary">Deterministic Conclusion: </strong>
            {explanation.decision}
          </div>
        </div>
      )}
    </div>
  );
}
