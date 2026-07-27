"use server";

import { cookies } from "next/headers";

const BACKEND_URL = process.env.BACKEND_URL;

type ApiError = { error: string; message: string; request_id: string | null };

async function setTokenCookies(accessToken: string, refreshToken: string) {
  const cookieStore = await cookies();

  cookieStore.set("access_token", accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
  });

  cookieStore.set("refresh_token", refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
  });
}

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
  await setTokenCookies(data.access_token, data.refresh_token);

  return { success: true };
}

export async function logout() {
  const cookieStore = await cookies();
  const refreshToken = cookieStore.get("refresh_token")?.value;

  if (refreshToken) {
    await fetch(`${BACKEND_URL}/v1/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    }).catch(() => {
      // Best-effort revoke - clearing the cookies below still logs the
      // browser out even if this call fails.
    });
  }

  cookieStore.delete("access_token");
  cookieStore.delete("refresh_token");
}

export async function updateName(name: string) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) return { error: "Not authenticated" };

  const res = await fetch(`${BACKEND_URL}/v1/auth/me`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ name }),
  });

  if (!res.ok) {
    const data: ApiError = await res.json();
    return { error: data.message };
  }

  return { success: true };
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