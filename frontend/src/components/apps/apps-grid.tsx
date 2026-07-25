"use client";

import { useState } from "react";
import Link from "next/link";
import { MoreHorizontal, ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DeleteAppDialog } from "@/components/apps/delete-app-dialog";
import { formatDate } from "@/lib/utils";

type ClientApp = {
  id: string;
  name: string;
  environment: string;
  client_id: string;
  created_at: string;
};

export function AppsGrid({ apps }: { apps: ClientApp[] }) {
  const [deleteTarget, setDeleteTarget] = useState<ClientApp | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  function handleDeleteClick(app: ClientApp) {
    setDeleteTarget(app);
    setDialogOpen(true);
  }

  if (apps.length === 0) {
    return (
      <div className="rounded-lg border p-10 text-center text-sm text-muted-foreground">
        No apps yet. Create one to get started.
      </div>
    );
  }

  return (
    <>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {apps.map((app) => (
          <div
            key={app.id}
            className="group relative cursor-pointer rounded-lg border p-4 transition-colors hover:border-primary/40 hover:bg-muted/30"
          >
            <Link
              href={`/dashboard/apps/${app.id}`}
              className="absolute inset-0"
              aria-label={`View ${app.name}`}
            />

            {/* Everything below is decorative for hit-testing purposes —
                pointer-events-none lets clicks fall through to the Link
                above, except where explicitly re-enabled. */}
            <div className="pointer-events-none">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="truncate font-medium">{app.name}</p>
                  <p className="mt-0.5 truncate font-mono text-xs text-muted-foreground">
                    {app.client_id}
                  </p>
                </div>

                <div className="pointer-events-auto">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon-sm" className="shrink-0">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        variant="destructive"
                        onSelect={(e) => {
                          e.preventDefault();
                          handleDeleteClick(app);
                        }}
                      >
                        Delete app
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
                <Badge variant="secondary">{app.environment}</Badge>
                <span>{formatDate(app.created_at)}</span>
              </div>

              <ChevronRight className="absolute bottom-4 right-4 h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
          </div>
        ))}
      </div>

      <DeleteAppDialog
        app={deleteTarget}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </>
  );
}