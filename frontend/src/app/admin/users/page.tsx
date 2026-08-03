import { apiFetch } from "@/lib/api";
import { getCurrentAdmin } from "@/lib/auth";
import { UsersFilterBar } from "@/components/admin/users-filter-bar";
import { UsersTable } from "@/components/admin/users-table";
import { PaginationControls } from "@/components/shared/pagination-controls";

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

type AdminUsersPageData = {
  items: AdminUser[];
  total: number;
  page: number;
  page_size: number;
};

export default async function AdminUsersPage({
  searchParams,
}: {
  searchParams: Promise<{
    page?: string;
    search?: string;
    is_active?: string;
    is_demo?: string;
  }>;
}) {
  const { page: pageParam, search, is_active, is_demo } = await searchParams;
  const page = pageParam ? parseInt(pageParam, 10) : 1;

  const admin = await getCurrentAdmin();

  const params = new URLSearchParams();
  params.set("page", String(page));
  if (search) params.set("search", search);
  if (is_active) params.set("is_active", is_active);
  if (is_demo) params.set("is_demo", is_demo);

  const res = await apiFetch(`/v1/admin/users?${params.toString()}`);
  const data: AdminUsersPageData = res.ok
    ? await res.json()
    : { items: [], total: 0, page: 1, page_size: 8 };

  return (
    <div>
      <h1 className="text-2xl font-semibold">Users</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Manage roles and account status across the platform.
      </p>

      <div className="mt-6">
        <UsersFilterBar />
      </div>

      <div className="mt-4">
        <UsersTable users={data.items} currentAdminId={admin?.id ?? ""} />
      </div>

      <div className="mt-2">
        <PaginationControls page={data.page} pageSize={data.page_size} total={data.total} />
      </div>
    </div>
  );
}