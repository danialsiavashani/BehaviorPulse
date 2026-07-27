import { apiFetch } from "@/lib/api";
import { AnalysesTable } from "@/components/analyses/analyses-table";
import { PaginationControls } from "@/components/shared/pagination-controls";

type AnalysisListItem = {
  analysis_id: string;
  app_name: string;
  subject_label: string;
  total_observations: number;
  computed_confidence: number;
  created_at: string;
};

type AnalysesPageData = {
  items: AnalysisListItem[];
  total: number;
  page: number;
  page_size: number;
};

export default async function AnalysesPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page: pageParam } = await searchParams;
  const page = pageParam ? parseInt(pageParam, 10) : 1;

  const res = await apiFetch(`/v1/analyses?page=${page}`);
  const data: AnalysesPageData = res.ok
    ? await res.json()
    : { items: [], total: 0, page: 1, page_size: 8 };

  return (
    <div>
      <h1 className="text-2xl font-semibold">Analyses</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Past observation analysis results across all your apps.
      </p>

      <div className="mt-6">
        <AnalysesTable analyses={data.items} />
      </div>

      <PaginationControls page={data.page} pageSize={data.page_size} total={data.total} />
    </div>
  );
}