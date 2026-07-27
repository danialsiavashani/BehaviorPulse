import { notFound } from "next/navigation";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { CopyableId } from "@/components/apps/copyable-id";
import { StatCard } from "@/components/usage/stat-card";
import { BreakdownList } from "@/components/usage/breakdown-list";
import { RequestsChart } from "@/components/usage/requests-chart";
import { formatDate } from "@/lib/utils";

type ServiceDetail = {
  service_key: string;
  name: string;
  description: string;
  status: string;
  endpoint: string;
};

type EnabledApp = {
  id: string;
  name: string;
  environment: string;
  created_at: string;
};

type UsageData = {
  total_requests: number;
  success_count: number;
  error_count: number;
  success_rate: number;
  by_app: { client_app_id: string; app_name: string; count: number }[];
  requests_over_time: { date: string; count: number }[];
};

export default async function ServiceDetailPage({
  params,
}: {
  params: Promise<{ service_key: string }>;
}) {
  const { service_key } = await params;

  const serviceRes = await apiFetch(`/v1/services/${service_key}`);
  if (!serviceRes.ok) notFound();
  const service: ServiceDetail = await serviceRes.json();

  const [appsRes, usageRes] = await Promise.all([
    apiFetch(`/v1/services/${service_key}/apps`),
    apiFetch(`/v1/usage?service_key=${service_key}`),
  ]);
  const enabledApps: EnabledApp[] = appsRes.ok ? await appsRes.json() : [];
  const usage: UsageData = usageRes.ok
    ? await usageRes.json()
    : {
        total_requests: 0,
        success_count: 0,
        error_count: 0,
        success_rate: 0,
        by_app: [],
        requests_over_time: [],
      };

  return (
    <div className="max-w-2xl">
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Link href="/dashboard/services" className="hover:text-foreground">
          Services
        </Link>
        <ChevronRight className="h-3.5 w-3.5" />
        <span className="text-foreground">{service.name}</span>
      </div>

      <div className="mt-3 flex items-center gap-3">
        <h1 className="text-2xl font-semibold">{service.name}</h1>
        <Badge variant={service.status === "active" ? "secondary" : "outline"}>
          {service.status}
        </Badge>
      </div>

      <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
        <CopyableId value={service.endpoint} />
        <span className="font-mono">{service.service_key}</span>
      </div>

      <section className="mt-6">
        <h2 className="text-sm font-medium">Description</h2>
        <p className="mt-1.5 text-sm text-muted-foreground">{service.description}</p>
      </section>

      <section className="mt-6">
        <h2 className="text-sm font-medium">Enabled on</h2>
        {enabledApps.length === 0 ? (
          <p className="mt-1.5 text-sm text-muted-foreground">
            Not enabled on any app yet. Grant this service from an app's Settings tab.
          </p>
        ) : (
          <div className="mt-1.5 flex flex-col gap-2">
            {enabledApps.map((app) => (
              <Link
                key={app.id}
                href={`/dashboard/apps/${app.id}`}
                className="flex items-center justify-between rounded-lg border p-3 text-sm hover:border-foreground/20"
              >
                <span className="font-medium">{app.name}</span>
                <span className="text-xs text-muted-foreground">
                  {app.environment} · added {formatDate(app.created_at)}
                </span>
              </Link>
            ))}
          </div>
        )}
      </section>

      <section className="mt-6">
        <h2 className="text-sm font-medium">Usage</h2>
        <div className="mt-1.5 grid gap-3 sm:grid-cols-3">
          <StatCard label="Total requests" value={String(usage.total_requests)} />
          <StatCard label="Success rate" value={`${usage.success_rate}%`} />
          <StatCard label="Errors" value={String(usage.error_count)} />
        </div>
        <div className="mt-3">
          <RequestsChart data={usage.requests_over_time} />
        </div>
        <div className="mt-3">
          <BreakdownList
            title="By app"
            items={usage.by_app.map((a) => ({ label: a.app_name, count: a.count }))}
          />
        </div>
      </section>
    </div>
  );
}