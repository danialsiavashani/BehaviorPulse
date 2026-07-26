import { notFound } from "next/navigation";
import { getAppById } from "@/lib/apps-data";
import { DangerZone } from "@/components/apps/danger-zone";

export default async function AppSettingsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const app = await getAppById(id);
  if (!app) notFound();

  return (
    <div>
      <h2 className="text-lg font-medium">Settings</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Manage settings for {app.name}.
      </p>

      <DangerZone appId={app.id} appName={app.name} />
    </div>
  );
}