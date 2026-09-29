/**
 * api.ts — Centralized API configuration for E-Green Quanta.
 * 
 * - In production behind an Nginx reverse proxy (such as AWS Lightsail),
 *   API_BASE_URL defaults to "" so requests are made relatively (e.g. `/api/auth/login`).
 * - In local development without a reverse proxy, it defaults to "http://127.0.0.1:8000".
 * - Can also be overridden at build time via NEXT_PUBLIC_API_URL environment variable.
 */

export const API_BASE_URL: string =
  process.env.NEXT_PUBLIC_API_URL !== undefined
    ? process.env.NEXT_PUBLIC_API_URL
    : process.env.NODE_ENV === "production"
    ? ""
    : "http://127.0.0.1:8000";
