import { BarChart3 } from "lucide-react";

import { ANIMALS } from "../pipeline-config";

export function DataProcessingStage() {
  return (
    <div className="animate-in fade-in-0 zoom-in-95 flex h-full min-h-0 flex-col gap-4 duration-300">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b pb-2">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-primary" />

          <span className="text-xs font-semibold text-foreground">
            Deterministic Frequency
            and Recurrence Analysis
          </span>
        </div>

        <span className="font-mono text-[10px] text-muted-foreground">
          pandas / NumPy
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-2.5 rounded-lg border bg-background p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
              Subject frequency
            </span>

            <span className="font-mono text-[10px] text-muted-foreground">
              28 observations
            </span>
          </div>

          {ANIMALS.map(
            (animal) => (
              <div
                key={
                  animal.subject
                }
                className="space-y-1"
              >
                <div className="flex items-center justify-between gap-2 font-mono text-[10px]">
                  <span className="text-foreground/80">
                    {
                      animal.label
                    }
                  </span>

                  <span className="font-semibold text-primary">
                    {animal.statPct.toFixed(
                      1
                    )}
                    %
                  </span>
                </div>

                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full origin-left rounded-full bg-primary [animation:metric-fill_900ms_ease-out_both]"
                    style={{
                      width: `${animal.statPct}%`,
                    }}
                  />
                </div>
              </div>
            )
          )}
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="rounded-lg border bg-background p-3">
            <span className="text-[9px] font-semibold uppercase tracking-wide text-muted-foreground">
              Top source
            </span>

            <div className="mt-1 font-mono text-xs font-semibold text-foreground">
              camera_04
            </div>
          </div>

          <div className="rounded-lg border bg-background p-3">
            <span className="text-[9px] font-semibold uppercase tracking-wide text-muted-foreground">
              Peak window
            </span>

            <div className="mt-1 text-xs font-semibold text-foreground">
              Sat, 6-8 AM
            </div>
          </div>

          <div className="rounded-lg border border-primary/25 bg-primary/5 p-3">
            <span className="text-[9px] font-semibold uppercase tracking-wide text-primary/80">
              Recurrence
            </span>

            <div className="mt-1 text-xs font-semibold text-primary">
              5 of 5 Saturdays
            </div>
          </div>

          <div className="rounded-lg border border-primary/25 bg-primary/5 p-3">
            <span className="text-[9px] font-semibold uppercase tracking-wide text-primary/80">
              Computed confidence
            </span>

            <div className="mt-1 font-mono text-xs font-semibold text-primary">
              0.97
            </div>
          </div>

          <div className="col-span-2 rounded-lg border bg-background p-3 text-[10px] leading-relaxed text-muted-foreground">
            Every displayed value is
            computed before the LLM
            is called.
          </div>
        </div>
      </div>
    </div>
  );
}
