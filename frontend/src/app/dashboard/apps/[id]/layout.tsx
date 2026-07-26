import Link from "next/link";
import { notFound } from "next/navigation";
import { ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { CopyableId } from "@/components/apps/copyable-id";
import { AppTabs } from "@/components/apps/app-tabs";
import { getAppById } from "@/lib/apps-data";
import { formatDate } from "@/lib/utils";

export default async function AppLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const app = await getAppById(id);
  if (!app) notFound();

  return (
    <div>
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Link href="/dashboard/apps" className="hover:text-foreground">
          Apps
        </Link>
        <ChevronRight className="h-3.5 w-3.5" />
        <span className="text-foreground">{app.name}</span>
      </div>

      <div className="mt-3 flex items-center gap-3">
        <h1 className="text-2xl font-semibold">{app.name}</h1>
        <Badge variant="secondary">{app.environment}</Badge>
      </div>

      <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
        <CopyableId value={app.client_id} />
        <span>Created {formatDate(app.created_at)}</span>
      </div>

      <AppTabs appId={app.id} />

      <div className="mt-4">{children}</div>
    </div>
  );
}