import {
  ArrowRight,
  Ban,
  BarChart3,
  BrainCircuit,
  ShieldCheck,
} from "lucide-react";

export function EvidenceGateStage() {
  return (
    <div className="animate-in fade-in-0 zoom-in-95 flex h-full min-h-0 flex-col items-center justify-center gap-4 duration-300">
      <div className="text-center">
        <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary">
          <ShieldCheck className="h-[18px] w-[18px]" />
        </div>

        <h4 className="mt-2 text-sm font-semibold text-foreground">
          Only computed facts reach
          the LLM
        </h4>

        <p className="mt-1 max-w-lg text-[11px] leading-relaxed text-muted-foreground">
          Raw observation records
          are analyzed
          deterministically, but
          they are never included
          in the LLM evidence
          packet.
        </p>
      </div>

      <div className="flex w-full max-w-2xl flex-col items-stretch justify-center gap-2 sm:flex-row sm:items-center">
        <div className="flex flex-1 flex-col items-center rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-center">
          <Ban className="h-4 w-4 text-destructive" />

          <span className="mt-1 font-mono text-[10px] text-foreground/80">
            Raw observations
          </span>

          <span className="text-[9px] text-destructive">
            Not sent to the LLM
          </span>
        </div>

        <ArrowRight className="mx-auto h-4 w-4 rotate-90 text-muted-foreground/50 sm:rotate-0" />

        <div className="flex flex-1 flex-col items-center rounded-lg border border-primary/30 bg-primary/5 p-3 text-center">
          <BarChart3 className="h-4 w-4 text-primary" />

          <span className="mt-1 font-mono text-[10px] text-foreground/80">
            Evidence packet
          </span>

          <span className="text-[9px] text-primary">
            Frequencies,
            recurrence, confidence
          </span>
        </div>

        <ArrowRight className="mx-auto h-4 w-4 rotate-90 text-muted-foreground/50 sm:rotate-0" />

        <div className="flex flex-1 flex-col items-center rounded-lg border bg-background p-3 text-center">
          <BrainCircuit className="h-4 w-4 text-muted-foreground" />

          <span className="mt-1 font-mono text-[10px] text-foreground/80">
            LLM explanation
          </span>

          <span className="text-[9px] text-muted-foreground">
            Cannot recalculate
            metrics
          </span>
        </div>
      </div>
    </div>
  );
}
