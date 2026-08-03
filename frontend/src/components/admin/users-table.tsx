import { formatDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { UserRowActions } from "@/components/admin/user-row-actions";

type AdminUser = {
  id: string;
  email: string;
  name: string | null;
  role: string;
  is_active: boolean;
  is_demo: boolean;
  created_at: string;
  app_count: number;
  request_count: number;
  last_active_at: string | null;
};

function RoleBadge({ role }: { role: string }) {
  return <Badge variant={role === "admin" ? "default" : "secondary"}>{role}</Badge>;
}

function StatusBadge({ isActive }: { isActive: boolean }) {
  return (
    <Badge
      variant={isActive ? "outline" : "destructive"}
      className={
        isActive
          ? "border-green-600/20 bg-green-50 text-green-700 dark:border-green-500/20 dark:bg-green-500/10 dark:text-green-400"
          : undefined
      }
    >
      {isActive ? "Active" : "Disabled"}
    </Badge>
  );
}

export function UsersTable({
  users,
  currentAdminId,
}: {
  users: AdminUser[];
  currentAdminId: string;
}) {
  if (users.length === 0) {
    return (
      <div className="rounded-lg border p-10 text-center text-sm text-muted-foreground">
        No users found.
      </div>
    );
  }

  return (
    <>
      {/* Mobile: stacked cards */}
      <div className="space-y-2 md:hidden">
        {users.map((user) => (
          <div key={user.id} className="rounded-lg border p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="truncate text-sm font-medium">{user.email}</span>
              {user.is_demo && (
                <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                  demo
                </span>
              )}
            </div>
            <div className="mt-2 flex items-center gap-2">
              <RoleBadge role={user.role} />
              <StatusBadge isActive={user.is_active} />
            </div>
            <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
              <span>
                {user.app_count} apps · {user.request_count} requests
              </span>
              <span>{formatDate(user.created_at)}</span>
            </div>
            <div className="mt-3">
              <UserRowActions
                userId={user.id}
                role={user.role}
                isActive={user.is_active}
                disabled={user.id === currentAdminId}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Desktop: full table */}
      <div className="hidden overflow-hidden rounded-lg border md:block">
        <table className="w-full text-sm">
          <thead className="border-b bg-muted/40 text-left text-xs text-muted-foreground">
            <tr>
              <th className="px-4 py-2 font-medium">Email</th>
              <th className="px-4 py-2 font-medium">Role</th>
              <th className="px-4 py-2 font-medium">Status</th>
              <th className="px-4 py-2 font-medium">Created</th>
              <th className="px-4 py-2 font-medium">Apps</th>
              <th className="px-4 py-2 font-medium">Requests</th>
              <th className="px-4 py-2 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b last:border-0">
                <td className="px-4 py-2.5">
                  <div className="flex items-center gap-2">
                    <span className="truncate">{user.email}</span>
                    {user.is_demo && (
                      <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                        demo
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-2.5">
                  <RoleBadge role={user.role} />
                </td>
                <td className="px-4 py-2.5">
                  <StatusBadge isActive={user.is_active} />
                </td>
                <td className="px-4 py-2.5 text-muted-foreground">{formatDate(user.created_at)}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{user.app_count}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{user.request_count}</td>
                <td className="px-4 py-2.5">
                  <UserRowActions
                    userId={user.id}
                    role={user.role}
                    isActive={user.is_active}
                    disabled={user.id === currentAdminId}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}