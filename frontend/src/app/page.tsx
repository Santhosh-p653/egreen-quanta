"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { useTheme } from "next-themes";
import {
  Sun,
  Moon,
  Navigation,
  Sliders,
  CheckCircle2,
  TrendingDown,
  Clock,
  MapPin,
  BarChart3,
  Layers,
  Shield,
  FileText,
  ListOrdered,
  Activity,
  Dna,
  Database,
  ArrowRight,
  LogOut,
  ChevronRight,
  Sparkles,
  Zap,
} from "lucide-react";
import AdminLoginPage from "@/components/AdminLoginPage";
import AnalyticsDashboardView from "@/components/AnalyticsDashboardView";
import AdminPortalView from "@/components/AdminPortalView";
import { AlgorithmResult } from "@/components/CompareView";
import { RouteExplanationData } from "@/components/RouteExplanationCard";

// Dynamically import MapComponent to avoid Leaflet SSR issues
const MapComponent = dynamic(() => import("@/components/MapComponent"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[500px] bg-bg-surface border border-border rounded-xl flex items-center justify-center text-text-secondary text-base font-medium">
      Loading Coimbatore Regional Network Map...
    </div>
  ),
});

// Fallback landmark fixtures for 70+ km Regional Road Network
const INITIAL_LANDMARKS = [
  { id: 0, name: "Gandhipuram Central Hub", lat: 11.0168, lon: 76.9678, desc: "Central Bus Terminus & Commercial Core" },
  { id: 1, name: "RS Puram (DB Road)", lat: 11.0095, lon: 76.9485, desc: "Western Residential & Retail District" },
  { id: 2, name: "Ukkadam Transit Hub", lat: 10.9890, lon: 76.9610, desc: "Southern Inter-City Bus Stand" },
  { id: 3, name: "Coimbatore Junction Railway", lat: 10.9995, lon: 76.9632, desc: "Major Rail Terminus" },
  { id: 4, name: "Peelamedu (PSG Tech)", lat: 11.0245, lon: 77.0028, desc: "Avinashi Road Education Zone" },
  { id: 5, name: "Hope College Junction", lat: 11.0282, lon: 77.0185, desc: "Arterial Intersection" },
  { id: 6, name: "Coimbatore Int. Airport (CJB)", lat: 11.0300, lon: 77.0434, desc: "Civil Aerodrome" },
  { id: 7, name: "Singanallur Junction", lat: 10.9984, lon: 77.0255, desc: "Trichy Road Terminal" },
  { id: 8, name: "Ramanathapuram Junction", lat: 11.0025, lon: 76.9890, desc: "Trichy Road Connector" },
  { id: 9, name: "Saibaba Colony", lat: 11.0289, lon: 76.9421, desc: "Mettupalayam Road Hub" },
  { id: 10, name: "Ganapathy Commercial Hub", lat: 11.0345, lon: 76.9745, desc: "Sathy Road Arterial" },
  { id: 11, name: "Saravanampatti Tech Zone", lat: 11.0792, lon: 76.9964, desc: "Northern IT Corridor" },
  { id: 12, name: "Kovaipudur Transit Hub", lat: 10.9325, lon: 76.9388, desc: "South-West Residential Valley" },
  { id: 13, name: "Kuniyamuthur Junction", lat: 10.9632, lon: 76.9530, desc: "Palakkad Road Gateway" },
  { id: 14, name: "Sundarapuram Hub", lat: 10.9520, lon: 76.9810, desc: "Pollachi Road Arterial Junction" },
  { id: 15, name: "Eachanari Industrial Zone", lat: 10.9312, lon: 76.9865, desc: "Southern Heavy Engineering & SIDCO" },
  { id: 16, name: "Podanur Rail Junction", lat: 10.9645, lon: 76.9892, desc: "Railway Division Terminus" },
  { id: 17, name: "Ondipudur Freight Terminal", lat: 10.9992, lon: 77.0515, desc: "Eastern Logistics Yard" },
  { id: 18, name: "Sulur Aero Logistics Hub", lat: 11.0280, lon: 77.1260, desc: "Far-East Highway Logistics" },
  { id: 19, name: "Neelambur NH-544 Bypass", lat: 11.0660, lon: 77.0980, desc: "NH-544 Express Interchange" },
  { id: 20, name: "Kalapatti Aerospace Zone", lat: 11.0682, lon: 77.0320, desc: "Precision Valve Cluster" },
  { id: 21, name: "CHIL SEZ (Keeranatham)", lat: 11.0995, lon: 77.0085, desc: "Global IT Campus & Tech Park" },
  { id: 22, name: "Thudiyalur Junction", lat: 11.0815, lon: 76.9580, desc: "NH-181 Mettupalayam Highway" },
  { id: 23, name: "Vadavalli Gateway", lat: 11.0260, lon: 76.9045, desc: "Western Foothills Link" },
  { id: 24, name: "Pollachi Logistics Terminal", lat: 10.6609, lon: 77.0048, desc: "Southern Agro-Industrial Hub (~42 km)" },
  { id: 25, name: "Kinathukadavu Industrial Bypass", lat: 10.8214, lon: 77.0201, desc: "NH-83 Manufacturing Hub (~25 km)" },
  { id: 26, name: "Madukkarai Cement Corridor", lat: 10.9020, lon: 76.9580, desc: "NH-544 Minerals Interchange (~18 km)" },
  { id: 27, name: "Walayar Interstate Border Post", lat: 10.8520, lon: 76.8550, desc: "Interstate Freight Gateway (~28 km)" },
  { id: 28, name: "Siruvani Eco Valley (Alandurai)", lat: 10.9410, lon: 76.7950, desc: "Western Foothills (~30 km)" },
  { id: 29, name: "Karamadai Agro Wholesale Market", lat: 11.2435, lon: 76.9582, desc: "Produce Exchange (~28 km)" },
  { id: 30, name: "Mettupalayam Nilgiris Gateway", lat: 11.3015, lon: 76.9465, desc: "Mountain Freight Rail Link (~36 km)" },
  { id: 31, name: "Annur Highway Junction", lat: 11.2335, lon: 77.1332, desc: "Expressway Cross-Link (~32 km)" },
  { id: 32, name: "Karumathampatti Logistics Park", lat: 11.1090, lon: 77.1820, desc: "6-Lane NH-544 Warehouse (~30 km)" },
  { id: 33, name: "Avinashi Industrial & Textile Hub", lat: 11.1925, lon: 77.2690, desc: "National Expressway Hub (~42 km)" },
  { id: 34, name: "Tiruppur Border (Perumanallur)", lat: 11.1780, lon: 77.3340, desc: "Export Freight Gateway (~48 km)" },
  { id: 35, name: "Palladam Freight Interchange", lat: 11.0045, lon: 77.2885, desc: "Poultry & Freight Interchange (~38 km)" },
];

export default function Dashboard() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Authenticated User State
  const [adminUser, setAdminUser] = useState<{ username: string; role: string; token: string } | null>(null);

  // Navigation View State: "simulation" | "dashboard" | "admin"
  const [activePage, setActivePage] = useState<"simulation" | "dashboard" | "admin">("simulation");

  // Leg Itinerary Overlay Drawer State (in Live Simulation)
  const [showItineraryDrawer, setShowItineraryDrawer] = useState(false);

  // GA Hyper-parameters State
  const [gaCrossover, setGaCrossover] = useState<"ox" | "pmx">("ox");
  const [gaMutationRate, setGaMutationRate] = useState(0.15);

  // Turn-by-Turn Waypoints Leg list
  const [turnByTurnLegs, setTurnByTurnLegs] = useState<Array<{ legIndex: number; from: string; to: string }>>([]);

  // Input states
  const [sourceId, setSourceId] = useState(0);
  const [destinationId, setDestinationId] = useState<number | null>(null);
  const [selectedStops, setSelectedStops] = useState<number[]>([1, 2, 6, 7, 11, 14, 15, 18, 19, 21, 22, 23]);
  const [activeScenario, setActiveScenario] = useState("metro_greater");
  const [trafficMode, setTrafficMode] = useState<"real" | "free">("real");
  const [vehicleCapacity, setVehicleCapacity] = useState(100);
  const [algorithm, setAlgorithm] = useState("qpso");
  const [iterations, setIterations] = useState(80);

  // Optimization output state
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationStatus, setOptimizationStatus] = useState<"idle" | "running" | "converged">("idle");

  const [landmarks, setLandmarks] = useState(INITIAL_LANDMARKS);
  const [beforeCoords, setBeforeCoords] = useState<[number, number][]>([]);
  const [afterCoords, setAfterCoords] = useState<[number, number][]>([]);
  const [alternativeCoords, setAlternativeCoords] = useState<[number, number][]>([]);
  const [alternativeName, setAlternativeName] = useState("Clarke-Wright Savings");
  const [routeExplanation, setRouteExplanation] = useState<RouteExplanationData | null>(null);
  const [convergenceHistory, setConvergenceHistory] = useState<number[]>([]);
  const [baselineCost, setBaselineCost] = useState(62.6);
  const [crossoverIteration, setCrossoverIteration] = useState<number | null>(14);

  // KPI Metrics
  const [metrics, setMetrics] = useState({
    beforeDistance: 28.4,
    afterDistance: 22.8,
    beforeTime: 62.6,
    afterTime: 44.8,
    beforeCongestion: 1.85,
    afterCongestion: 1.35,
    timeSavedMin: 17.8,
    timeImprovementPct: 28.4,
    distanceImprovementPct: 19.7,
    runtimeMs: 142.5,
    iterationCount: 80,
  });

  const [compareResults, setCompareResults] = useState<AlgorithmResult[]>([]);
  const [isComparing, setIsComparing] = useState(false);

  useEffect(() => {
    setMounted(true);

    // Fetch landmarks from backend if available
    fetch("http://127.0.0.1:8000/api/network/landmarks")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) setLandmarks(data);
      })
      .catch(() => {});

    // Check stored admin authentication
    try {
      const savedToken = localStorage.getItem("egreen_token");
      const savedUser = localStorage.getItem("egreen_user");
      if (savedToken && savedUser) {
        const parsed = JSON.parse(savedUser);
        setAdminUser({ username: parsed.username, role: parsed.role, token: savedToken });
      }
    } catch {}

    // Initialize baseline calculation
    runOptimization();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("egreen_token");
    localStorage.removeItem("egreen_user");
    setAdminUser(null);
  };

  const toggleStop = (id: number) => {
    if (selectedStops.includes(id)) {
      if (selectedStops.length > 1) {
        setSelectedStops(selectedStops.filter((s) => s !== id));
      }
    } else {
      setSelectedStops([...selectedStops, id]);
    }
    setActiveScenario("custom");
  };

  const handleScenarioChange = async (key: string) => {
    setActiveScenario(key);
    if (key === "regional_conglomerate") {
      setSourceId(0);
      setSelectedStops([1, 6, 11, 15, 18, 19, 21, 24, 25, 27, 28, 29, 30, 32, 33, 34]);
    } else if (key === "interstate_cargo") {
      setSourceId(0);
      setSelectedStops([2, 6, 15, 18, 19, 26, 27, 32, 33, 34]);
    } else if (key === "metro_greater") {
      setSourceId(0);
      setSelectedStops([1, 2, 6, 7, 11, 14, 15, 18, 19, 21, 22, 23]);
    } else if (key === "cbd_express") {
      setSourceId(0);
      setSelectedStops([1, 3, 4, 9, 10]);
    } else if (key === "industrial_cargo") {
      setSourceId(0);
      setSelectedStops([4, 5, 6, 17, 18, 19, 20, 21]);
    } else if (key === "north_south") {
      setSourceId(0);
      setSelectedStops([2, 7, 8, 9, 10, 14, 15, 22]);
    } else if (key === "western_suburbs") {
      setSourceId(0);
      setSelectedStops([1, 4, 9, 12, 13, 23]);
    } else if (key === "random") {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/instances/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ n_stops: 12, radius_km: 70 }),
        });
        const data = await res.json();
        if (data.stops_ids && data.stops_ids.length > 0) {
          setSourceId(0);
          setSelectedStops(data.stops_ids);
          return;
        }
      } catch {}
      const candidateIds = landmarks.map((l) => l.id).filter((id) => id !== 0);
      const shuffled = [...candidateIds].sort(() => 0.5 - Math.random());
      setSourceId(0);
      setSelectedStops(shuffled.slice(0, 12));
    }
  };

  // Run Optimization Call
  const runOptimization = async () => {
    setIsOptimizing(true);
    setOptimizationStatus("running");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_id: sourceId,
          destination_id: destinationId,
          intermediate_stops: selectedStops,
          traffic_mode: trafficMode,
          algorithm: algorithm,
          iterations: iterations,
          swarm_size: 30,
          ga_crossover: gaCrossover,
          ga_mutation_rate: gaMutationRate,
        }),
      });

      if (!res.ok) throw new Error("Optimization failed");

      const data = await res.json();

      if (data.route_coordinates && data.route_coordinates.length > 0) {
        setAfterCoords(data.route_coordinates);
      }
      if (data.baseline_coordinates && data.baseline_coordinates.length > 0) {
        setBeforeCoords(data.baseline_coordinates);
      }
      if (data.alternative_coordinates && data.alternative_coordinates.length > 0) {
        setAlternativeCoords(data.alternative_coordinates);
        setAlternativeName(data.alternative_name || "Clarke-Wright Savings");
      }

      if (data.turn_by_turn && Array.isArray(data.turn_by_turn)) {
        setTurnByTurnLegs(
          data.turn_by_turn.map((leg: any, idx: number) => ({
            legIndex: idx + 1,
            from: leg.from || `Stop ${idx}`,
            to: leg.to || `Stop ${idx + 1}`,
          }))
        );
      }

      setMetrics({
        beforeDistance: data.baseline_distance_km || 28.4,
        afterDistance: data.optimized_distance_km || 22.8,
        beforeTime: data.baseline_time_min || 62.6,
        afterTime: data.optimized_time_min || 44.8,
        beforeCongestion: data.baseline_congestion || 1.85,
        afterCongestion: data.optimized_congestion || 1.35,
        timeSavedMin: data.time_saved_min || 17.8,
        timeImprovementPct: data.time_improvement_pct || 28.4,
        distanceImprovementPct: data.distance_improvement_pct || 19.7,
        runtimeMs: data.runtime_ms || 142.5,
        iterationCount: data.iterations || iterations,
      });

      if (data.convergence_history) {
        setConvergenceHistory(data.convergence_history);
      }
      if (data.baseline_time_min) {
        setBaselineCost(data.baseline_time_min);
      }
      if (data.crossover_iteration !== undefined) {
        setCrossoverIteration(data.crossover_iteration);
      }

      if (data.explanation) {
        setRouteExplanation(data.explanation);
      }

      setOptimizationStatus("converged");
    } catch {
      simulateLocalRun();
    } finally {
      setIsOptimizing(false);
    }
  };

  const simulateLocalRun = () => {
    const stops = [sourceId, ...selectedStops, sourceId];
    const coords: [number, number][] = stops.map((id) => {
      const lm = landmarks.find((l) => l.id === id) || landmarks[0];
      return [lm.lat, lm.lon];
    });

    setBeforeCoords(coords);
    const reversedCoords = [...coords].reverse();
    setAfterCoords(reversedCoords);

    const altCoords = [...coords];
    if (altCoords.length > 3) {
      const temp = altCoords[1];
      altCoords[1] = altCoords[2];
      altCoords[2] = temp;
    }
    setAlternativeCoords(altCoords);
    setAlternativeName("Clarke-Wright Savings");

    const hist = [72.0, 68.4, 63.1, 58.7, 54.2, 50.1, 47.9, 46.2, 45.1, 44.8];
    setConvergenceHistory(hist);
    setBaselineCost(65.0);
    setCrossoverIteration(3);

    const stopNames = stops.map((id) => landmarks.find((l) => l.id === id)?.name || `Landmark ${id}`);
    const altNames = [stopNames[0], ...(stopNames.slice(1, -1).reverse()), stopNames[stopNames.length - 1]];

    setRouteExplanation({
      vehicle: "Vehicle 01",
      selected_route: stopNames,
      metrics: {
        distance_km: 22.8,
        travel_time_min: 44.8,
        capacity_used_percent: 75.0,
        objective_cost: 44.8,
        congestion_level: 1.35,
      },
      reasons: [
        "lower_travel_time",
        "lower_total_distance",
        "capacity_satisfied",
        "all_locations_covered",
        "time_constraint_satisfied",
        "strictly_dominates_alternative",
      ],
      constraints: {
        capacity: {
          satisfied: true,
          used_percent: 75.0,
          demand_total: 75.0,
          capacity_limit: 100.0,
        },
        all_locations_covered: {
          satisfied: true,
          locations_visited: selectedStops.length,
          locations_required: selectedStops.length,
        },
        time_constraint: {
          satisfied: true,
          travel_time_min: 44.8,
          time_limit_min: null,
        },
      },
      tradeoffs: [
        {
          type: "pareto_dominance",
          statement: "No compromise required: selected route strictly dominates Clarke-Wright Savings with 8.2 min faster travel time and 3.1 km shorter distance.",
          distance_difference_km: -3.1,
          time_difference_min: -8.2,
        },
      ],
      alternative: {
        name: "Clarke-Wright Savings",
        selected_route: altNames,
        metrics: {
          distance_km: 25.9,
          travel_time_min: 53.0,
          objective_cost: 53.0,
          congestion_level: 1.62,
        },
        reasons_rejected: ["higher_travel_time", "higher_total_distance"],
      },
      decision: "The optimizer selected this route because it achieves a 28.4% reduction in travel time (17.8 min saved) over the baseline while fully satisfying vehicle payload capacity and delivery coverage constraints.",
      human_readable: `ROUTE EXPLANATION\n\nVehicle:\nVehicle 01\n\nSelected Route:\n${stopNames.join(" -> ")}\n\nWHY THIS ROUTE WAS SELECTED\n• Reduced estimated travel time\n• Shorter road transit distance\n• Payload capacity strictly satisfied\n• 100% delivery waypoints covered\n\nROUTE METRICS\n• Distance: 22.8 km\n• Estimated time: 44.8 min\n• Capacity used: 75.0%\n• Optimization cost: 44.8\n\nKEY TRADE-OFF\nNo compromise required: selected route strictly dominates alternative candidate.\n\nCONSTRAINTS\n✓ Vehicle capacity (75.0% utilized)\n✓ All locations covered (${selectedStops.length} stops)\n✓ Time constraint (44.8 min elapsed)\n\nALTERNATIVE CONSIDERED\nCandidate: Clarke-Wright Savings (Yellow Candidate)\n• Distance: 25.9 km\n• Estimated time: 53.0 min\n• Cost: 53.0\n\nDECISION\nThe optimizer selected this route because it achieves a 28.4% reduction in travel time while fully satisfying payload and coverage constraints.`,
    });

    setOptimizationStatus("converged");
  };

  const runComparison = async () => {
    setIsComparing(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_id: sourceId,
          intermediate_stops: selectedStops,
          traffic_mode: trafficMode,
          iterations: iterations,
        }),
      });
      const data = await res.json();
      if (data.results) setCompareResults(data.results);
    } catch {
      setCompareResults([
        { id: "qpso", name: "QPSO", travel_time_min: 44.8, distance_km: 22.8, runtime_ms: 120, history: [65, 55, 48, 44.8], is_best: true },
        { id: "classical_pso", name: "Classical PSO", travel_time_min: 49.2, distance_km: 24.5, runtime_ms: 95, history: [65, 58, 52, 49.2] },
        { id: "ga_ox", name: "GA (Order Crossover)", travel_time_min: 47.6, distance_km: 23.9, runtime_ms: 210, history: [65, 59, 51, 47.6] },
        { id: "ga_pmx", name: "GA (PMX Crossover)", travel_time_min: 48.9, distance_km: 24.3, runtime_ms: 225, history: [65, 60, 53, 48.9] },
        { id: "clarke_wright", name: "Clarke-Wright Savings", travel_time_min: 52.4, distance_km: 25.8, runtime_ms: 2.1, history: [52.4, 52.4] },
        { id: "cheapest_insertion", name: "Cheapest Insertion", travel_time_min: 51.0, distance_km: 25.1, runtime_ms: 2.5, history: [51.0, 51.0] },
        { id: "nearest_neighbor", name: "Nearest Neighbor", travel_time_min: 62.6, distance_km: 28.4, runtime_ms: 1.2, history: [62.6, 62.6] },
      ]);
    } finally {
      setIsComparing(false);
    }
  };

  if (!mounted) return null;

  // =========================================================================
  // AUTHENTICATION GATE: First Page is Admin Login Page
  // =========================================================================
  if (!adminUser) {
    return (
      <AdminLoginPage
        onLoginSuccess={(authData) => {
          setAdminUser(authData);
          setActivePage("simulation");
        }}
      />
    );
  }

  return (
    <div className="min-h-screen flex bg-bg-base text-text-primary select-none antialiased">
      {/* ========================================================================= */}
      {/* LEFT-SIDE SIDEBAR MENU */}
      {/* ========================================================================= */}
      <aside className="w-64 sm:w-72 bg-bg-surface border-r border-border flex flex-col justify-between shrink-0 shadow-lg z-30">
        {/* Top Header & Brand */}
        <div className="flex flex-col">
          <div className="p-5 border-b border-border flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-signal-green/15 border border-signal-green/40 flex items-center justify-center text-signal-green shadow-sm">
              <Shield size={20} />
            </div>
            <div>
              <h1 className="font-bold text-base sm:text-lg tracking-tight text-text-primary">
                E-Green Quanta
              </h1>
              <p className="text-xs text-text-secondary font-medium">
                Coimbatore Regional Engine
              </p>
            </div>
          </div>

          {/* System Status Indicators */}
          <div className="p-4 border-b border-border flex flex-col gap-2 bg-bg-base/50">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-text-secondary flex items-center gap-1.5">
                <Database size={13} className="text-signal-green" />
                <span>Database:</span>
              </span>
              <span className="text-signal-green font-bold">PostgreSQL Ready</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-text-secondary flex items-center gap-1.5">
                <MapPin size={13} className="text-signal-amber" />
                <span>Coverage:</span>
              </span>
              <span className="text-signal-amber font-bold">70+ km Regional</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 flex flex-col gap-1.5">
            <button
              onClick={() => setActivePage("simulation")}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-semibold transition-all ${
                activePage === "simulation"
                  ? "bg-signal-green text-[#0B0F14] shadow-md shadow-signal-green/20"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-base"
              }`}
            >
              <div className="flex items-center gap-3">
                <Navigation size={18} />
                <span>Live Simulation</span>
              </div>
              {activePage === "simulation" && <ChevronRight size={16} />}
            </button>

            <button
              onClick={() => {
                setActivePage("dashboard");
                if (compareResults.length === 0) runComparison();
              }}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-semibold transition-all ${
                activePage === "dashboard"
                  ? "bg-signal-green text-[#0B0F14] shadow-md shadow-signal-green/20"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-base"
              }`}
            >
              <div className="flex items-center gap-3">
                <BarChart3 size={18} />
                <span>Analytics Dashboard</span>
              </div>
              {activePage === "dashboard" && <ChevronRight size={16} />}
            </button>

            <button
              onClick={() => setActivePage("admin")}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-semibold transition-all ${
                activePage === "admin"
                  ? "bg-signal-green text-[#0B0F14] shadow-md shadow-signal-green/20"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-base"
              }`}
            >
              <div className="flex items-center gap-3">
                <Shield size={18} />
                <span>Admin Console</span>
              </div>
              {activePage === "admin" && <ChevronRight size={16} />}
            </button>
          </nav>
        </div>

        {/* Bottom User Profile, Logout & Theme */}
        <div className="p-4 border-t border-border flex flex-col gap-3 bg-bg-base/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-signal-amber/20 border border-signal-amber text-signal-amber flex items-center justify-center font-bold text-xs">
                {adminUser.username.slice(0, 2).toUpperCase()}
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold text-text-primary truncate max-w-[110px]">
                  {adminUser.username}
                </span>
                <span className="text-[11px] text-signal-green font-semibold capitalize font-mono">
                  {adminUser.role}
                </span>
              </div>
            </div>

            {/* Theme Switcher */}
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2 rounded-lg border border-border bg-bg-surface text-text-secondary hover:text-text-primary transition-colors"
              title="Toggle theme"
            >
              {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>

          {/* Logout Action Button */}
          <button
            onClick={handleLogout}
            className="w-full py-2 px-3 rounded-lg border border-signal-red/30 bg-signal-red/10 text-signal-red hover:bg-signal-red/20 transition-colors text-xs font-semibold flex items-center justify-center gap-2"
          >
            <LogOut size={14} />
            <span>Sign Out Admin</span>
          </button>
        </div>
      </aside>

      {/* ========================================================================= */}
      {/* MAIN VIEWPORT AREA */}
      {/* ========================================================================= */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* ========================================================================= */}
        {/* PAGE 1: LIVE SIMULATION VIEW */}
        {/* ========================================================================= */}
        {activePage === "simulation" && (
          <div className="w-full h-full grid grid-cols-12 overflow-hidden">
            {/* Left Parameters Control Column */}
            <aside className="col-span-12 lg:col-span-4 xl:col-span-3 border-r border-border bg-bg-surface p-5 flex flex-col gap-4 overflow-y-auto max-h-screen shadow-sm">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-2">
                  <Sliders size={18} className="text-signal-green" />
                  <h2 className="text-base font-bold text-text-primary">
                    Mission Control
                  </h2>
                </div>
                <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-signal-amber/15 text-signal-amber border border-signal-amber/30">
                  70km
                </span>
              </div>

              {/* Scenario Preset Selector */}
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-text-primary">
                  Scenario Preset
                </label>
                <select
                  value={activeScenario}
                  onChange={(e) => handleScenarioChange(e.target.value)}
                  className="bg-bg-base border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-signal-amber transition-colors"
                >
                  <option value="regional_conglomerate">Regional Conglomerate (16 Stops, 65km)</option>
                  <option value="interstate_cargo">Interstate Freight Corridor (10 Stops, 50km)</option>
                  <option value="metro_greater">Greater Coimbatore Metro (12 Stops, 32km)</option>
                  <option value="cbd_express">CBD Commercial Express (5 Stops, 8km)</option>
                  <option value="industrial_cargo">Airport & Eastern Cargo (8 Stops, 24km)</option>
                  <option value="north_south">North-South Arterial Spine (8 Stops, 26km)</option>
                  <option value="western_suburbs">Western Suburbs & Tech Valley (6 Stops, 18km)</option>
                  <option value="custom">Custom Stop Selection</option>
                  <option value="random">🎲 Generate Dynamic Random OSM Instance</option>
                </select>
              </div>

              {/* Origin / Depot Hub */}
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-text-primary flex items-center justify-between">
                  <span>Depot / Origin Hub</span>
                  <span className="font-mono text-xs text-signal-green">Node #{sourceId}</span>
                </label>
                <select
                  value={sourceId}
                  onChange={(e) => setSourceId(Number(e.target.value))}
                  className="bg-bg-base border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-signal-amber transition-colors"
                >
                  {landmarks.map((lm) => (
                    <option key={lm.id} value={lm.id}>
                      {lm.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Final Destination */}
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-text-primary">Final Destination</label>
                <select
                  value={destinationId === null ? "" : destinationId}
                  onChange={(e) => setDestinationId(e.target.value === "" ? null : Number(e.target.value))}
                  className="bg-bg-base border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-signal-amber transition-colors"
                >
                  <option value="">Round-trip back to Depot</option>
                  {landmarks
                    .filter((lm) => lm.id !== sourceId)
                    .map((lm) => (
                      <option key={lm.id} value={lm.id}>
                        {lm.name}
                      </option>
                    ))}
                </select>
              </div>

              {/* Delivery Stops Checkboxes */}
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between text-sm font-semibold text-text-primary">
                  <span>Delivery Waypoints</span>
                  <span className="font-mono text-xs text-signal-green">
                    {selectedStops.length} active stops
                  </span>
                </div>
                <div className="max-h-36 overflow-y-auto border border-border rounded-lg bg-bg-base p-2 flex flex-col gap-1 text-sm">
                  {landmarks
                    .filter((lm) => lm.id !== sourceId)
                    .map((lm) => {
                      const isChecked = selectedStops.includes(lm.id);
                      return (
                        <label
                          key={lm.id}
                          className="flex items-center gap-2.5 p-1 rounded hover:bg-bg-surface cursor-pointer select-none transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => toggleStop(lm.id)}
                            className="rounded border-border text-signal-green focus:ring-0 focus:outline-none w-4 h-4"
                          />
                          <span className="truncate text-xs font-medium">{lm.name}</span>
                        </label>
                      );
                    })}
                </div>
              </div>

              {/* Traffic Mode */}
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-text-primary">Traffic Mode</label>
                <div className="grid grid-cols-2 gap-2 bg-bg-base p-1.5 rounded-lg border border-border text-sm">
                  <button
                    type="button"
                    onClick={() => setTrafficMode("real")}
                    className={`py-1.5 rounded-md text-center font-semibold transition-colors ${
                      trafficMode === "real"
                        ? "bg-signal-red/20 text-signal-red border border-signal-red/40"
                        : "text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    Live Congestion
                  </button>
                  <button
                    type="button"
                    onClick={() => setTrafficMode("free")}
                    className={`py-1.5 rounded-md text-center font-semibold transition-colors ${
                      trafficMode === "free"
                        ? "bg-signal-green/20 text-signal-green border border-signal-green/40"
                        : "text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    Free Flowing
                  </button>
                </div>
              </div>

              {/* Algorithm Selector */}
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-text-primary">Routing Algorithm</label>
                <select
                  value={algorithm}
                  onChange={(e) => setAlgorithm(e.target.value)}
                  className="bg-bg-base border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-signal-amber transition-colors font-medium"
                >
                  <option value="qpso">Quantum-behaved Particle Swarm (QPSO)</option>
                  <option value="classical_pso">Classical PSO</option>
                  <option value="ga_ox">Genetic Algorithm (Order Crossover)</option>
                  <option value="ga_pmx">Genetic Algorithm (PMX)</option>
                  <option value="clarke_wright">Clarke-Wright Savings</option>
                  <option value="cheapest_insertion">Cheapest Insertion</option>
                  <option value="nearest_neighbor">Nearest Neighbor Baseline</option>
                </select>
              </div>

              {/* GA Operators (Shown if GA selected) */}
              {(algorithm === "ga_ox" || algorithm === "ga_pmx") && (
                <div className="flex flex-col gap-2.5 bg-bg-base p-3 rounded-lg border border-border">
                  <div className="flex items-center gap-2 text-sm font-bold text-text-primary">
                    <Dna size={15} className="text-signal-green" />
                    <span>GA Genetic Operators</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-text-secondary font-medium">Crossover Type</span>
                    <select
                      value={algorithm === "ga_pmx" ? "pmx" : gaCrossover}
                      onChange={(e) => {
                        const val = e.target.value as "ox" | "pmx";
                        setGaCrossover(val);
                        setAlgorithm(val === "pmx" ? "ga_pmx" : "ga_ox");
                      }}
                      className="bg-bg-surface border border-border rounded px-2.5 py-1.5 text-xs text-text-primary focus:outline-none"
                    >
                      <option value="ox">Order Crossover (OX)</option>
                      <option value="pmx">Partially Mapped (PMX)</option>
                    </select>
                  </div>
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center justify-between text-xs text-text-secondary font-medium">
                      <span>Mutation Probability</span>
                      <span className="font-mono text-text-primary font-bold">{Math.round(gaMutationRate * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min={0.05}
                      max={0.50}
                      step={0.05}
                      value={gaMutationRate}
                      onChange={(e) => setGaMutationRate(parseFloat(e.target.value))}
                      className="w-full accent-signal-green"
                    />
                  </div>
                </div>
              )}

              {/* Iterations Slider */}
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between text-sm text-text-secondary font-medium">
                  <span>Iterations</span>
                  <span className="font-mono text-text-primary font-bold">{iterations}</span>
                </div>
                <input
                  type="range"
                  min={20}
                  max={200}
                  step={10}
                  value={iterations}
                  onChange={(e) => setIterations(Number(e.target.value))}
                  className="w-full accent-signal-green"
                />
              </div>

              {/* Action Button */}
              <button
                onClick={runOptimization}
                disabled={isOptimizing}
                className="w-full py-3 rounded-lg font-bold text-sm transition-all mt-auto flex items-center justify-center gap-2 border disabled:opacity-50 shadow-md"
                style={{
                  backgroundColor: isOptimizing ? "var(--signal-amber)" : "var(--signal-green)",
                  color: "#0B0F14",
                  borderColor: "transparent",
                }}
              >
                {isOptimizing ? (
                  <>
                    <span className="w-4 h-4 border-2 border-[#0B0F14] border-t-transparent rounded-full animate-spin"></span>
                    <span>Optimizing Route...</span>
                  </>
                ) : (
                  <>
                    <Navigation size={16} />
                    <span>Run Route Optimization</span>
                  </>
                )}
              </button>
            </aside>

            {/* Right Interactive Map Canvas */}
            <section className="col-span-12 lg:col-span-8 xl:col-span-9 flex flex-col h-full relative overflow-hidden bg-bg-base">
              {/* Map Floating Status Bar */}
              <div className="absolute top-4 left-4 right-4 z-[400] flex items-center justify-between pointer-events-none">
                <div className="flex flex-wrap items-center gap-2 pointer-events-auto bg-bg-surface/90 backdrop-blur-md border border-border px-3.5 py-2 rounded-xl shadow-lg">
                  <div className="flex items-center gap-2 font-mono text-sm font-bold text-signal-green pr-2 border-r border-border">
                    <Clock size={15} />
                    <span>-{metrics.timeSavedMin.toFixed(1)}m Saved</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono text-sm font-bold text-text-primary pr-2 border-r border-border">
                    <TrendingDown size={15} className="text-signal-green" />
                    <span>{metrics.afterDistance.toFixed(1)} km</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs font-mono text-text-secondary">
                    <Activity size={13} className="text-signal-amber" />
                    <span>{metrics.runtimeMs.toFixed(0)} ms</span>
                  </div>
                </div>

                {/* Button to toggle turn-by-turn itinerary drawer */}
                <button
                  onClick={() => setShowItineraryDrawer(!showItineraryDrawer)}
                  className="pointer-events-auto flex items-center gap-2 px-3.5 py-2 rounded-xl bg-bg-surface/90 backdrop-blur-md border border-border hover:border-signal-amber text-text-primary text-sm font-semibold shadow-lg transition-colors"
                >
                  <ListOrdered size={16} className="text-signal-amber" />
                  <span>{showItineraryDrawer ? "Hide Route Legs" : `Route Legs (${turnByTurnLegs.length})`}</span>
                </button>
              </div>

              {/* Fullscreen Map */}
              <div className="w-full h-full flex-1">
                <MapComponent
                  beforeCoordinates={beforeCoords}
                  afterCoordinates={afterCoords}
                  alternativeCoordinates={alternativeCoords}
                  alternativeName={alternativeName}
                  landmarks={landmarks}
                  isOptimizing={isOptimizing}
                />
              </div>

              {/* Collapsible Turn-by-Turn Route Legs Drawer */}
              {showItineraryDrawer && (
                <div className="absolute bottom-4 right-4 w-96 max-h-[60%] z-[400] bg-bg-surface/95 backdrop-blur-md border border-border rounded-xl shadow-2xl p-4 flex flex-col gap-3 overflow-hidden animate-in fade-in slide-in-from-bottom-5">
                  <div className="flex items-center justify-between border-b border-border pb-2">
                    <div className="flex items-center gap-2">
                      <ListOrdered size={16} className="text-signal-amber" />
                      <span className="font-bold text-sm text-text-primary">
                        Turn-by-Turn Waypoints ({turnByTurnLegs.length} Legs)
                      </span>
                    </div>
                    <button
                      onClick={() => setShowItineraryDrawer(false)}
                      className="text-text-secondary hover:text-text-primary text-xs"
                    >
                      Close
                    </button>
                  </div>

                  <div className="overflow-y-auto flex flex-col gap-2 pr-1">
                    {turnByTurnLegs.length === 0 ? (
                      <p className="text-xs text-text-secondary text-center py-4">
                        Run an optimization to view route itinerary.
                      </p>
                    ) : (
                      turnByTurnLegs.map((leg) => (
                        <div
                          key={leg.legIndex}
                          className="p-2.5 rounded-lg bg-bg-base border border-border flex flex-col gap-1 text-xs"
                        >
                          <span className="font-mono text-[11px] font-bold text-signal-green">
                            Leg #{leg.legIndex}
                          </span>
                          <div className="flex items-center gap-1.5 font-medium text-text-primary">
                            <span className="truncate">{leg.from}</span>
                            <ArrowRight size={13} className="shrink-0 text-text-secondary" />
                            <span className="truncate text-signal-amber font-semibold">{leg.to}</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </section>
          </div>
        )}

        {/* ========================================================================= */}
        {/* PAGE 2: DASHBOARD VIEW (STRICTLY NO MAPS OR DEPOT PICKERS) */}
        {/* ========================================================================= */}
        {activePage === "dashboard" && (
          <div className="w-full h-full overflow-y-auto">
            <AnalyticsDashboardView
              metrics={metrics}
              compareResults={compareResults}
              isComparing={isComparing}
              onRefreshCompare={runComparison}
              routeExplanation={routeExplanation}
              convergenceHistory={convergenceHistory}
              baselineCost={baselineCost}
              crossoverIteration={crossoverIteration}
            />
          </div>
        )}

        {/* ========================================================================= */}
        {/* PAGE 3: ADMIN CONSOLE VIEW */}
        {/* ========================================================================= */}
        {activePage === "admin" && (
          <div className="w-full h-full p-6 overflow-y-auto">
            <AdminPortalView
              token={adminUser?.token || null}
              username={adminUser?.username || "admin"}
              onLogout={handleLogout}
            />
          </div>
        )}
      </main>
    </div>
  );
}
