import { getCurrentUser } from "@/lib/auth";
import { EditNameForm } from "@/components/account/edit-name-form";
import { formatDate } from "@/lib/utils";

export default async function AccountProfilePage() {
  const user = await getCurrentUser();
  const initial = (user?.name?.[0] ?? user?.email?.[0])?.toUpperCase() ?? "?";

  return (
    <div className="max-w-md rounded-lg border p-5">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-lg font-medium text-primary">
          {initial}
        </div>
        <div className="min-w-0">
          <p className="truncate text-base font-medium">{user?.name ?? user?.email}</p>
          {user?.name && (
            <p className="truncate text-xs text-muted-foreground">{user.email}</p>
          )}
          <p className="text-xs text-muted-foreground">
            Member since {user?.created_at ? formatDate(user.created_at) : "—"}
          </p>
        </div>
      </div>

      <div className="mt-4 border-t pt-4">
        <EditNameForm currentName={user?.name ?? null} />
      </div>
    </div>
  );
}