"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { DeleteAppDialog } from "@/components/apps/delete-app-dialog";

export function DangerZone({ appId, appName }: { appId: string; appName: string }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-12 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
      <h2 className="text-sm font-medium text-destructive">Danger zone</h2>

      <div className="mt-3 flex items-center justify-between gap-4">
        <p className="text-sm text-muted-foreground">
          Permanently delete this app, its API keys, service scopes, and analysis history.
        </p>
        <Button variant="destructive" onClick={() => setOpen(true)} className="shrink-0">
          Delete app
        </Button>
      </div>

      <DeleteAppDialog
        app={{ id: appId, name: appName }}
        open={open}
        onOpenChange={setOpen}
        redirectTo="/dashboard/apps"
      />
    </div>
  );
}