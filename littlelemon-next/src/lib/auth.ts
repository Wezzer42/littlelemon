// src/lib/auth.ts
"use client";

import { api } from "./api";

export async function login(username: string, password: string) {
  const { data } = await api.post("/auth/jwt/create/", { username, password });
  localStorage.setItem("access", data.access);
  localStorage.setItem("refresh", data.refresh);
  return data;
}

export async function register(payload: { username: string; password: string; email?: string }) {
  return api.post("/auth/users/", payload);
}

export async function logout() {
  const refresh = localStorage.getItem("refresh");
  try {
    if (refresh) await api.post("/auth/jwt/blacklist/", { refresh });
  } finally {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  }
}

export function isAuthed() {
  return typeof window !== "undefined" && !!localStorage.getItem("access");
}
