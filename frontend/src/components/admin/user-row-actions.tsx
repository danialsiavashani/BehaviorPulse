"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { updateAdminUser } from "@/lib/admin";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function UserRowActions({
  userId,
  role,
  isActive,
  disabled = false,
}: {
  userId: string;
  role: string;
  isActive: boolean;
  disabled?: boolean;
}) {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState(role);
  const [selectedStatus, setSelectedStatus] = useState(isActive ? "active" : "disabled");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (disabled) {
    return <span className="text-xs text-muted-foreground">Your account</span>;
  }

  const dirty = selectedRole !== role || selectedStatus !== (isActive ? "active" : "disabled");

  async function handleSave() {
    setSaving(true);
    setError(null);

    const result = await updateAdminUser(userId, {
      role: selectedRole,
      is_active: selectedStatus === "active",
    });

    setSaving(false);

    if (result?.error) {
      setError(result.error);
      return;
    }

    router.refresh();
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <div className="flex items-center gap-2">
        <Select value={selectedRole} onValueChange={setSelectedRole}>
          <SelectTrigger size="sm" className="w-[100px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="user">User</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger size="sm" className="w-[110px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="disabled">Disabled</SelectItem>
          </SelectContent>
        </Select>

        <Button size="sm" onClick={handleSave} disabled={!dirty || saving}>
          {saving ? "Saving..." : "Save"}
        </Button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}