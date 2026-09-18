"use client";

import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";

interface Landmark {
  id: number;
  name: string;
  lat: number;
  lon: number;
  desc?: string;
}

interface MapComponentProps {
  beforeCoordinates: [number, number][];
  afterCoordinates: [number, number][];
  alternativeCoordinates?: [number, number][];
  alternativeName?: string;
  landmarks: Landmark[];
  depotId?: number;
  destinationId?: number | null;
  isOptimizing?: boolean;
}

export default function MapComponent({
  beforeCoordinates,
  afterCoordinates,
  alternativeCoordinates = [],
  alternativeName = "Suggested Alternative",
  landmarks,
  depotId = 0,
  destinationId = null,
  isOptimizing = false,
}: MapComponentProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const beforePolylineRef = useRef<L.Polyline | null>(null);
  const afterPolylineRef = useRef<L.Polyline | null>(null);
  const alternativePolylineRef = useRef<L.Polyline | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);

  const vehicleMarkerRef = useRef<L.Marker | null>(null);
  const animationTimerRef = useRef<NodeJS.Timeout | null>(null);
  const transitionTimerRef = useRef<NodeJS.Timeout | null>(null);

  const [viewMode, setViewMode] = useState<"all" | "optimal" | "alternative" | "baseline">("all");
  const [isVehicleTracing, setIsVehicleTracing] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitionStage, setTransitionStage] = useState<string | null>(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [11.0168, 76.9678], // Coimbatore Regional Center
      zoom: 11,
      zoomControl: true,
      attributionControl: false,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
    }).addTo(map);

    markersLayerRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    return () => {
      if (animationTimerRef.current) clearInterval(animationTimerRef.current);
      if (transitionTimerRef.current) clearTimeout(transitionTimerRef.current);
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update polylines, vehicle tracer, and markers whenever routes or landmarks change
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear old polylines and animations
    if (beforePolylineRef.current) map.removeLayer(beforePolylineRef.current);
    if (afterPolylineRef.current) map.removeLayer(afterPolylineRef.current);
    if (alternativePolylineRef.current) map.removeLayer(alternativePolylineRef.current);
    if (vehicleMarkerRef.current) {
      map.removeLayer(vehicleMarkerRef.current);
      vehicleMarkerRef.current = null;
    }
    if (animationTimerRef.current) {
      clearInterval(animationTimerRef.current);
      animationTimerRef.current = null;
    }

    // 1. Baseline Route (Red, dashed line)
    if (beforeCoordinates.length > 1 && (viewMode === "all" || viewMode === "baseline")) {
      const beforeLine = L.polyline(beforeCoordinates, {
        color: "#E5484D",
        weight: viewMode === "baseline" ? 5 : 4,
        dashArray: "8, 8",
        opacity: viewMode === "baseline" ? 1.0 : 0.65,
        lineJoin: "round",
        className: "leaflet-route-baseline",
      }).addTo(map);
      beforePolylineRef.current = beforeLine;
    }

    // 2. Alternative Route (Yellow / Amber, dashed-solid line)
    if (alternativeCoordinates.length > 1 && (viewMode === "all" || viewMode === "alternative")) {
      const altLine = L.polyline(alternativeCoordinates, {
        color: "#F5A623",
        weight: viewMode === "alternative" ? 5 : 4,
        dashArray: "4, 6",
        opacity: viewMode === "alternative" ? 1.0 : 0.8,
        lineJoin: "round",
        className: "leaflet-route-alternative",
      }).addTo(map);
      alternativePolylineRef.current = altLine;
    }

    // 3. Optimal After Route (Green, solid line)
    if (afterCoordinates.length > 1 && (viewMode === "all" || viewMode === "optimal")) {
      const afterLine = L.polyline(afterCoordinates, {
        color: "#2ECC71",
        weight: viewMode === "optimal" ? 6 : 5,
        opacity: 0.95,
        lineJoin: "round",
        className: "leaflet-route-optimal",
      }).addTo(map);
      afterPolylineRef.current = afterLine;
    }

    // 4. Moving Dispatch Vehicle Tracer along active view's route
    let activeTraceCoords = afterCoordinates;
    if (viewMode === "baseline" && beforeCoordinates.length > 1) {
      activeTraceCoords = beforeCoordinates;
    } else if (viewMode === "alternative" && alternativeCoordinates.length > 1) {
      activeTraceCoords = alternativeCoordinates;
    }

    if (isVehicleTracing && activeTraceCoords.length > 1) {
      const tracerColor = viewMode === "baseline" ? "#E5484D" : viewMode === "alternative" ? "#F5A623" : "#2ECC71";
      const vehicleIcon = L.divIcon({
        html: `<div style="background:${tracerColor}; border:2px solid #FFFFFF; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 0 14px ${tracerColor}, 0 2px 6px rgba(0,0,0,0.4); font-size:15px; animation:pulse 1.5s infinite;">🚛</div>`,
        className: "dispatch-tracer-icon",
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });

      const startPt = activeTraceCoords[0];
      const vMarker = L.marker(startPt, { icon: vehicleIcon, zIndexOffset: 2000 }).addTo(map);
      vehicleMarkerRef.current = vMarker;

      let coordIdx = 0;
      let subStep = 0;
      const subDivisions = 8;

      animationTimerRef.current = setInterval(() => {
        if (!activeTraceCoords || activeTraceCoords.length <= 1) return;
        const fromPt = activeTraceCoords[coordIdx];
        const toPt = activeTraceCoords[(coordIdx + 1) % activeTraceCoords.length];

        const lat = fromPt[0] + ((toPt[0] - fromPt[0]) * subStep) / subDivisions;
        const lon = fromPt[1] + ((toPt[1] - fromPt[1]) * subStep) / subDivisions;

        vMarker.setLatLng([lat, lon]);

        subStep++;
        if (subStep >= subDivisions) {
          subStep = 0;
          coordIdx = (coordIdx + 1) % activeTraceCoords.length;
        }
      }, 75);
    }

    // 5. Render Landmark Markers with Dynamic Depot & Destination
    if (markersLayerRef.current) {
      markersLayerRef.current.clearLayers();

      landmarks.forEach((lm) => {
        const isDepot = lm.id === depotId;
        const isDestination = destinationId !== null && lm.id === destinationId;

        let iconHtml = "";
        let iconSize: [number, number] = [24, 24];
        let iconAnchor: [number, number] = [12, 12];
        let zOffset = 100;

        if (isDepot) {
          // Prominent Gold/Amber Origin Depot Marker
          iconHtml = `<div style="background:#F5A623; color:#0B0F14; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:14px; border:3px solid #FFFFFF; box-shadow:0 0 12px #F5A623, 0 3px 6px rgba(0,0,0,0.5);">D</div>`;
          iconSize = [32, 32];
          iconAnchor = [16, 16];
          zOffset = 1500;
        } else if (isDestination) {
          // Distinct Indigo/Cyan Checkered Finish Line Marker
          iconHtml = `<div style="background:#3B82F6; color:#FFFFFF; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:16px; border:3px solid #FFFFFF; box-shadow:0 0 12px #3B82F6, 0 3px 6px rgba(0,0,0,0.5);">🏁</div>`;
          iconSize = [32, 32];
          iconAnchor = [16, 16];
          zOffset = 1400;
        } else {
          // Standard Delivery Waypoint Pin
          iconHtml = `<div style="background:#2ECC71; color:#0B0F14; width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:11px; border:2px solid #FFFFFF; box-shadow:0 2px 5px rgba(0,0,0,0.35);">${lm.id}</div>`;
        }

        const customIcon = L.divIcon({
          html: iconHtml,
          className: "custom-map-pin",
          iconSize: iconSize,
          iconAnchor: iconAnchor,
        });

        const marker = L.marker([lm.lat, lm.lon], { icon: customIcon, zIndexOffset: zOffset });
        marker.bindPopup(
          `<div style="font-family:inherit; padding:6px;">
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
              <strong style="font-size:14px;">${lm.name}</strong>
              ${isDepot ? '<span style="background:#F5A623; color:#000; font-size:10px; font-weight:bold; padding:2px 6px; border-radius:4px;">DEPOT</span>' : ''}
              ${isDestination ? '<span style="background:#3B82F6; color:#fff; font-size:10px; font-weight:bold; padding:2px 6px; border-radius:4px;">DESTINATION</span>' : ''}
            </div>
            <p style="margin:2px 0; font-size:12px; opacity:0.8;">${lm.desc || "Regional Delivery Waypoint"}</p>
            <p style="margin:4px 0 0 0; font-family:monospace; font-size:11px; opacity:0.6;">[${lm.lat.toFixed(4)}° N, ${lm.lon.toFixed(4)}° E]</p>
          </div>`
        );
        marker.addTo(markersLayerRef.current!);
      });
    }

    // Auto-fit bounds with smooth camera fly-to
    const allCoords = [...beforeCoordinates, ...afterCoordinates, ...alternativeCoordinates];
    if (allCoords.length > 1 && !isTransitioning) {
      const bounds = L.latLngBounds(allCoords);
      map.flyToBounds(bounds, { padding: [45, 45], maxZoom: 13, duration: 1.0 });
    }
  }, [beforeCoordinates, afterCoordinates, alternativeCoordinates, landmarks, depotId, destinationId, viewMode, isVehicleTracing, isTransitioning]);

  // Handle Morph / Sequential Transition Animation (Baseline -> Alternative -> Optimal)
  const handlePlayTransition = () => {
    if (isTransitioning) return;
    setIsTransitioning(true);

    // Step 1: Show Baseline (Red)
    setTransitionStage("Step 1: Baseline Route (Unoptimized Nearest Neighbor)");
    setViewMode("baseline");

    transitionTimerRef.current = setTimeout(() => {
      // Step 2: Show Alternative (Yellow)
      setTransitionStage(`Step 2: Suboptimal Candidate (${alternativeName})`);
      setViewMode("alternative");

      transitionTimerRef.current = setTimeout(() => {
        // Step 3: Show Optimal (Green)
        setTransitionStage("Step 3: Converged Optimal Route (Quantum-behaved PSO)");
        setViewMode("optimal");

        transitionTimerRef.current = setTimeout(() => {
          // Final: Show All with optimal prominent
          setTransitionStage(null);
          setViewMode("all");
          setIsTransitioning(false);
        }, 1800);
      }, 1800);
    }, 1800);
  };

  return (
    <div className="relative w-full h-full min-h-[500px] rounded-xl border border-border overflow-hidden bg-bg-surface flex flex-col shadow-sm">
      {/* Top Map Control Bar */}
      <div className="absolute top-4 right-4 z-[1000] flex flex-wrap items-center gap-2 bg-bg-surface/90 backdrop-blur-md px-3 py-2 rounded-xl border border-border text-sm shadow-md">
        {/* Toggle Live Vehicle Tracer */}
        <button
          onClick={() => setIsVehicleTracing(!isVehicleTracing)}
          title="Toggle live dispatch vehicle tracer animation"
          className={`px-3 py-1.5 rounded-lg border transition-colors flex items-center gap-1.5 font-semibold text-xs ${
            isVehicleTracing
              ? "bg-signal-green/20 border-signal-green text-signal-green"
              : "bg-bg-base border-border text-text-secondary hover:text-text-primary"
          }`}
        >
          <span>🚛</span>
          <span>{isVehicleTracing ? "Tracing Live" : "Tracer Paused"}</span>
        </button>

        {/* View Filters */}
        <div className="flex items-center gap-1 bg-bg-base border border-border rounded-lg p-0.5 text-xs">
          <button
            onClick={() => setViewMode("all")}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              viewMode === "all"
                ? "bg-bg-surface text-text-primary font-bold shadow-sm"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setViewMode("optimal")}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              viewMode === "optimal"
                ? "bg-signal-green text-[#0B0F14] font-bold shadow-sm"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Optimal (Green)
          </button>
          <button
            onClick={() => setViewMode("alternative")}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              viewMode === "alternative"
                ? "bg-[#F5A623] text-[#0B0F14] font-bold shadow-sm"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Alternative (Yellow)
          </button>
          <button
            onClick={() => setViewMode("baseline")}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              viewMode === "baseline"
                ? "bg-signal-red text-white font-bold shadow-sm"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Baseline (Red)
          </button>
        </div>

        {/* Morph Transition Animation Button */}
        <button
          onClick={handlePlayTransition}
          disabled={isTransitioning}
          className="px-3 py-1.5 rounded-lg bg-bg-base border border-border hover:border-signal-amber text-text-primary text-xs font-bold transition-all disabled:opacity-50 flex items-center gap-1.5"
        >
          <span>🎬</span>
          <span>{isTransitioning ? "Morphing..." : "Play Route Morph"}</span>
        </button>
      </div>

      {/* Transition Banner Notification */}
      {isTransitioning && transitionStage && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-[1000] bg-bg-surface/95 backdrop-blur-md border border-signal-amber/40 text-text-primary px-4 py-2 rounded-xl shadow-2xl text-xs sm:text-sm font-semibold flex items-center gap-2 animate-bounce">
          <span className="w-2.5 h-2.5 rounded-full bg-signal-amber animate-ping" />
          <span>{transitionStage}</span>
        </div>
      )}

      {/* Map Legend Overlay */}
      <div className="absolute bottom-5 left-5 z-[1000] bg-bg-surface/95 backdrop-blur-md p-3.5 rounded-xl border border-border text-xs flex flex-col gap-2 shadow-lg">
        <div className="flex items-center gap-2">
          <span className="w-4 h-1.5 bg-signal-green rounded"></span>
          <span className="text-text-primary font-bold">Optimized Route (Green)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-1.5 bg-[#F5A623] rounded"></span>
          <span className="text-text-secondary font-medium">{alternativeName} (Yellow Alternative)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-0.5 border-b-2 border-dashed border-signal-red"></span>
          <span className="text-text-secondary">Unoptimized Baseline (Red)</span>
        </div>
        <div className="flex items-center gap-3 pt-1 border-t border-border/60">
          <div className="flex items-center gap-1.5">
            <span className="w-3.5 h-3.5 rounded-full bg-[#F5A623] text-[9px] font-bold text-black flex items-center justify-center">D</span>
            <span className="text-text-secondary font-medium">Origin Depot</span>
          </div>
          {destinationId !== null && (
            <div className="flex items-center gap-1.5">
              <span className="w-3.5 h-3.5 rounded-full bg-[#3B82F6] text-[9px] flex items-center justify-center text-white">🏁</span>
              <span className="text-text-secondary font-medium">Destination</span>
            </div>
          )}
        </div>
      </div>

      {/* Leaflet Map Canvas */}
      <div ref={mapContainerRef} className="w-full flex-1 z-0" />
    </div>
  );
}
