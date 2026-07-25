"use server";

import { revalidatePath } from "next/cache";
import { apiFetch } from "@/lib/api";

export async function createApp(name: string, environment: string) {
  const res = await apiFetch("/v1/apps", {
    method: "POST",
    body: JSON.stringify({ name, environment }),
  });

  if (!res.ok) {
    const data = await res.json();
    return { error: data.message as string };
  }

  revalidatePath("/dashboard/apps");
  return { success: true };
}

export async function deleteApp(clientAppId: string) {
  const res = await apiFetch(`/v1/apps/${clientAppId}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const data = await res.json();
    return { error: data.message as string };
  }

  revalidatePath("/dashboard/apps");
  return { success: true };
}