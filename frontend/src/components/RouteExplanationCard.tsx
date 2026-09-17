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
      <div className="border border-border rounded bg-bg-base p-4 text-xs text-text-secondary text-center">
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
    lower_traffic_penalty: "Avoided congested corridors",
    capacity_satisfied: "Payload capacity strictly satisfied",
    all_locations_covered: "100% delivery waypoints covered",
    time_constraint_satisfied: "Within transit duration limits",
    strictly_dominates_alternative: "Pareto dominates alternative route",
  };

  return (
    <div className="border border-border rounded bg-bg-base flex flex-col gap-3 p-3.5 text-xs">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border pb-2">
        <div className="flex items-center gap-1.5">
          <ShieldCheck size={15} className="text-signal-green" />
          <span className="font-bold uppercase tracking-wider text-text-primary text-[11px]">
            Explainability Layer
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-signal-green/10 text-signal-green border border-signal-green/30">
            Deterministic
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowRawText(!showRawText)}
            className="px-2 py-0.5 rounded border border-border text-[11px] text-text-secondary hover:text-text-primary flex items-center gap-1 transition-colors"
          >
            <FileText size={11} />
            <span>{showRawText ? "Cards" : "Template"}</span>
          </button>
          <button
            onClick={handleCopy}
            className="px-2 py-0.5 rounded border border-border text-[11px] text-text-secondary hover:text-text-primary flex items-center gap-1 transition-colors"
            title="Copy Human-Readable Report"
          >
            {copied ? <Check size={11} className="text-signal-green" /> : <Copy size={11} />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
        </div>
      </div>

      {showRawText ? (
        /* Render Deterministic Human-Readable Text View */
        <pre className="font-mono text-[11px] bg-bg-surface p-2.5 rounded border border-border text-text-primary whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto">
          {explanation.human_readable}
        </pre>
      ) : (
        /* Render Structured Visual Explanation */
        <div className="flex flex-col gap-3">
          {/* Assigned Vehicle & Route */}
          <div className="flex flex-col gap-1 bg-bg-surface p-2.5 rounded border border-border">
            <div className="flex items-center justify-between">
              <span className="text-text-secondary font-medium">Assigned Unit:</span>
              <span className="font-mono font-bold text-text-primary">{explanation.vehicle}</span>
            </div>
            <div className="flex items-center gap-1 mt-1 text-[11px] text-text-secondary overflow-x-auto pb-0.5">
              <Navigation size={12} className="text-signal-green shrink-0" />
              <span className="truncate">
                {explanation.selected_route.join(" ➔ ")}
              </span>
            </div>
          </div>

          {/* Why Selected Reasons */}
          <div className="flex flex-col gap-1.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">
              Why This Route Was Selected
            </span>
            <div className="grid grid-cols-1 gap-1">
              {explanation.reasons.map((reason) => (
                <div
                  key={reason}
                  className="flex items-center gap-2 px-2 py-1 rounded bg-bg-surface border border-border text-text-primary"
                >
                  <CheckCircle2 size={13} className="text-signal-green shrink-0" />
                  <span className="font-medium text-[11px]">
                    {reasonLabels[reason] || reason.replace(/_/g, " ")}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Key Trade-Off */}
          {explanation.tradeoffs && explanation.tradeoffs.length > 0 && (
            <div className="flex flex-col gap-1 border border-signal-amber/30 bg-signal-amber/10 p-2.5 rounded">
              <div className="flex items-center gap-1.5 text-signal-amber font-semibold text-[11px]">
                <Scale size={13} />
                <span>Key Trade-Off</span>
              </div>
              <p className="text-text-primary text-[11px] leading-relaxed">
                {explanation.tradeoffs[0].statement}
              </p>
            </div>
          )}

          {/* Constraint Checks */}
          <div className="flex flex-col gap-1.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">
              Constraint Verification
            </span>
            <div className="grid grid-cols-3 gap-1.5">
              {/* Capacity */}
              <div
                className={`p-1.5 rounded border text-center flex flex-col items-center justify-center gap-0.5 ${
                  explanation.constraints.capacity.satisfied
                    ? "border-signal-green/30 bg-signal-green/5 text-signal-green"
                    : "border-signal-red/30 bg-signal-red/5 text-signal-red"
                }`}
              >
                {explanation.constraints.capacity.satisfied ? (
                  <CheckCircle2 size={13} />
                ) : (
                  <XCircle size={13} />
                )}
                <span className="text-[10px] font-medium text-text-primary">Capacity</span>
                <span className="font-mono text-[9px] opacity-80">
                  {explanation.metrics.capacity_used_percent}% used
                </span>
              </div>

              {/* Waypoint Coverage */}
              <div
                className={`p-1.5 rounded border text-center flex flex-col items-center justify-center gap-0.5 ${
                  explanation.constraints.all_locations_covered.satisfied
                    ? "border-signal-green/30 bg-signal-green/5 text-signal-green"
                    : "border-signal-red/30 bg-signal-red/5 text-signal-red"
                }`}
              >
                {explanation.constraints.all_locations_covered.satisfied ? (
                  <CheckCircle2 size={13} />
                ) : (
                  <XCircle size={13} />
                )}
                <span className="text-[10px] font-medium text-text-primary">Waypoints</span>
                <span className="font-mono text-[9px] opacity-80">
                  {explanation.constraints.all_locations_covered.locations_visited} /{" "}
                  {explanation.constraints.all_locations_covered.locations_required}
                </span>
              </div>

              {/* Time Window */}
              <div
                className={`p-1.5 rounded border text-center flex flex-col items-center justify-center gap-0.5 ${
                  explanation.constraints.time_constraint.satisfied
                    ? "border-signal-green/30 bg-signal-green/5 text-signal-green"
                    : "border-signal-red/30 bg-signal-red/5 text-signal-red"
                }`}
              >
                {explanation.constraints.time_constraint.satisfied ? (
                  <CheckCircle2 size={13} />
                ) : (
                  <XCircle size={13} />
                )}
                <span className="text-[10px] font-medium text-text-primary">Time Limit</span>
                <span className="font-mono text-[9px] opacity-80">
                  {explanation.metrics.travel_time_min.toFixed(0)}m elapsed
                </span>
              </div>
            </div>
          </div>

          {/* Alternative Route Candidate (Highlighted in Yellow/Amber) */}
          {explanation.alternative && (
            <div className="flex flex-col gap-1.5 border border-[#F5A623]/50 bg-[#F5A623]/10 p-2.5 rounded">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[#F5A623] font-semibold text-[11px]">
                  <GitCompare size={13} />
                  <span>Evaluated Alternative: {explanation.alternative.name}</span>
                </div>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#F5A623]/20 text-[#F5A623] border border-[#F5A623]/40">
                  Yellow Candidate
                </span>
              </div>

              <div className="grid grid-cols-3 gap-1 pt-1 font-mono text-[10px] text-text-secondary">
                <div>
                  Dist:{" "}
                  <span className="text-text-primary font-bold">
                    {explanation.alternative.metrics.distance_km?.toFixed(1) || "N/A"} km
                  </span>
                </div>
                <div>
                  Time:{" "}
                  <span className="text-text-primary font-bold">
                    {explanation.alternative.metrics.travel_time_min?.toFixed(1) || "N/A"} min
                  </span>
                </div>
                <div>
                  Cost:{" "}
                  <span className="text-text-primary font-bold">
                    {explanation.alternative.metrics.objective_cost?.toFixed(1) || "N/A"}
                  </span>
                </div>
              </div>

              <div className="text-[10px] text-text-secondary mt-0.5">
                Rejection reason:{" "}
                <span className="font-medium text-text-primary">
                  {explanation.alternative.reasons_rejected
                    .map((r) => r.replace(/_/g, " "))
                    .join(", ")}
                </span>
              </div>
            </div>
          )}

          {/* Decision Statement */}
          <div className="bg-bg-surface p-2 rounded border border-border text-[11px] text-text-secondary leading-relaxed">
            <span className="font-semibold text-text-primary">Decision: </span>
            {explanation.decision}
          </div>
        </div>
      )}
    </div>
  );
}
