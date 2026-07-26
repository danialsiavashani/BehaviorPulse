import { getCurrentUser } from "@/lib/auth";
import { formatDate } from "@/lib/utils";

export default async function AccountProfilePage() {
  const user = await getCurrentUser();

  return (
    <div className="max-w-md rounded-lg border p-4">
      <div>
        <p className="text-xs text-muted-foreground">Email</p>
        <p className="mt-0.5 text-sm font-medium">{user?.email}</p>
      </div>
      <div className="mt-4">
        <p className="text-xs text-muted-foreground">Member since</p>
        <p className="mt-0.5 text-sm font-medium">
          {user?.created_at ? formatDate(user.created_at) : "—"}
        </p>
      </div>
    </div>
  );
}