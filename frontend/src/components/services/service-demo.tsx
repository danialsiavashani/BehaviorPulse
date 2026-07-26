"use client";

import { useEffect, useRef, useState } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const STEPS = [
  { label: "01 Send", detail: "POST timestamped detections, any mix of subjects" },
  { label: "02 Compute", detail: "Deterministic pandas/numpy analytics, never estimated" },
  { label: "03 Explain", detail: "Plain-English summary, no invented numbers" },
] as const;

const RESULT_JSON = `{
  "summary": "Birds dominate activity (92.9%)...",
  "prediction": "Next likely window: Saturday, 6-8 AM",
  "computed_confidence": 0.87
}`;

export function ServiceDemo() {
  const [step, setStep] = useState(0);
  const [typedLength, setTypedLength] = useState(0);
  const cycleRef = useRef<ReturnType<typeof setInterval> | null>(null);

  function startCycle() {
    if (cycleRef.current) clearInterval(cycleRef.current);
    cycleRef.current = setInterval(() => setStep((s) => (s + 1) % 3), 2400);
  }

  useEffect(() => {
    startCycle();
    return () => {
      if (cycleRef.current) clearInterval(cycleRef.current);
    };
  }, []);

  useEffect(() => {
    if (step !== 2) {
      setTypedLength(0);
      return;
    }
    const typing = setInterval(() => {
      setTypedLength((len) => {
        if (len >= RESULT_JSON.length) {
          clearInterval(typing);
          return len;
        }
        return len + 2;
      });
    }, 18);
    return () => clearInterval(typing);
  }, [step]);

  function handleAnalyzeClick() {
    setStep(1);
    startCycle();
  }

  return (
    <div>
      <div className="flex flex-col gap-1">
        {STEPS.map((s, i) => (
          <button
            key={s.label}
            onClick={() => setStep(i)}
            className={cn(
              "rounded-md border p-3 text-left transition-colors",
              step === i ? "border-primary/40 bg-primary/5" : "border-transparent"
            )}
          >
            <p
              className={cn(
                "text-sm font-medium transition-colors",
                step === i ? "text-primary" : "text-foreground"
              )}
            >
              {s.label}
            </p>
            <p className="mt-0.5 text-xs leading-relaxed text-muted-foreground">{s.detail}</p>
          </button>
        ))}
      </div>

      <div className="mt-3 flex h-40 flex-col justify-center rounded-lg border bg-muted/40 p-6 font-mono text-xs leading-relaxed text-muted-foreground">
        {step === 0 && (
          <div className="animate-in fade-in-0 zoom-in-95 duration-300 flex flex-col items-center justify-center gap-3 text-center">
            <div className="text-foreground/70">POST /v1/observations/analyze</div>
            <button
              onClick={handleAnalyzeClick}
              className="scale-95 cursor-pointer rounded-md bg-primary px-4 py-2 text-primary-foreground transition-transform hover:scale-100 active:scale-90"
            >
              Analyze
            </button>
          </div>
        )}

        {step === 1 && (
          <div className="animate-in fade-in-0 zoom-in-95 duration-300 flex flex-col items-center justify-center gap-2 text-center">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
            <div>Computing patterns with pandas / numpy...</div>
          </div>
        )}

        {step === 2 && (
          <div className="animate-in fade-in-0 duration-200">
            {typedLength >= RESULT_JSON.length ? (
              <>
                <div className="text-foreground/70">{"{"}</div>
                <div className="pl-4">
                  &quot;summary&quot;: &quot;Birds dominate activity (92.9%)...&quot;,
                </div>
                <div className="pl-4">
                  &quot;prediction&quot;: &quot;Next likely window: Saturday, 6-8 AM&quot;,
                </div>
                <div className="pl-4">
                  &quot;computed_confidence&quot;: <span className="text-primary">0.87</span>
                </div>
                <div className="text-foreground/70">{"}"}</div>
              </>
            ) : (
              <pre className="whitespace-pre-wrap font-mono">
                {RESULT_JSON.slice(0, typedLength)}
                <span className="opacity-70">▋</span>
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}