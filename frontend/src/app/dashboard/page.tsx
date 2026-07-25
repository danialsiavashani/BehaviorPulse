import { getCurrentUser } from "@/lib/auth";

export default async function DashboardOverviewPage() {
  const user = await getCurrentUser();

  return (
    <div>
      <h1 className="text-2xl font-semibold">Overview</h1>
      <p className="mt-2 text-muted-foreground">
        Welcome back, {user?.email}.
      </p>
    </div>
  );
}