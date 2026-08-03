import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { Sidebar } from "@/components/dashboard/sidebar";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  return (
    <div className="flex h-svh flex-col overflow-hidden lg:flex-row">
      <Sidebar userEmail={user.email} isAdmin={user.role === "admin"} />
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}