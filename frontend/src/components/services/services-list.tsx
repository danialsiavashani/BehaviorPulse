import { Badge } from "@/components/ui/badge";
import { CopyableId } from "@/components/apps/copyable-id";
import { formatDate } from "@/lib/utils";

type Service = {
  id: string;
  service_key: string;
  name: string;
  description: string;
  status: string;
  endpoint: string;
  created_at: string;
};

export function ServicesList({ services }: { services: Service[] }) {
  if (services.length === 0) {
    return (
      <div className="rounded-lg border p-10 text-center text-sm text-muted-foreground">
        No services available yet.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {services.map((service) => (
        <div key={service.id} className="rounded-lg border p-4">
          <div className="flex items-center gap-2">
            <p className="font-medium">{service.name}</p>
            <Badge variant={service.status === "active" ? "secondary" : "outline"}>
              {service.status}
            </Badge>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{service.description}</p>

          <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
            <CopyableId value={service.endpoint} />
            <span className="font-mono">{service.service_key}</span>
            <span>Added {formatDate(service.created_at)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}