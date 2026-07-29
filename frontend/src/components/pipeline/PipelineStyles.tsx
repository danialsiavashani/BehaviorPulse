export function PipelineStyles() {
  return (
    <style jsx global>{`
      @keyframes camera-pulse {
        0% {
          opacity: 0.55;
          transform: scale(0.8);
        }

        100% {
          opacity: 0;
          transform: scale(2.35);
        }
      }

      @keyframes animal-drift {
        0% {
          opacity: 0;
          transform: translate3d(
              0,
              5px,
              0
            )
            scale(0.78);
        }

        20% {
          opacity: 0.55;
        }

        45% {
          opacity: 1;
          transform: translate3d(
              var(--animal-mid-x),
              var(--animal-mid-y),
              0
            )
            scale(1);
        }

        72% {
          opacity: 0.75;
        }

        100% {
          opacity: 0;
          transform: translate3d(
              var(--animal-x),
              var(--animal-y),
              0
            )
            scale(1.08);
        }
      }

      @keyframes detection-label {
        0%,
        100% {
          opacity: 0;
        }

        18%,
        78% {
          opacity: 1;
        }
      }

      @keyframes metric-fill {
        from {
          transform: scaleX(0);
        }

        to {
          transform: scaleX(1);
        }
      }

      @media (
        prefers-reduced-motion:
          reduce
      ) {
        :global(
            [class*="animal-drift"]
          ),
        :global(
            [class*="camera-pulse"]
          ),
        :global(
            [class*="detection-label"]
          ),
        :global(
            [class*="metric-fill"]
          ) {
          animation: none !important;
          opacity: 0.85;
        }
      }
    `}</style>
  );
}
