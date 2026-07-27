import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL;

// How much of a safety margin to refresh ahead of actual expiry, so a
// request that lands a moment after middleware runs doesn't just miss it.
const REFRESH_MARGIN_SECONDS = 120;

function base64UrlDecode(segment: string): string {
  let base64 = segment.replace(/-/g, "+").replace(/_/g, "/");
  while (base64.length % 4 !== 0) {
    base64 += "=";
  }
  return atob(base64);
}

function getExpiryFromJwt(token: string): number | null {
  try {
    const payloadSegment = token.split(".")[1];
    const json = base64UrlDecode(payloadSegment);
    const payload = JSON.parse(json);
    return typeof payload.exp === "number" ? payload.exp : null;
  } catch {
    return null;
  }
}

function isExpiredOrNearExpiry(accessToken: string): boolean {
  const exp = getExpiryFromJwt(accessToken);
  if (exp === null) return true;
  const nowSeconds = Date.now() / 1000;
  return exp - nowSeconds < REFRESH_MARGIN_SECONDS;
}

export async function middleware(request: NextRequest) {
  const accessToken = request.cookies.get("access_token")?.value;
  const refreshToken = request.cookies.get("refresh_token")?.value;

  if (!refreshToken) {
    return NextResponse.next();
  }

  if (accessToken && !isExpiredOrNearExpiry(accessToken)) {
    return NextResponse.next();
  }

  const refreshRes = await fetch(`${BACKEND_URL}/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  }).catch(() => null);

  if (!refreshRes || !refreshRes.ok) {
    return NextResponse.next();
  }

  const data: { access_token: string; refresh_token: string } = await refreshRes.json();
  const response = NextResponse.next();

  response.cookies.set("access_token", data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
  });
  response.cookies.set("refresh_token", data.refresh_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
  });

  return response;
}

export const config = {
  matcher: ["/dashboard/:path*"],
};