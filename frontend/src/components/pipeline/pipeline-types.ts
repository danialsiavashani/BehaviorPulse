import type { LucideIcon } from "lucide-react";

export type PipelineStageId = 0 | 1 | 2 | 3 | 4;

export type PipelineStage = {
  id: PipelineStageId;
  label: string;
  subtitle: string;
  icon: LucideIcon;
};

export type AnimalConfig = {
  subject: string;
  label: string;
  icon: LucideIcon;
  baseConfidence: number;
  statPct: number;
  colorClass: string;
  badgeClass: string;
};

export type CameraConfig = {
  id: string;
  top: number;
  left: number;
  size: number;
  initialAnimalIndex: number;
  initialDelay: number;
  animalX: number;
  animalY: number;
};

export type CameraDetectionState = {
  firing: boolean;
  fireKey: number;
  animalIndex: number;
  confidence: number;
  animalX: number;
  animalY: number;
};

export type CameraState = Record<string, CameraDetectionState>;

export type RecentDetection = {
  id: number;
  time: string;
  subject: string;
  source: string;
};
