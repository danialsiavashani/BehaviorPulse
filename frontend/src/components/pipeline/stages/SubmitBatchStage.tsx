import { Send } from "lucide-react";

export function SubmitBatchStage() {
  return (
    <div className="animate-in fade-in-0 zoom-in-95 flex h-full min-h-0 flex-col gap-3 overflow-hidden duration-300">
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b pb-2">
        <div className="flex items-center gap-2">
          <Send className="h-4 w-4 text-primary" />

          <span className="text-xs font-semibold text-foreground">
            POST /v1/observations/analyze
          </span>
        </div>

        <span className="rounded-md border bg-background px-2 py-0.5 font-mono text-[10px] text-muted-foreground">
          Mixed observation batch
        </span>
      </div>

      <div className="grid min-h-0 flex-1 gap-3 md:grid-cols-[minmax(0,1.45fr)_minmax(190px,0.55fr)]">
        <pre className="h-full min-h-0 min-w-0 overflow-auto rounded-lg border bg-background p-3 font-mono text-[9px] leading-[1.45] text-muted-foreground">
{`{
  "observations": [
    {
      "observed_at": "2026-07-25T06:14:00Z",
      "subject": {
        "type": "animal",
        "label": "hummingbird"
      },
      "source": {
        "type": "camera",
        "id": "camera_04"
      },
      "confidence": 0.91
    },
    {
      "observed_at": "2026-07-25T06:18:00Z",
      "subject": {
        "type": "animal",
        "label": "cat"
      },
      "source": {
        "type": "camera",
        "id": "camera_02"
      },
      "confidence": 0.93
    }
  ]
}`}
        </pre>

        <div className="flex min-h-0 min-w-0 flex-col justify-center gap-2">
          {[
            "Request authenticated",
            "Observation schema validated",
            "Raw records passed to deterministic analytics",
          ].map((item, index) => (
            <div
              key={item}
              className="flex min-w-0 items-start gap-2 rounded-lg border bg-background p-2.5"
            >
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 font-mono text-[9px] font-semibold text-primary">
                {index + 1}
              </span>

              <span className="min-w-0 text-[11px] leading-relaxed text-muted-foreground">
                {item}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
