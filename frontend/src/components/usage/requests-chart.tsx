import { formatDate } from "@/lib/utils";

type DayCount = { date: string; count: number };

export function RequestsChart({
  data,
  title = "Requests over the last 14 days",
}: {
  data: DayCount[];
  title?: string;
}) {
  const maxCount = Math.max(...data.map((d) => d.count), 1);

  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm font-medium">{title}</p>
      <div className="mt-4 flex h-32 items-end gap-1">
        {data.map((d) => (
          <div key={d.date} className="group relative flex-1">
            <div
              className="w-full rounded-sm bg-primary/70 transition-colors group-hover:bg-primary"
              style={{
                height: `${(d.count / maxCount) * 100}%`,
                minHeight: d.count > 0 ? "4px" : "2px",
              }}
            />
            <div className="pointer-events-none absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap rounded bg-foreground px-1.5 py-0.5 text-[10px] text-background opacity-0 transition-opacity group-hover:opacity-100">
              {d.count}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-2 flex justify-between text-[10px] text-muted-foreground">
        <span>{data[0] ? formatDate(data[0].date) : ""}</span>
        <span>{data[data.length - 1] ? formatDate(data[data.length - 1].date) : ""}</span>
      </div>
    </div>
  );
}