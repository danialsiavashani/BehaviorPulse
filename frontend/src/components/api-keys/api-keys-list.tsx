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
import { RevokeKeyDialog } from "@/components/api-keys/revoke-key-dialog";
import { formatDate } from "@/lib/utils";

type ApiKey = {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  created_at: string;
  revoked_at: string | null;
  last_used_at: string | null;
};

export function ApiKeysList({
  apiKeys,
  clientAppId,
}: {
  apiKeys: ApiKey[];
  clientAppId: string;
}) {
  const [revokeTarget, setRevokeTarget] = useState<ApiKey | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  function handleRevokeClick(key: ApiKey) {
    setRevokeTarget(key);
    setDialogOpen(true);
  }

  if (apiKeys.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center text-sm text-muted-foreground">
        No API keys yet. Create one to start making requests.
      </div>
    );
  }

  return (
    <>
      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="border-b bg-muted/40 text-left text-xs text-muted-foreground">
            <tr>
              <th className="px-4 py-2 font-medium">Name</th>
              <th className="px-4 py-2 font-medium">Key</th>
              <th className="px-4 py-2 font-medium">Status</th>
              <th className="px-4 py-2 font-medium">Last used</th>
              <th className="px-4 py-2 font-medium">Created</th>
              <th className="px-4 py-2 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {apiKeys.map((key) => (
              <tr key={key.id} className="border-b last:border-0">
                <td className="px-4 py-2.5 font-medium">{key.name}</td>
                <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground">
                  {key.key_prefix}••••••••
                </td>
                <td className="px-4 py-2.5">
                  {key.is_active ? (
                    <Badge variant="secondary">Active</Badge>
                  ) : (
                    <Badge variant="outline" className="text-muted-foreground">
                      Revoked
                    </Badge>
                  )}
                </td>
                <td className="px-4 py-2.5 text-muted-foreground">
                  {key.last_used_at ? formatDate(key.last_used_at) : "Never"}
                </td>
                <td className="px-4 py-2.5 text-muted-foreground">
                  {formatDate(key.created_at)}
                </td>
                <td className="px-4 py-2.5 text-right">
                  {key.is_active && (
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
                            handleRevokeClick(key);
                          }}
                        >
                          Revoke key
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <RevokeKeyDialog
        apiKey={revokeTarget}
        clientAppId={clientAppId}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </>
  );
}