"use client";

import React, { useState } from "react";
import { Lock, Shield, User, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface AdminLoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (authData: { username: string; role: string; token: string }) => void;
}

export default function AdminLoginModal({
  isOpen,
  onClose,
  onLoginSuccess,
}: AdminLoginModalProps) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

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
        const errData = await res.json().catch(() => ({ detail: "Invalid credentials" }));
        throw new Error(errData.detail || "Authentication failed");
      }

      const data = await res.json();
      localStorage.setItem("egreen_token", data.access_token);
      localStorage.setItem("egreen_user", JSON.stringify({ username: data.username, role: data.role }));
      onLoginSuccess({ username: data.username, role: data.role, token: data.access_token });
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to connect to backend service");
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
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-md bg-bg-surface border border-border rounded-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border bg-bg-base">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-signal-amber/20 border border-signal-amber flex items-center justify-center text-signal-amber">
              <Shield size={16} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-text-primary">Admin Authentication</h3>
              <p className="text-[11px] text-text-secondary">PostgreSQL & Fleet Audit Console</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-text-primary p-1 rounded transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleLogin} className="p-5 flex flex-col gap-4">
          {errorMsg && (
            <div className="flex items-center gap-2 p-3 rounded bg-signal-red/15 border border-signal-red/30 text-signal-red text-xs">
              <AlertCircle size={14} className="shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-text-primary flex items-center gap-1.5">
              <User size={13} className="text-text-secondary" />
              <span>Username</span>
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-3 py-2 text-xs bg-bg-base border border-border rounded text-text-primary focus:outline-none focus:border-signal-green transition-colors"
              placeholder="admin"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-text-primary flex items-center gap-1.5">
              <Lock size={13} className="text-text-secondary" />
              <span>Password</span>
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 text-xs bg-bg-base border border-border rounded text-text-primary focus:outline-none focus:border-signal-green transition-colors font-mono"
              placeholder="••••••••"
            />
          </div>

          {/* Demo Autofill Helper */}
          <div className="flex items-center justify-between text-[11px] bg-bg-base p-2.5 rounded border border-border">
            <span className="text-text-secondary">Default Credentials:</span>
            <button
              type="button"
              onClick={fillDemo}
              className="text-signal-green hover:underline font-medium font-mono"
            >
              admin / admin123 (Auto-fill)
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs rounded border border-border text-text-secondary hover:text-text-primary hover:bg-bg-base transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-xs rounded font-semibold bg-signal-green text-bg-base hover:bg-signal-green/90 transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 size={13} className="animate-spin" />
                  <span>Verifying...</span>
                </>
              ) : (
                <>
                  <CheckCircle size={13} />
                  <span>Log In as Admin</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
