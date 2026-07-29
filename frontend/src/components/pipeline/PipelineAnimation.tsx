"use client";

import { cn } from "@/lib/utils";

import { PipelineStyles } from "./PipelineStyles";
import { StageTabs } from "./StageTabs";
import { usePipelineAnimation } from "./usePipelineAnimation";

import {
  DataProcessingStage,
  DetectionSourcesStage,
  EvidenceGateStage,
  GroundedExplanationStage,
  SubmitBatchStage,
} from "./stages";

export function PipelineAnimation() {
  const {
    activeStage,
    settled,
    summaryLength,
    predictionLength,
    cameraState,
    recentDetections,
    selectStage,
  } = usePipelineAnimation();

  return (
    <div className="w-full">
      <StageTabs
        activeStage={activeStage}
        onSelect={selectStage}
      />

      <div
        className={cn(
          "relative mt-3 h-[500px] overflow-x-hidden overflow-y-auto rounded-xl border p-5 transition-colors duration-500 [scrollbar-gutter:stable] sm:h-[430px] lg:h-[390px]",
          activeStage === 0
            ? "border-green-950/20 bg-white"
            : "border-border bg-muted/30"
        )}
      >
        {activeStage === 0 && (
          <DetectionSourcesStage
            cameraState={
              cameraState
            }
            recentDetections={
              recentDetections
            }
          />
        )}

        {activeStage === 1 && (
          <SubmitBatchStage />
        )}

        {activeStage === 2 && (
          <DataProcessingStage />
        )}

        {activeStage === 3 && (
          <EvidenceGateStage />
        )}

        {activeStage === 4 && (
          <GroundedExplanationStage
            summaryLength={
              summaryLength
            }
            predictionLength={
              predictionLength
            }
          />
        )}
      </div>

      {settled && (
        <p className="mt-2 text-center text-[11px] text-muted-foreground/70">
          Real output from a real
          analysis. Click any stage above
          to explore.
        </p>
      )}

      <PipelineStyles />
    </div>
  );
}
