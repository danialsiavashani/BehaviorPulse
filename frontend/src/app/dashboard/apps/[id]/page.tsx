import { apiFetch } from "@/lib/api";
import { CreateApiKeyDialog } from "@/components/api-keys/create-api-key-dialog";
import { ApiKeysList } from "@/components/api-keys/api-keys-list";
import { PaginationControls } from "@/components/shared/pagination-controls";

type ApiKeysPage = {
  items: {
    id: string;
    name: string;
    key_prefix: string;
    is_active: boolean;
    created_at: string;
    revoked_at: string | null;
    last_used_at: string | null;
  }[];
  total: number;
  page: number;
  page_size: number;
};

export default async function AppApiKeysPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { id } = await params;
  const { page: pageParam } = await searchParams;
  const page = pageParam ? parseInt(pageParam, 10) : 1;

  const keysRes = await apiFetch(`/v1/api-keys?client_app_id=${id}&page=${page}&page_size=8`);
  const keysData: ApiKeysPage = keysRes.ok
    ? await keysRes.json()
    : { items: [], total: 0, page: 1, page_size: 8 };

  return (
    <div>
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">API keys</h2>
        <CreateApiKeyDialog clientAppId={id} />
      </div>

      <div className="mt-4">
        <ApiKeysList apiKeys={keysData.items} clientAppId={id} />
      </div>

      <PaginationControls
        page={keysData.page}
        pageSize={keysData.page_size}
        total={keysData.total}
      />
    </div>
  );
}