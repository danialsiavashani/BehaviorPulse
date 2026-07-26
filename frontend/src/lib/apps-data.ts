import { apiFetch } from "@/lib/api";

export type ClientApp = {
  id: string;
  name: string;
  environment: string;
  client_id: string;
  created_at: string;
};

export async function getAppById(id: string): Promise<ClientApp | null> {
  const res = await apiFetch("/v1/apps?page_size=100");
  if (!res.ok) return null;
  const data: { items: ClientApp[] } = await res.json();
  return data.items.find((a) => a.id === id) ?? null;
}