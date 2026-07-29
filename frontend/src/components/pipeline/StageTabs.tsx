"use client";

import { cn } from "@/lib/utils";

import { STAGES } from "./pipeline-config";
import type { PipelineStageId } from "./pipeline-types";

type StageTabsProps = {
  activeStage: PipelineStageId;
  onSelect: (
    id: PipelineStageId
  ) => void;
};

export function StageTabs({
  activeStage,
  onSelect,
}: StageTabsProps) {
  return (
    <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-5">
      {STAGES.map((stage) => {
        const StageIcon = stage.icon;

        const isActive =
          activeStage === stage.id;

        return (
          <button
            key={stage.id}
            type="button"
            onClick={() =>
              onSelect(stage.id)
            }
            className={cn(
              "group flex min-h-[76px] min-w-0 flex-col items-start overflow-hidden rounded-lg border p-2.5 text-left transition-all duration-200",
              isActive
                ? "border-primary/40 bg-primary/5 text-foreground shadow-sm"
                : "border-border/60 bg-background text-muted-foreground hover:border-border hover:bg-muted/40 hover:text-foreground"
            )}
          >
            <div className="flex w-full items-center justify-between gap-2">
              <span className="font-mono text-[9px] font-semibold text-muted-foreground/70">
                0{stage.id + 1}
              </span>

              <StageIcon
                className={cn(
                  "h-3.5 w-3.5 shrink-0",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground/60 group-hover:text-foreground/70"
                )}
              />
            </div>

            <span className="mt-1 block min-h-[2rem] w-full min-w-0 whitespace-normal break-words text-[11px] font-semibold leading-[1.15] sm:text-xs">
              {stage.label}
            </span>

            <span className="mt-0.5 hidden w-full min-w-0 truncate text-[9px] text-muted-foreground lg:block">
              {stage.subtitle}
            </span>
          </button>
        );
      })}
    </div>
  );
}
