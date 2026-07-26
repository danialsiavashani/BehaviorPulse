import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";

type ClientApp = {
  id: string;
  name: string;
  environment: string;
  client_id: string;
  created_at: string;
};

export function AppsGrid({ apps }: { apps: ClientApp[] }) {
  if (apps.length === 0) {
    return (
      <div className="rounded-lg border p-10 text-center text-sm text-muted-foreground">
        No apps yet. Create one to get started.
      </div>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {apps.map((app) => (
        <Link
          key={app.id}
          href={`/dashboard/apps/${app.id}`}
          className="group relative block rounded-lg border p-4 transition-colors hover:border-primary/40 hover:bg-muted/30"
        >
          <div className="min-w-0">
            <p className="truncate font-medium">{app.name}</p>
            <p className="mt-0.5 truncate font-mono text-xs text-muted-foreground">
              {app.client_id}
            </p>
          </div>

          <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
            <Badge variant="secondary">{app.environment}</Badge>
            <span>{formatDate(app.created_at)}</span>
          </div>

          <ChevronRight className="pointer-events-none absolute bottom-4 right-4 h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
        </Link>
      ))}
    </div>
  );
}