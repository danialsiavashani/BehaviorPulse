import { apiFetch } from "@/lib/api";
import { ServicesList } from "@/components/services/services-list";
import { ServiceDemo } from "@/components/services/service-demo";
import { PaginationControls } from "@/components/shared/pagination-controls";

type Service = {
  id: string;
  service_key: string;
  name: string;
  description: string;
  status: string;
  endpoint: string;
  created_at: string;
};

type ServicesPageData = {
  items: Service[];
  total: number;
  page: number;
  page_size: number;
};

export default async function ServicesPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page: pageParam } = await searchParams;
  const page = pageParam ? parseInt(pageParam, 10) : 1;

  const res = await apiFetch(`/v1/services?page=${page}`);
  const data: ServicesPageData = res.ok
    ? await res.json()
    : { items: [], total: 0, page: 1, page_size: 8 };

  return (
    <div>
      <h1 className="text-2xl font-semibold">Services</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        API services available on BehaviorPulse.
      </p>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div>
          <ServicesList services={data.items} />
          <PaginationControls page={data.page} pageSize={data.page_size} total={data.total} />
        </div>
        <ServiceDemo />
      </div>
    </div>
  );
}