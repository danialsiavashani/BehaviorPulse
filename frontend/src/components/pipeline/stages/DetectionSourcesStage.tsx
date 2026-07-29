"use client";

import type { CSSProperties } from "react";

import {
  Activity,
  Home,
  Server,
  TreePine,
  Video,
} from "lucide-react";

import { cn } from "@/lib/utils";

import {
  ANIMALS,
  CAMERAS,
  HUB,
  MAX_RECENT_DETECTIONS,
} from "../pipeline-config";

import type {
  CameraState,
  RecentDetection,
} from "../pipeline-types";

import { elbowPath } from "../pipeline-utils";

type ForestTreeProps = {
  top: string;
  left: string;
  sizeClass: string;
  foliageClass?: string;
  opacityClass?: string;
};

function ForestTree({
  top,
  left,
  sizeClass,
  foliageClass = "text-green-950",
  opacityClass = "opacity-90",
}: ForestTreeProps) {
  return (
    <div
      className={cn(
        "absolute",
        sizeClass,
        opacityClass
      )}
      style={{ top, left }}
      aria-hidden="true"
    >
      <span className="absolute bottom-[4%] left-1/2 h-[36%] w-[16%] -translate-x-1/2 rounded-sm bg-amber-950/90" />

      <TreePine
        className={cn(
          "relative h-full w-full",
          foliageClass
        )}
      />
    </div>
  );
}

type DetectionSourcesStageProps = {
  cameraState: CameraState;
  recentDetections: RecentDetection[];
};

export function DetectionSourcesStage({
  cameraState,
  recentDetections,
}: DetectionSourcesStageProps) {
  return (
    <div className="animate-in fade-in-0 relative flex h-full min-h-0 flex-col duration-300">
      <div className="relative flex-1">
        <ForestTree
          top="4%"
          left="38%"
          sizeClass="h-9 w-9"
          foliageClass="text-green-950"
        />

        <ForestTree
          top="24%"
          left="2%"
          sizeClass="h-10 w-10"
          foliageClass="text-green-950"
          opacityClass="opacity-85"
        />

        <ForestTree
          top="43%"
          left="8%"
          sizeClass="h-8 w-8"
          foliageClass="text-emerald-950"
        />

        <ForestTree
          top="72%"
          left="9%"
          sizeClass="h-9 w-9"
          foliageClass="text-green-900"
          opacityClass="opacity-80"
        />

        <ForestTree
          top="24%"
          left="90%"
          sizeClass="h-11 w-11"
          foliageClass="text-emerald-950"
          opacityClass="opacity-80"
        />

        <ForestTree
          top="60%"
          left="3%"
          sizeClass="h-7 w-7"
          foliageClass="text-green-950"
        />

        <ForestTree
          top="7%"
          left="68%"
          sizeClass="h-8 w-8"
          foliageClass="text-green-900"
          opacityClass="opacity-85"
        />

        <ForestTree
          top="77%"
          left="27%"
          sizeClass="h-7 w-7"
          foliageClass="text-emerald-950"
        />

        <ForestTree
          top="10%"
          left="57%"
          sizeClass="h-10 w-10"
          foliageClass="text-green-950"
          opacityClass="opacity-75"
        />

        <Home
          className="absolute h-7 w-7 fill-amber-950/45 text-amber-950 drop-shadow-sm"
          style={{
            top: "50%",
            left: "1%",
          }}
          aria-label="Cabin"
        />

        <Home
          className="absolute h-7 w-7 fill-amber-950/45 text-amber-950 drop-shadow-sm"
          style={{
            top: "57%",
            left: "88%",
          }}
          aria-label="Cabin"
        />

        <Home
          className="absolute h-6 w-6 fill-amber-950/45 text-amber-950 drop-shadow-sm"
          style={{
            top: "9%",
            left: "82%",
          }}
          aria-label="Cabin"
        />

        <svg
          className="absolute inset-0 h-full w-full overflow-visible text-primary/35"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          {CAMERAS.map(
            (camera) => (
              <path
                key={camera.id}
                d={elbowPath(
                  camera.left,
                  camera.top
                )}
                fill="none"
                stroke="currentColor"
                strokeWidth="0.55"
                strokeDasharray="1.6 1.4"
              />
            )
          )}
        </svg>

        <div
          className="absolute -translate-x-1/2 -translate-y-1/2 rounded-md border border-primary/30 bg-primary p-1.5 text-primary-foreground shadow-sm"
          style={{
            top: `${HUB.top}%`,
            left: `${HUB.left}%`,
          }}
          aria-label="Observation receiver"
        >
          <Server className="h-4 w-4" />
        </div>

        {CAMERAS.map(
          (camera) => {
            const state =
              cameraState[
                camera.id
              ];

            const animal =
              ANIMALS[
                state.animalIndex
              ];

            const AnimalIcon =
              animal.icon;

            return (
              <div
                key={camera.id}
                className="absolute -translate-x-1/2 -translate-y-1/2"
                style={{
                  top: `${camera.top}%`,
                  left: `${camera.left}%`,
                }}
              >
                <div className="relative flex items-center justify-center">
                  {state.firing && (
                    <span
                      key={`pulse-${state.fireKey}`}
                      className="absolute rounded-full bg-primary/35 [animation:camera-pulse_1.2s_ease-out_both]"
                      style={{
                        width:
                          camera.size,
                        height:
                          camera.size,
                      }}
                    />
                  )}

                  <div
                    className={cn(
                      "relative flex items-center justify-center rounded-md border p-1.5 shadow-sm transition-colors duration-300",
                      state.firing
                        ? "border-primary/40 bg-primary text-primary-foreground"
                        : "border-primary/20 bg-primary/90 text-primary-foreground/80"
                    )}
                  >
                    <Video
                      style={{
                        width:
                          camera.size,
                        height:
                          camera.size,
                      }}
                    />

                    {state.firing && (
                      <AnimalIcon
                        key={`animal-${state.fireKey}`}
                        className={cn(
                          "pointer-events-none absolute -right-3 -top-2 h-4 w-4 drop-shadow-[0_1px_2px_rgba(0,0,0,0.85)] [animation:animal-drift_2.2s_ease-in-out_both]",
                          animal.colorClass
                        )}
                        style={
                          {
                            "--animal-x": `${state.animalX}px`,
                            "--animal-y": `${state.animalY}px`,
                            "--animal-mid-x": `${state.animalX * 0.42}px`,
                            "--animal-mid-y": `${state.animalY * 0.42}px`,
                          } as CSSProperties
                        }
                        aria-label={
                          animal.subject
                        }
                      />
                    )}
                  </div>
                </div>

                <div className="mt-0.5 text-center font-mono text-[8px] text-primary/80">
                  {camera.id}
                </div>

                {state.firing && (
                  <div
                    key={`label-${state.fireKey}`}
                    className={cn(
                      "absolute left-1/2 top-full z-20 mt-1.5 -translate-x-1/2 whitespace-nowrap rounded border px-1.5 py-0.5 font-mono text-[9px] shadow-sm [animation:detection-label_2.2s_ease-in-out_both]",
                      animal.badgeClass
                    )}
                  >
                    {
                      animal.subject
                    }{" "}
                    -{" "}
                    {state.confidence.toFixed(
                      2
                    )}
                  </div>
                )}
              </div>
            );
          }
        )}
      </div>

      <div className="relative z-10 mt-2 grid shrink-0 gap-2 sm:grid-cols-[minmax(0,1fr)_minmax(240px,0.9fr)]">
        <div className="rounded-lg border bg-background px-3 py-2 shadow-sm">
          <div className="flex items-center gap-2 text-[10px] text-foreground">
            <Activity className="h-3.5 w-3.5 shrink-0 text-primary" />

            <span>
              Example: a wildlife application sends raw detections
            </span>
          </div>

          <div className="mt-2 rounded border bg-muted/40 px-2 py-2">
            <code className="block overflow-x-auto whitespace-nowrap font-mono text-[10px] font-medium text-primary">
              {`{ observed_at, subject, source, confidence }`}
            </code>
          </div>
        </div>

        <div className="rounded-lg border border-green-950/15 bg-white px-3 py-2 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <span className="text-[9px] font-semibold uppercase tracking-wide text-primary">
              Recent detections
            </span>

            <span className="flex items-center gap-1 font-mono text-[8px] text-primary/70">
              <span className="h-1.5 w-1.5 rounded-full bg-lime-500 animate-pulse" />

              live
            </span>
          </div>

          <div className="mt-1.5 h-[52px] overflow-hidden">
            {recentDetections.length ===
            0 ? (
              <div className="rounded border border-dashed border-green-950/15 px-2 py-1.5 text-center text-[9px] text-green-950/45">
                Waiting for a
                detection...
              </div>
            ) : (
              <div className="space-y-1">
                {recentDetections
                  .slice(
                    0,
                    MAX_RECENT_DETECTIONS
                  )
                  .map(
                    (
                      detection
                    ) => (
                      <div
                        key={
                          detection.id
                        }
                        className="grid h-[24px] grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-2 overflow-hidden rounded border border-green-950/10 bg-green-50/70 px-2 font-mono text-[8px] text-primary/80 sm:text-[9px]"
                      >
                        <span className="whitespace-nowrap tabular-nums text-primary/70">
                          {
                            detection.time
                          }
                        </span>

                        <span className="min-w-0 truncate font-semibold text-green-950">
                          {
                            detection.subject
                          }
                        </span>

                        <span className="whitespace-nowrap text-green-800/65">
                          {
                            detection.source
                          }
                        </span>
                      </div>
                    )
                  )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
