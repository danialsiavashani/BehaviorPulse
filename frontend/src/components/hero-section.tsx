import Link from "next/link";
import { Button } from "@/components/ui/button";
import { PipelineAnimation } from "@/components/pipeline";
import { DemoLoginButton } from "@/components/auth/demo-login-button";

export function HeroSection() {
  return (
    <div className="grid w-full gap-10 px-[5%] py-12 md:grid-cols-2 md:items-center md:gap-16 md:py-0">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          For camera, sensor & CV detection pipelines
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
          Compute first. Explain second. Never guess.
        </h1>
        <p className="mt-4 text-base leading-relaxed text-muted-foreground">
          Send raw, timestamped detections — from a CNN-driven camera pipeline
          or just structured data you provide. BehaviorPulse computes every
          pattern deterministically before an LLM ever sees it, and only
          explains facts that already exist.
        </p>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <DemoLoginButton />
          <Button size="lg" variant="outline" asChild>
            <Link href="/signup">Get started</Link>
          </Button>
          <Button size="lg" variant="ghost" asChild>
            <Link href="/login">Log in</Link>
          </Button>
        </div>
      </div>

      <PipelineAnimation />
    </div>
  );
}