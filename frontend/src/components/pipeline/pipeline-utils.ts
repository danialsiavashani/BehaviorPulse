import {
  ANIMALS,
  CAMERAS,
  HUB,
} from "./pipeline-config";
import type { CameraState } from "./pipeline-types";

export function elbowPath(
  cameraLeft: number,
  cameraTop: number
) {
  return `M ${cameraLeft},${cameraTop} L ${cameraLeft},${HUB.top} L ${HUB.left},${HUB.top}`;
}

export function randomBetween(
  min: number,
  max: number
) {
  return (
    Math.floor(
      Math.random() * (max - min + 1)
    ) + min
  );
}

export function confidenceFor(
  animalIndex: number
) {
  const base =
    ANIMALS[animalIndex].baseConfidence;

  const variation =
    (Math.random() - 0.5) * 0.06;

  return Math.min(
    0.99,
    Math.max(
      0.8,
      Number(
        (base + variation).toFixed(2)
      )
    )
  );
}

export function nextAnimalIndex(
  currentIndex: number,
  fireKey: number
) {
  if (
    fireKey === 0 ||
    Math.random() > 0.4
  ) {
    return currentIndex;
  }

  const candidates = ANIMALS.map(
    (_, index) => index
  ).filter(
    (index) =>
      index !== currentIndex
  );

  return candidates[
    randomBetween(
      0,
      candidates.length - 1
    )
  ];
}

export function formatDetectionTime(
  date = new Date()
) {
  return date.toLocaleTimeString(
    [],
    {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }
  );
}

export function createInitialCameraState(): CameraState {
  return Object.fromEntries(
    CAMERAS.map((camera) => [
      camera.id,
      {
        firing: false,
        fireKey: 0,
        animalIndex:
          camera.initialAnimalIndex,
        confidence:
          ANIMALS[
            camera.initialAnimalIndex
          ].baseConfidence,
        animalX: camera.animalX,
        animalY: camera.animalY,
      },
    ])
  );
}
