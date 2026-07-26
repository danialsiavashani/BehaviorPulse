"use server";

import { revalidatePath } from "next/cache";
import { apiFetch } from "@/lib/api";

export async function createApiKey(clientAppId: string, name: string) {
  const res = await apiFetch("/v1/api-keys", {
    method: "POST",
    body: JSON.stringify({ client_app_id: clientAppId, name }),
  });

  const data = await res.json();

  if (!res.ok) {
    return { error: data.message as string };
  }

  revalidatePath(`/dashboard/apps/${clientAppId}`);
  return { data };
}

export async function revokeApiKey(apiKeyId: string, clientAppId: string) {
  const res = await apiFetch(`/v1/api-keys/${apiKeyId}/revoke`, {
    method: "POST",
  });

  if (!res.ok) {
    const data = await res.json();
    return { error: data.message as string };
  }

  revalidatePath(`/dashboard/apps/${clientAppId}`);
  return { success: true };
}