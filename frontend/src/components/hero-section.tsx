import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ServiceDemo } from "@/components/services/service-demo";
import { DemoLoginButton } from "@/components/auth/demo-login-button";

export function HeroSection() {
  return (
    <div className="grid w-full gap-16 px-[5%] md:grid-cols-2 md:items-center">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Behavioral analytics for computer-vision pipelines
        </h1>
        <p className="mt-4 text-base leading-relaxed text-muted-foreground">
          Send timestamped observation data from your cameras or sensors.
          BehaviorPulse computes deterministic patterns and returns plain-English
          summaries, predictions, and confidence scores — no guessing, no invented numbers.
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

      <ServiceDemo />
    </div>
  );
}