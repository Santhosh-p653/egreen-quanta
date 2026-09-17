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
  isOptimizing?: boolean;
}

export default function MapComponent({
  beforeCoordinates,
  afterCoordinates,
  alternativeCoordinates = [],
  alternativeName = "Suggested Alternative",
  landmarks,
  isOptimizing = false,
}: MapComponentProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const beforePolylineRef = useRef<L.Polyline | null>(null);
  const afterPolylineRef = useRef<L.Polyline | null>(null);
  const alternativePolylineRef = useRef<L.Polyline | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);

  const [viewMode, setViewMode] = useState<"all" | "optimal" | "alternative" | "baseline">("all");
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [11.0168, 76.9678], // Coimbatore Center
      zoom: 12,
      zoomControl: true,
      attributionControl: false,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
    }).addTo(map);

    markersLayerRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update polylines and markers whenever coordinates change
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear old polylines
    if (beforePolylineRef.current) map.removeLayer(beforePolylineRef.current);
    if (afterPolylineRef.current) map.removeLayer(afterPolylineRef.current);
    if (alternativePolylineRef.current) map.removeLayer(alternativePolylineRef.current);

    // 1. Before Route (Red, dashed line)
    if (beforeCoordinates.length > 1 && (viewMode === "all" || viewMode === "baseline")) {
      const beforeLine = L.polyline(beforeCoordinates, {
        color: "#E5484D",
        weight: 4,
        dashArray: "8, 8",
        opacity: viewMode === "all" ? 0.7 : 0.95,
        lineJoin: "round",
      }).addTo(map);
      beforePolylineRef.current = beforeLine;
    }

    // 2. Alternative Route (Yellow / Amber, dashed-solid line)
    if (alternativeCoordinates.length > 1 && (viewMode === "all" || viewMode === "alternative")) {
      const altLine = L.polyline(alternativeCoordinates, {
        color: "#F5A623", // Vivid Yellow / Amber for suggesting routes other than best
        weight: 4,
        dashArray: "4, 6",
        opacity: viewMode === "all" ? 0.85 : 0.95,
        lineJoin: "round",
      }).addTo(map);
      alternativePolylineRef.current = altLine;
    }

    // 3. Optimal After Route (Green, solid line)
    if (afterCoordinates.length > 1 && (viewMode === "all" || viewMode === "optimal")) {
      const afterLine = L.polyline(afterCoordinates, {
        color: "#2ECC71",
        weight: 5,
        opacity: 0.95,
        lineJoin: "round",
      }).addTo(map);
      afterPolylineRef.current = afterLine;
    }

    // 3. Render Landmark Markers
    if (markersLayerRef.current) {
      markersLayerRef.current.clearLayers();

      landmarks.forEach((lm, index) => {
        const isDepot = index === 0;
        const iconHtml = isDepot
          ? `<div style="background:#F5A623; color:#0B0F14; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:12px; border:2px solid #FFFFFF; box-shadow:0 2px 4px rgba(0,0,0,0.4);">D</div>`
          : `<div style="background:#2ECC71; color:#0B0F14; width:22px; height:22px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:11px; border:2px solid #FFFFFF; box-shadow:0 2px 4px rgba(0,0,0,0.3);">${index}</div>`;

        const customIcon = L.divIcon({
          html: iconHtml,
          className: "custom-map-pin",
          iconSize: isDepot ? [26, 26] : [22, 22],
          iconAnchor: isDepot ? [13, 13] : [11, 11],
        });

        const marker = L.marker([lm.lat, lm.lon], { icon: customIcon });
        marker.bindPopup(
          `<div style="font-family:inherit; padding:4px;">
            <strong style="font-size:13px;">${lm.name}</strong>
            <p style="margin:4px 0 0 0; font-size:11px; opacity:0.8;">${lm.desc || "Delivery Waypoint"}</p>
            <p style="margin:2px 0 0 0; font-family:monospace; font-size:10px; opacity:0.6;">[${lm.lat.toFixed(4)}, ${lm.lon.toFixed(4)}]</p>
          </div>`
        );
        marker.addTo(markersLayerRef.current!);
      });
    }

    // Auto-fit bounds
    const allCoords = [...beforeCoordinates, ...afterCoordinates, ...alternativeCoordinates];
    if (allCoords.length > 1) {
      const bounds = L.latLngBounds(allCoords);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
    }
  }, [beforeCoordinates, afterCoordinates, alternativeCoordinates, landmarks, viewMode]);

  // Handle Morph / Transition Animation
  const handleTransition = () => {
    setIsTransitioning(true);
    setViewMode("baseline");
    setTimeout(() => {
      setViewMode("alternative");
      setTimeout(() => {
        setViewMode("optimal");
        setTimeout(() => {
          setViewMode("all");
          setIsTransitioning(false);
        }, 1200);
      }, 1200);
    }, 1200);
  };

  return (
    <div className="relative w-full h-full min-h-[480px] rounded-md border border-border overflow-hidden bg-bg-surface flex flex-col">
      {/* Top Map Control Bar */}
      <div className="absolute top-3 right-3 z-[1000] flex items-center gap-1.5 bg-bg-surface/90 backdrop-blur-md px-2 py-1.5 rounded border border-border text-xs">
        <span className="text-text-secondary pr-1 font-medium">Route:</span>
        <button
          onClick={() => setViewMode("all")}
          className={`px-2 py-1 rounded transition-colors ${
            viewMode === "all"
              ? "bg-text-primary text-bg-surface font-semibold"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          All
        </button>
        <button
          onClick={() => setViewMode("optimal")}
          className={`px-2 py-1 rounded transition-colors ${
            viewMode === "optimal"
              ? "bg-signal-green text-bg-base font-semibold"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          Optimal (Green)
        </button>
        <button
          onClick={() => setViewMode("alternative")}
          className={`px-2 py-1 rounded transition-colors ${
            viewMode === "alternative"
              ? "bg-[#F5A623] text-bg-base font-semibold"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          Alternative (Yellow)
        </button>
        <button
          onClick={() => setViewMode("baseline")}
          className={`px-2 py-1 rounded transition-colors ${
            viewMode === "baseline"
              ? "bg-signal-red text-white font-semibold"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          Baseline (Red)
        </button>
        <button
          onClick={handleTransition}
          disabled={isTransitioning}
          className="ml-1 px-2 py-1 rounded bg-bg-base border border-border text-text-primary hover:border-signal-amber transition-colors disabled:opacity-50"
        >
          {isTransitioning ? "Transitioning..." : "Play Transition"}
        </button>
      </div>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-bg-surface/90 backdrop-blur-md px-3 py-2 rounded border border-border text-xs flex flex-col gap-1.5">
        <div className="flex items-center gap-2">
          <span className="w-4 h-1 bg-signal-green rounded"></span>
          <span className="text-text-primary font-medium">Selected Best Route (Optimal)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-1 bg-[#F5A623] rounded"></span>
          <span className="text-text-primary font-medium">{alternativeName} (Yellow Alternative)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-0.5 border-b-2 border-dashed border-signal-red"></span>
          <span className="text-text-secondary">Unoptimized Baseline Route</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-signal-amber"></span>
          <span className="text-text-secondary">Depot / Start Hub</span>
        </div>
      </div>

      {/* Actual Leaflet Map Canvas */}
      <div ref={mapContainerRef} className="w-full flex-1 z-0" />
    </div>
  );
}
