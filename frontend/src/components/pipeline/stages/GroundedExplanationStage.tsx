import { BrainCircuit } from "lucide-react";

import {
  REAL_PREDICTION,
  REAL_SUMMARY,
} from "../pipeline-config";

type GroundedExplanationStageProps = {
  summaryLength: number;
  predictionLength: number;
};

export function GroundedExplanationStage({
  summaryLength,
  predictionLength,
}: GroundedExplanationStageProps) {
  return (
    <div className="animate-in fade-in-0 flex h-full min-h-0 flex-col gap-3 duration-200">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b pb-2">
        <div className="flex items-center gap-2">
          <BrainCircuit className="h-4 w-4 text-primary" />

          <span className="text-xs font-semibold text-foreground">
            Provider-agnostic
            grounded explanation
          </span>
        </div>

        <span className="rounded-md border border-primary/25 bg-primary/5 px-2 py-0.5 font-mono text-[10px] text-primary">
          Computed confidence:
          0.97
        </span>
      </div>

      <div className="rounded-lg border bg-background p-3">
        <span className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
          Summary
        </span>

        <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
          {REAL_SUMMARY.slice(
            0,
            summaryLength
          )}

          {summaryLength <
            REAL_SUMMARY.length && (
            <span className="opacity-70">
              |
            </span>
          )}
        </p>
      </div>

      {summaryLength >=
        REAL_SUMMARY.length && (
        <div className="animate-in fade-in-0 rounded-lg border border-primary/30 bg-primary/5 p-3 duration-300">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-primary">
              Pattern estimate
            </span>

            <span className="text-[9px] font-medium text-muted-foreground">
              Not a guarantee
            </span>
          </div>

          <p className="mt-1 text-xs font-medium leading-relaxed text-foreground">
            {REAL_PREDICTION.slice(
              0,
              predictionLength
            )}

            {predictionLength <
              REAL_PREDICTION.length && (
              <span className="opacity-70">
                |
              </span>
            )}
          </p>
        </div>
      )}
    </div>
  );
}
