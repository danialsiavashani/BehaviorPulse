"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  ANIMALS,
  CAMERAS,
  DETECTION_VISIBLE_MS,
  MAX_NEXT_DETECTION_MS,
  MAX_RECENT_DETECTIONS,
  MIN_NEXT_DETECTION_MS,
  REAL_PREDICTION,
  REAL_SUMMARY,
} from "./pipeline-config";

import type {
  CameraDetectionState,
  CameraState,
  PipelineStageId,
  RecentDetection,
} from "./pipeline-types";

import {
  confidenceFor,
  createInitialCameraState,
  formatDetectionTime,
  nextAnimalIndex,
  randomBetween,
} from "./pipeline-utils";

export function usePipelineAnimation() {
  const [
    activeStage,
    setActiveStage,
  ] = useState<PipelineStageId>(0);

  const [
    settled,
    setSettled,
  ] = useState(false);

  const [
    summaryLength,
    setSummaryLength,
  ] = useState(0);

  const [
    predictionLength,
    setPredictionLength,
  ] = useState(0);

  const [
    cameraState,
    setCameraState,
  ] = useState<CameraState>(
    createInitialCameraState
  );

  const [
    recentDetections,
    setRecentDetections,
  ] = useState<RecentDetection[]>([]);

  const stageTimeouts = useRef<
    ReturnType<typeof setTimeout>[]
  >([]);

  const cameraTimeouts = useRef<
    ReturnType<typeof setTimeout>[]
  >([]);

  const cameraStateRef =
    useRef<CameraState>(
      createInitialCameraState()
    );

  const detectionSequence =
    useRef(0);

  const clearStageTimers =
    useCallback(() => {
      stageTimeouts.current.forEach(
        clearTimeout
      );

      stageTimeouts.current = [];
    }, []);

  const clearCameraTimers =
    useCallback(() => {
      cameraTimeouts.current.forEach(
        clearTimeout
      );

      cameraTimeouts.current = [];
    }, []);

  useEffect(() => {
    const schedule = (
      stage: PipelineStageId,
      delay: number
    ) => {
      const timer = setTimeout(
        () => setActiveStage(stage),
        delay
      );

      stageTimeouts.current.push(
        timer
      );
    };

    schedule(1, 2300);
    schedule(2, 4200);
    schedule(3, 6200);
    schedule(4, 8000);

    const settleTimer = setTimeout(
      () => setSettled(true),
      8200
    );

    stageTimeouts.current.push(
      settleTimer
    );

    return clearStageTimers;
  }, [clearStageTimers]);

  useEffect(() => {
    if (activeStage !== 4) {
      return;
    }

    let typingPrediction:
      | ReturnType<typeof setInterval>
      | undefined;

    const typingSummary =
      setInterval(() => {
        setSummaryLength(
          (length) => {
            if (
              length >=
              REAL_SUMMARY.length
            ) {
              clearInterval(
                typingSummary
              );

              return length;
            }

            return length + 2;
          }
        );
      }, 10);

    const predictionDelay =
      setTimeout(() => {
        typingPrediction =
          setInterval(() => {
            setPredictionLength(
              (length) => {
                if (
                  length >=
                  REAL_PREDICTION.length
                ) {
                  if (
                    typingPrediction
                  ) {
                    clearInterval(
                      typingPrediction
                    );
                  }

                  return length;
                }

                return length + 2;
              }
            );
          }, 10);
      }, 1400);

    return () => {
      clearInterval(
        typingSummary
      );

      clearTimeout(
        predictionDelay
      );

      if (typingPrediction) {
        clearInterval(
          typingPrediction
        );
      }
    };
  }, [activeStage]);

  useEffect(() => {
    clearCameraTimers();

    if (activeStage !== 0) {
      const resetState =
        createInitialCameraState();

      cameraStateRef.current =
        resetState;

      setCameraState({
        ...resetState,
      });

      setRecentDetections([]);

      return;
    }

    let cancelled = false;

    const scheduleDetection = (
      camera: (typeof CAMERAS)[number],
      delay: number
    ) => {
      const detectionTimer =
        setTimeout(() => {
          if (cancelled) {
            return;
          }

          const current =
            cameraStateRef.current[
              camera.id
            ];

          const animalIndex =
            nextAnimalIndex(
              current.animalIndex,
              current.fireKey
            );

          const confidence =
            confidenceFor(
              animalIndex
            );

          const nextCameraState: CameraDetectionState =
            {
              firing: true,
              fireKey:
                current.fireKey + 1,
              animalIndex,
              confidence,
              animalX:
                camera.animalX +
                randomBetween(-5, 5),
              animalY:
                camera.animalY +
                randomBetween(-4, 4),
            };

          cameraStateRef.current = {
            ...cameraStateRef.current,
            [camera.id]:
              nextCameraState,
          };

          setCameraState({
            ...cameraStateRef.current,
          });

          detectionSequence.current += 1;

          const nextDetection: RecentDetection =
            {
              id: detectionSequence.current,
              time:
                formatDetectionTime(),
              subject:
                ANIMALS[
                  animalIndex
                ].subject,
              source: camera.id,
            };

          setRecentDetections(
            (previous) =>
              [
                nextDetection,
                ...previous,
              ].slice(
                0,
                MAX_RECENT_DETECTIONS
              )
          );

          const stopTimer =
            setTimeout(() => {
              if (cancelled) {
                return;
              }

              const latest =
                cameraStateRef.current[
                  camera.id
                ];

              cameraStateRef.current =
                {
                  ...cameraStateRef.current,
                  [camera.id]: {
                    ...latest,
                    firing: false,
                  },
                };

              setCameraState({
                ...cameraStateRef.current,
              });
            }, DETECTION_VISIBLE_MS);

          cameraTimeouts.current.push(
            stopTimer
          );

          scheduleDetection(
            camera,
            randomBetween(
              MIN_NEXT_DETECTION_MS,
              MAX_NEXT_DETECTION_MS
            )
          );
        }, delay);

      cameraTimeouts.current.push(
        detectionTimer
      );
    };

    CAMERAS.forEach(
      (camera) => {
        scheduleDetection(
          camera,
          camera.initialDelay
        );
      }
    );

    return () => {
      cancelled = true;
      clearCameraTimers();
    };
  }, [
    activeStage,
    clearCameraTimers,
  ]);

  const selectStage = useCallback(
    (id: PipelineStageId) => {
      clearStageTimers();

      setSettled(true);
      setActiveStage(id);

      if (id === 4) {
        setSummaryLength(
          REAL_SUMMARY.length
        );

        setPredictionLength(
          REAL_PREDICTION.length
        );
      }
    },
    [clearStageTimers]
  );

  return {
    activeStage,
    settled,
    summaryLength,
    predictionLength,
    cameraState,
    recentDetections,
    selectStage,
  };
}
