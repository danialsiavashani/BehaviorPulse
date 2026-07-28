import { getCurrentUser } from "@/lib/auth";
import { AccountDangerZone } from "@/components/account/danger-zone";

export default async function AccountDangerZonePage() {
  const user = await getCurrentUser();

  return (
    <div className="max-w-md">
      <AccountDangerZone email={user?.email ?? ""} />
    </div>
  );
}