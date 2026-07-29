import {
  BarChart3,
  Bird,
  BrainCircuit,
  Cat,
  Cpu,
  Dog,
  Radio,
  Send,
  ShieldCheck,
} from "lucide-react";

import type {
  AnimalConfig,
  CameraConfig,
  PipelineStage,
} from "./pipeline-types";

export const REAL_SUMMARY =
  "Over 28 observations, the most common subject was hummingbirds (57.1%), followed by cats (28.6%), with blue jays and dogs each at 7.1%. The top source is camera_04, and peak activity occurs on Saturdays between 6 AM and 8 AM. A recurring pattern is noted: observations occurred on 5 of the last 5 Saturdays.";

export const REAL_PREDICTION =
  "Based on the strong recurring pattern and high prediction confidence (0.97), it is likely that hummingbird activity will continue to be observed on Saturdays during the early morning window, though occasional variations may occur.";

export const STAGES: PipelineStage[] = [
  {
    id: 0,
    label: "Detection Sources",
    subtitle: "Raw observations",
    icon: Radio,
  },
  {
    id: 1,
    label: "Submit Batch",
    subtitle: "Authenticated API request",
    icon: Send,
  },
  {
    id: 2,
    label: "Data Processing",
    subtitle: "Deterministic analytics",
    icon: Cpu,
  },
  {
    id: 3,
    label: "LLM Evidence Gate",
    subtitle: "Computed facts only",
    icon: ShieldCheck,
  },
  {
    id: 4,
    label: "Grounded Explanation",
    subtitle: "Summary and estimate",
    icon: BrainCircuit,
  },
];

export const ANIMALS: AnimalConfig[] = [
  {
    subject: "hummingbird",
    label: "Hummingbird",
    icon: Bird,
    baseConfidence: 0.91,
    statPct: 57.1,
    colorClass: "text-teal-200",
    badgeClass:
      "border-teal-200/40 bg-teal-950/75 text-teal-100",
  },
  {
    subject: "cat",
    label: "Cat",
    icon: Cat,
    baseConfidence: 0.93,
    statPct: 28.6,
    colorClass: "text-amber-200",
    badgeClass:
      "border-amber-200/40 bg-amber-950/75 text-amber-100",
  },
  {
    subject: "blue_jay",
    label: "Blue Jay",
    icon: Bird,
    baseConfidence: 0.86,
    statPct: 7.1,
    colorClass: "text-sky-200",
    badgeClass:
      "border-sky-200/40 bg-sky-950/75 text-sky-100",
  },
  {
    subject: "dog",
    label: "Dog",
    icon: Dog,
    baseConfidence: 0.96,
    statPct: 7.1,
    colorClass: "text-orange-200",
    badgeClass:
      "border-orange-200/40 bg-orange-950/75 text-orange-100",
  },
];

export const HUB = {
  top: 84,
  left: 50,
};

export const CAMERAS: CameraConfig[] = [
  {
    id: "camera_04",
    top: 15,
    left: 15,
    size: 17,
    initialAnimalIndex: 0,
    initialDelay: 400,
    animalX: 18,
    animalY: -8,
  },
  {
    id: "camera_02",
    top: 21,
    left: 79,
    size: 18,
    initialAnimalIndex: 1,
    initialDelay: 1250,
    animalX: -16,
    animalY: 4,
  },
  {
    id: "camera_01",
    top: 46,
    left: 46,
    size: 16,
    initialAnimalIndex: 2,
    initialDelay: 2150,
    animalX: 17,
    animalY: -10,
  },
  {
    id: "camera_03",
    top: 65,
    left: 63,
    size: 18,
    initialAnimalIndex: 3,
    initialDelay: 3000,
    animalX: -18,
    animalY: 4,
  },
];

export const DETECTION_VISIBLE_MS = 2200;
export const MIN_NEXT_DETECTION_MS = 5200;
export const MAX_NEXT_DETECTION_MS = 9000;
export const MAX_RECENT_DETECTIONS = 2;
