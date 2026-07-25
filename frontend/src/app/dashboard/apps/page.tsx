import { apiFetch } from "@/lib/api";
import { CreateAppDialog } from "@/components/apps/create-app-dialog";
import { AppsGrid } from "@/components/apps/apps-grid";

type ClientApp = {
  id: string;
  name: string;
  environment: string;
  client_id: string;
  created_at: string;
};

export default async function AppsPage() {
  const res = await apiFetch("/v1/apps");
  const apps: ClientApp[] = res.ok ? await res.json() : [];

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Apps</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Client apps that can call the BehaviorPulse API.
          </p>
        </div>
        <CreateAppDialog />
      </div>

      <div className="mt-6">
        <AppsGrid apps={apps} />
      </div>
    </div>
  );
}