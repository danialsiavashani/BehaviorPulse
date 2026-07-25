"use client";

import { useState } from "react";
import { MoreHorizontal } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DeleteAppDialog } from "@/components/apps/delete-app-dialog";

type ClientApp = {
  id: string;
  name: string;
  environment: string;
  client_id: string;
  created_at: string;
};

export function AppsTable({ apps }: { apps: ClientApp[] }) {
  const [deleteTarget, setDeleteTarget] = useState<ClientApp | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  function handleDeleteClick(app: ClientApp) {
    setDeleteTarget(app);
    setDialogOpen(true);
  }

  return (
    <>
      <div className="overflow-hidden rounded-lg border">
        {apps.length === 0 ? (
          <div className="p-10 text-center text-sm text-muted-foreground">
            No apps yet. Create one to get started.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b bg-muted/40 text-left text-xs text-muted-foreground">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Client ID</th>
                <th className="px-4 py-2 font-medium">Environment</th>
                <th className="px-4 py-2 font-medium">Created</th>
                <th className="px-4 py-2 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {apps.map((app) => (
                <tr key={app.id} className="border-b last:border-0">
                  <td className="px-4 py-3 font-medium">{app.name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                    {app.client_id}
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant="secondary">{app.environment}</Badge>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {new Date(app.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon-sm">
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
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <DeleteAppDialog
        app={deleteTarget}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </>
  );
}