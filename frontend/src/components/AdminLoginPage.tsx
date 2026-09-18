"use client";

import React, { useState } from "react";
import { Shield, Lock, User, AlertCircle, CheckCircle, ArrowRight, Database, MapPin, Sparkles } from "lucide-react";

interface AdminLoginPageProps {
  onLoginSuccess: (authData: { username: string; role: string; token: string }) => void;
}

export default function AdminLoginPage({ onLoginSuccess }: AdminLoginPageProps) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: "Invalid username or password" }));
        throw new Error(errData.detail || "Authentication failed");
      }

      const data = await res.json();
      localStorage.setItem("egreen_token", data.access_token);
      localStorage.setItem("egreen_user", JSON.stringify({ username: data.username, role: data.role }));
      onLoginSuccess({ username: data.username, role: data.role, token: data.access_token });
    } catch (err: any) {
      setErrorMsg(err.message || "Unable to reach the authentication service. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = () => {
    setUsername("admin");
    setPassword("admin123");
    setErrorMsg(null);
  };

  return (
    <div className="min-h-screen w-full flex flex-col justify-center items-center bg-bg-base p-6 select-none relative overflow-hidden">
      {/* Background Subtle Gradient Blobs */}
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-signal-green/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 w-96 h-96 bg-signal-amber/5 rounded-full blur-3xl pointer-events-none" />

      {/* Main Container */}
      <div className="w-full max-w-lg z-10 flex flex-col gap-6">
        {/* Brand & System Badges Header */}
        <div className="flex flex-col items-center text-center gap-3">
          <div className="w-14 h-14 rounded-2xl bg-signal-green/15 border border-signal-green/40 flex items-center justify-center text-signal-green shadow-lg shadow-signal-green/10">
            <Shield size={28} />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary">
              E-Green Quanta
            </h1>
            <p className="text-base text-text-secondary mt-1 font-medium">
              Coimbatore Regional Traffic & Route Optimization Engine
            </p>
          </div>

          {/* System Status Badges */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full border border-border bg-bg-surface text-xs font-mono text-signal-green">
              <Database size={13} />
              <span>PostgreSQL Ready</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full border border-signal-amber/30 bg-signal-amber/10 text-xs font-mono text-signal-amber font-semibold">
              <MapPin size={13} />
              <span>70+ km Regional Road Network</span>
            </div>
          </div>
        </div>

        {/* Login Card */}
        <div className="bg-bg-surface border border-border rounded-xl shadow-xl p-6 sm:p-8 flex flex-col gap-5">
          <div className="border-b border-border pb-3">
            <h2 className="text-lg font-bold text-text-primary">Admin Sign In</h2>
            <p className="text-sm text-text-secondary mt-0.5">
              Authenticate to access Live Simulation and Analytics Dashboard
            </p>
          </div>

          {errorMsg && (
            <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-signal-red/10 border border-signal-red/30 text-signal-red text-sm leading-relaxed">
              <AlertCircle size={18} className="shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-semibold text-text-primary flex items-center gap-1.5">
                <User size={15} className="text-text-secondary" />
                <span>Username</span>
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter username"
                className="w-full px-3.5 py-2.5 text-sm bg-bg-base border border-border rounded-lg text-text-primary focus:outline-none focus:border-signal-green transition-colors"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-semibold text-text-primary flex items-center gap-1.5">
                <Lock size={15} className="text-text-secondary" />
                <span>Password</span>
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter password"
                className="w-full px-3.5 py-2.5 text-sm bg-bg-base border border-border rounded-lg text-text-primary focus:outline-none focus:border-signal-green transition-colors"
              />
            </div>

            {/* Autofill Demo Credentials */}
            <button
              type="button"
              onClick={fillDemo}
              className="flex items-center justify-between px-3.5 py-2 rounded-lg bg-signal-amber/10 border border-signal-amber/30 text-signal-amber hover:bg-signal-amber/20 transition-colors text-xs font-semibold"
            >
              <span className="flex items-center gap-1.5">
                <Sparkles size={14} />
                <span>Click to Fill Demo Credentials</span>
              </span>
              <span className="font-mono text-[11px] bg-bg-base/60 px-2 py-0.5 rounded border border-signal-amber/20">
                admin / admin123
              </span>
            </button>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 rounded-lg font-bold text-sm bg-signal-green text-[#0B0F14] hover:brightness-110 active:scale-[0.99] transition-all flex items-center justify-center gap-2 shadow-md shadow-signal-green/20 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-[#0B0F14] border-t-transparent rounded-full animate-spin"></span>
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <span>Enter Mission Control</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Security Note */}
          <div className="pt-3 border-t border-border flex items-center justify-between text-xs text-text-secondary">
            <span className="flex items-center gap-1.5">
              <CheckCircle size={13} className="text-signal-green" />
              <span>JWT Bearer Security</span>
            </span>
            <span>Bcrypt Hashed Storage</span>
          </div>
        </div>
      </div>
    </div>
  );
}
