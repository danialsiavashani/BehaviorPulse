import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { StatCard } from "@/components/usage/stat-card";
import { RequestsChart } from "@/components/usage/requests-chart";
import { formatDate } from "@/lib/utils";

type AdminStats = {
  total_users: number;
  demo_users: number;
  real_users: number;
  active_users: number;
  disabled_users: number;
  total_requests: number;
  signups_over_time: { date: string; count: number }[];
  recent_signups: { id: string; email: string; created_at: string; is_demo: boolean }[];
};

export default async function AdminOverviewPage() {
  const res = await apiFetch("/v1/admin/stats");
  const stats: AdminStats = res.ok
    ? await res.json()
    : {
        total_users: 0,
        demo_users: 0,
        real_users: 0,
        active_users: 0,
        disabled_users: 0,
        total_requests: 0,
        signups_over_time: [],
        recent_signups: [],
      };

  return (
    <div>
      <h1 className="text-2xl font-semibold">Admin Overview</h1>
      <p className="mt-1 text-sm text-muted-foreground">Platform-wide stats across all users.</p>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        <StatCard label="Users (real / demo)" value={`${stats.real_users} / ${stats.demo_users}`} />
        <StatCard
          label="Active / disabled"
          value={`${stats.active_users} / ${stats.disabled_users}`}
        />
        <StatCard label="Total requests" value={String(stats.total_requests)} />
      </div>

      <div className="mt-4">
        <RequestsChart data={stats.signups_over_time} title="Signups over the last 30 days" />
      </div>

      <div className="mt-6">
        <h2 className="text-sm font-medium">Recent signups</h2>

        {stats.recent_signups.length > 0 ? (
          <div className="mt-2 divide-y rounded-lg border">
            {stats.recent_signups.map((user) => (
              <div key={user.id} className="flex items-center justify-between gap-2 p-3 text-sm">
                <span className="truncate">{user.email}</span>
                <div className="flex shrink-0 items-center gap-2">
                  {user.is_demo && (
                    <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                      demo
                    </span>
                  )}
                  <span className="text-xs text-muted-foreground">{formatDate(user.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-2 rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
            No signups yet.
          </div>
        )}
      </div>

      <div className="mt-6">
        <Link href="/admin/users" className="text-sm text-primary hover:underline">
          Manage users →
        </Link>
      </div>
    </div>
  );
}