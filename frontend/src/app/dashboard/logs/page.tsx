import { apiFetch } from "@/lib/api";
import { LogsTable } from "@/components/logs/logs-table";
import { PaginationControls } from "@/components/shared/pagination-controls";

type LogEntry = {
  id: string;
  client_app_id: string | null;
  service_key: string | null;
  endpoint: string;
  method: string;
  status_code: number;
  success: boolean;
  error_code: string | null;
  latency_ms: number;
  request_id: string;
  created_at: string;
};

type LogsPageData = {
  items: LogEntry[];
  total: number;
  page: number;
  page_size: number;
};

export default async function LogsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page: pageParam } = await searchParams;
  const page = pageParam ? parseInt(pageParam, 10) : 1;

  const res = await apiFetch(`/v1/logs?page=${page}`);
  const data: LogsPageData = res.ok
    ? await res.json()
    : { items: [], total: 0, page: 1, page_size: 8 };

  return (
    <div>
      <h1 className="text-2xl font-semibold">Logs</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        API requests across all your apps.
      </p>

      <div className="mt-6">
        <LogsTable logs={data.items} />
      </div>

      <PaginationControls page={data.page} pageSize={data.page_size} total={data.total} />
    </div>
  );
}