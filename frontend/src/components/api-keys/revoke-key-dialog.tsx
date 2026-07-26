"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { revokeApiKey } from "@/lib/api-keys";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type KeyToRevoke = { id: string; name: string };

export function RevokeKeyDialog({
  apiKey,
  clientAppId,
  open,
  onOpenChange,
}: {
  apiKey: KeyToRevoke | null;
  clientAppId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleConfirm() {
    if (!apiKey) return;
    setLoading(true);
    setError(null);
    const result = await revokeApiKey(apiKey.id, clientAppId);
    setLoading(false);

    if (result?.error) {
      setError(result.error);
      return;
    }

    onOpenChange(false);
    router.refresh();
  }

  if (!apiKey) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Revoke {apiKey.name}?</DialogTitle>
          <DialogDescription>
            Requests using this key will stop working immediately. This can&apos;t be undone.
          </DialogDescription>
        </DialogHeader>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button variant="destructive" onClick={handleConfirm} disabled={loading}>
            {loading ? "Revoking..." : "Revoke key"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}