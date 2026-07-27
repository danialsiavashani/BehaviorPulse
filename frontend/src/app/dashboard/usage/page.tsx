import { apiFetch } from "@/lib/api";
import { StatCard } from "@/components/usage/stat-card";
import { BreakdownList } from "@/components/usage/breakdown-list";
import { RequestsChart } from "@/components/usage/requests-chart";

type UsageData = {
  total_requests: number;
  success_count: number;
  error_count: number;
  success_rate: number;
  by_service: { service_key: string; count: number }[];
  by_app: { client_app_id: string; app_name: string; count: number }[];
  requests_over_time: { date: string; count: number }[];
};

export default async function UsagePage() {
  const res = await apiFetch("/v1/usage");
  const data: UsageData = res.ok
    ? await res.json()
    : {
        total_requests: 0,
        success_count: 0,
        error_count: 0,
        success_rate: 0,
        by_service: [],
        by_app: [],
        requests_over_time: [],
      };

  return (
    <div>
      <h1 className="text-2xl font-semibold">Usage</h1>
      <p className="mt-1 text-sm text-muted-foreground">API activity across all your apps.</p>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        <StatCard label="Total requests" value={String(data.total_requests)} />
        <StatCard label="Success rate" value={`${data.success_rate}%`} />
        <StatCard label="Errors" value={String(data.error_count)} />
      </div>

      <div className="mt-4">
        <RequestsChart data={data.requests_over_time} />
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <BreakdownList
          title="By service"
          items={data.by_service.map((s) => ({ label: s.service_key, count: s.count }))}
        />
        <BreakdownList
          title="By app"
          items={data.by_app.map((a) => ({ label: a.app_name, count: a.count }))}
        />
      </div>
    </div>
  );
}