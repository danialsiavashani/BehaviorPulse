"use server";

import { cookies } from "next/headers";

const BACKEND_URL = process.env.BACKEND_URL;

type ApiError = { error: string; message: string; request_id: string | null };

export async function signup(email: string, password: string) {
  const res = await fetch(`${BACKEND_URL}/v1/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const data: ApiError = await res.json();
    return { error: data.message };
  }

  // Signup succeeded but doesn't log the user in - reuse login() so
  // they're authenticated immediately after signing up.
  return login(email, password);
}

export async function login(email: string, password: string) {
  const res = await fetch(`${BACKEND_URL}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const data: ApiError = await res.json();
    return { error: data.message };
  }

  const data = await res.json();
  const cookieStore = await cookies();

  cookieStore.set("access_token", data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
  });

  return { success: true };
}

export async function logout() {
  const cookieStore = await cookies();
  cookieStore.delete("access_token");
  // No server-side revoke call yet - BehaviorPulse has no refresh/
  // blacklist mechanism (v1 stretch, not built). Clearing the cookie
  // is enough; the JWT just expires naturally on its own.
}

export async function getCurrentUser() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) return null;

  const res = await fetch(`${BACKEND_URL}/v1/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!res.ok) return null;

  return res.json();
}