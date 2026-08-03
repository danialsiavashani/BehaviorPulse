"use server";

import { revalidatePath } from "next/cache";
import { apiFetch } from "@/lib/api";

export async function updateAdminUser(
  userId: string,
  updates: { role?: string; is_active?: boolean }
) {
  const res = await apiFetch(`/v1/admin/users/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });

  if (!res.ok) {
    const data = await res.json();
    return { error: data.message as string };
  }

  revalidatePath("/admin/users");
  revalidatePath("/admin");
  return { success: true };
}