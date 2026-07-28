"use server";

import { cookies } from "next/headers";

const BACKEND_URL = process.env.BACKEND_URL;

type ApiError = { error: string; message: string; request_id: string | null };
type ActionResult = { error?: string; success?: true };

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

async function safeFetch(url: string, init: RequestInit): Promise<Response | null> {
  try {
    return await fetch(url, init);
  } catch {
    return null;
  }
}

export async function signup(email: string, password: string): Promise<ActionResult> {
  const res = await safeFetch(`${BACKEND_URL}/v1/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res) return { error: "Could not reach the server. Please try again." };

  if (!res.ok) {
    const data: ApiError = await res.json();
    return { error: data.message };
  }

  return login(email, password);
}

export async function login(email: string, password: string): Promise<ActionResult> {
  const res = await safeFetch(`${BACKEND_URL}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res) return { error: "Could not reach the server. Please try again." };

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
    await safeFetch(`${BACKEND_URL}/v1/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  cookieStore.delete("access_token");
  cookieStore.delete("refresh_token");
}

export async function updateName(name: string): Promise<ActionResult> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) return { error: "Not authenticated" };

  const res = await safeFetch(`${BACKEND_URL}/v1/auth/me`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ name }),
  });

  if (!res) return { error: "Could not reach the server. Please try again." };

  if (!res.ok) {
    const data: ApiError = await res.json();
    return { error: data.message };
  }

  return { success: true };
}

export async function changePassword(
  currentPassword: string,
  newPassword: string
): Promise<ActionResult> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) return { error: "Not authenticated" };

  const res = await safeFetch(`${BACKEND_URL}/v1/auth/change-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });

  if (!res) return { error: "Could not reach the server. Please try again." };

  if (!res.ok) {
    const data: ApiError = await res.json();
    return { error: data.message };
  }

  const data = await res.json();
  await setTokenCookies(data.access_token, data.refresh_token);

  return { success: true };
}

export async function changeEmail(
  currentPassword: string,
  newEmail: string
): Promise<ActionResult> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) return { error: "Not authenticated" };

  const res = await safeFetch(`${BACKEND_URL}/v1/auth/change-email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ current_password: currentPassword, new_email: newEmail }),
  });

  if (!res) return { error: "Could not reach the server. Please try again." };

  if (!res.ok) {
    const data: ApiError = await res.json();
    return { error: data.message };
  }

  const data = await res.json();
  await setTokenCookies(data.access_token, data.refresh_token);

  return { success: true };
}

export async function deleteAccount(): Promise<ActionResult> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) return { error: "Not authenticated" };

  const res = await safeFetch(`${BACKEND_URL}/v1/auth/me`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!res) return { error: "Could not reach the server. Please try again." };

  if (!res.ok) {
    const data: ApiError = await res.json();
    return { error: data.message };
  }

  cookieStore.delete("access_token");
  cookieStore.delete("refresh_token");

  return { success: true };
}

export async function getCurrentUser() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) return null;

  const res = await safeFetch(`${BACKEND_URL}/v1/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!res || !res.ok) return null;

  return res.json();
}