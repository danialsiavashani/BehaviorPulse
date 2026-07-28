"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { DeleteAccountDialog } from "@/components/account/delete-account-dialog";

export function AccountDangerZone({ email }: { email: string }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4">
      <h2 className="text-sm font-medium text-destructive">Danger zone</h2>

      <div className="mt-3 flex items-center justify-between gap-4">
        <p className="text-sm text-muted-foreground">
          Permanently delete your account, every app you&apos;ve created, and all analysis history.
        </p>
        <Button variant="destructive" onClick={() => setOpen(true)} className="shrink-0">
          Delete account
        </Button>
      </div>

      <DeleteAccountDialog email={email} open={open} onOpenChange={setOpen} />
    </div>
  );
}