import { apiFetch } from "@/lib/api";
import { CreateAppDialog } from "@/components/apps/create-app-dialog";
import { AppsGrid } from "@/components/apps/apps-grid";
import { PaginationControls } from "@/components/shared/pagination-controls";

type ClientApp = {
  id: string;
  name: string;
  environment: string;
  client_id: string;
  created_at: string;
};

type AppsPageData = {
  items: ClientApp[];
  total: number;
  page: number;
  page_size: number;
};

export default async function AppsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page: pageParam } = await searchParams;
  const page = pageParam ? parseInt(pageParam, 10) : 1;

  const res = await apiFetch(`/v1/apps?page=${page}&page_size=9`);
  const data: AppsPageData = res.ok
    ? await res.json()
    : { items: [], total: 0, page: 1, page_size: 9 };

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Apps</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Client apps that can call the BehaviorPulse API.
          </p>
        </div>
        <CreateAppDialog />
      </div>

      <div className="mt-6">
        <AppsGrid apps={data.items} />
      </div>

      <PaginationControls page={data.page} pageSize={data.page_size} total={data.total} />
    </div>
  );
}