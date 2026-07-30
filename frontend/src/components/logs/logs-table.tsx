import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";

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

function StatusBadge({ log }: { log: LogEntry }) {
  return (
    <div className="flex items-center gap-2">
      <Badge
        variant={log.success ? "outline" : "destructive"}
        className={
          log.success
            ? "border-green-600/20 bg-green-50 text-green-700 dark:border-green-500/20 dark:bg-green-500/10 dark:text-green-400"
            : undefined
        }
      >
        {log.status_code}
      </Badge>
      {log.error_code && (
        <span className="text-xs text-muted-foreground">{log.error_code}</span>
      )}
    </div>
  );
}

export function LogsTable({ logs }: { logs: LogEntry[] }) {
  if (logs.length === 0) {
    return (
      <div className="rounded-lg border p-10 text-center text-sm text-muted-foreground">
        No requests logged yet.
      </div>
    );
  }

  return (
    <>
      {/* Mobile: stacked cards, no horizontal scroll */}
      <div className="space-y-2 md:hidden">
        {logs.map((log) => (
          <div key={log.id} className="rounded-lg border p-3">
            <div className="flex items-center justify-between gap-2">
              <StatusBadge log={log} />
              <span className="text-xs text-muted-foreground">{log.latency_ms}ms</span>
            </div>
            <div className="mt-2 break-all font-mono text-xs">
              <span className="text-muted-foreground">{log.method}</span> {log.endpoint}
            </div>
            <div className="mt-2 flex items-center justify-between gap-2 text-xs text-muted-foreground">
              <span className="truncate font-mono">{log.request_id}</span>
              <span className="shrink-0">{formatDate(log.created_at)}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Desktop: full table */}
      <div className="hidden overflow-hidden rounded-lg border md:block">
        <table className="w-full text-sm">
          <thead className="border-b bg-muted/40 text-left text-xs text-muted-foreground">
            <tr>
              <th className="px-4 py-2 font-medium">Status</th>
              <th className="px-4 py-2 font-medium">Endpoint</th>
              <th className="px-4 py-2 font-medium">Latency</th>
              <th className="px-4 py-2 font-medium">Request ID</th>
              <th className="px-4 py-2 font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b last:border-0">
                <td className="px-4 py-2.5">
                  <StatusBadge log={log} />
                </td>
                <td className="px-4 py-2.5">
                  <span className="font-mono text-xs text-muted-foreground">{log.method}</span>{" "}
                  <span className="font-mono text-xs">{log.endpoint}</span>
                </td>
                <td className="px-4 py-2.5 text-muted-foreground">{log.latency_ms}ms</td>
                <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground">
                  {log.request_id}
                </td>
                <td className="px-4 py-2.5 text-muted-foreground">{formatDate(log.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}