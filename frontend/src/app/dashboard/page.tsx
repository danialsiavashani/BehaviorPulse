import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { getCurrentUser } from "@/lib/auth";
import { Badge } from "@/components/ui/badge";
import { StatCard } from "@/components/usage/stat-card";
import { RequestsChart } from "@/components/usage/requests-chart";
import { formatDate } from "@/lib/utils";

type UsageData = {
  total_requests: number;
  by_app: { client_app_id: string; app_name: string; count: number }[];
  requests_over_time: { date: string; count: number }[];
};

type LatestAnalysis = {
  analysis_id: string;
  app_name: string;
  subject_label: string;
  total_observations: number;
  computed_confidence: number;
  summary: string;
  created_at: string;
};

type AnalysesData = {
  items: LatestAnalysis[];
  total: number;
};

export default async function DashboardOverviewPage() {
  const [user, usageRes, analysesRes] = await Promise.all([
    getCurrentUser(),
    apiFetch("/v1/usage"),
    apiFetch("/v1/analyses?page=1&page_size=1"),
  ]);

  const usage: UsageData = usageRes.ok
    ? await usageRes.json()
    : { total_requests: 0, by_app: [], requests_over_time: [] };

  const analyses: AnalysesData = analysesRes.ok
    ? await analysesRes.json()
    : { items: [], total: 0 };

  const latest = analyses.items[0];
  const topApp = usage.by_app[0]?.app_name ?? "—";

  return (
    <div>
      <h1 className="text-2xl font-semibold">Overview</h1>
      <p className="mt-1 text-sm text-muted-foreground">Welcome back, {user?.email}.</p>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        <StatCard label="Total requests" value={String(usage.total_requests)} />
        <StatCard label="Analyses run" value={String(analyses.total)} />
        <StatCard label="Most active app" value={topApp} />
      </div>

      <div className="mt-4">
        <RequestsChart data={usage.requests_over_time} />
      </div>

      <div className="mt-6">
        <h2 className="text-sm font-medium">Latest analysis</h2>

        {latest ? (
          <Link
            href={`/dashboard/analyses/${latest.analysis_id}`}
            className="mt-2 block rounded-lg border p-4 transition-colors hover:border-primary/40 hover:bg-muted/30"
          >
            <div className="flex items-center gap-2">
              <span className="font-medium">{latest.app_name}</span>
              <Badge variant="secondary">{Math.round(latest.computed_confidence * 100)}%</Badge>
              <span className="text-xs text-muted-foreground">
                {formatDate(latest.created_at)}
              </span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{latest.summary}</p>
          </Link>
        ) : (
          <div className="mt-2 rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
            No analyses yet.{" "}
            <Link href="/dashboard/services" className="text-primary hover:underline">
              Run your first one
            </Link>
            .
          </div>
        )}
      </div>
    </div>
  );
}