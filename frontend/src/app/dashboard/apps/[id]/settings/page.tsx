import { notFound } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getAppById } from "@/lib/apps-data";
import { ServiceScopes } from "@/components/apps/service-scopes";
import { DangerZone } from "@/components/apps/danger-zone";

type Service = {
  service_key: string;
  name: string;
};

type Scope = {
  service_key: string;
  enabled: boolean;
};

export default async function AppSettingsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const app = await getAppById(id);
  if (!app) notFound();

  const [servicesRes, scopesRes] = await Promise.all([
    apiFetch("/v1/services?page_size=100"),
    apiFetch(`/v1/apps/${id}/scopes`),
  ]);

  const servicesData: { items: Service[] } = servicesRes.ok
    ? await servicesRes.json()
    : { items: [] };
  const scopes: Scope[] = scopesRes.ok ? await scopesRes.json() : [];

  return (
    <div>
      <h2 className="text-lg font-medium">Settings</h2>
      <p className="mt-1 text-sm text-muted-foreground">Manage settings for {app.name}.</p>

      <div className="mt-4">
        <ServiceScopes clientAppId={app.id} services={servicesData.items} initialScopes={scopes} />
      </div>

      <DangerZone appId={app.id} appName={app.name} />
    </div>
  );
}