import { redirect } from "next/navigation";
import { getCurrentAdmin } from "@/lib/auth";
import { AdminSidebar } from "@/components/admin/admin-sidebar";

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const admin = await getCurrentAdmin();
  if (!admin) redirect("/dashboard");

  return (
    <div className="flex h-svh flex-col overflow-hidden lg:flex-row">
      <AdminSidebar adminEmail={admin.email} />
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}