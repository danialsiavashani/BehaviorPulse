export function BreakdownList({
  title,
  items,
}: {
  title: string;
  items: { label: string; count: number }[];
}) {
  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm font-medium">{title}</p>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-muted-foreground">No data yet.</p>
      ) : (
        <div className="mt-3 flex flex-col gap-2">
          {items.map((item) => (
            <div key={item.label} className="flex items-center justify-between text-sm">
              <span>{item.label}</span>
              <span className="text-muted-foreground">{item.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}