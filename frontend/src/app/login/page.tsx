import Link from "next/link";
import { Activity } from "lucide-react";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="grid min-h-svh md:grid-cols-2">
      <div className="hidden flex-col justify-between bg-muted/40 p-10 md:flex">
        <Link href="/" className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium">BehaviorPulse</span>
        </Link>

        <div className="space-y-6">
          <p className="text-base leading-relaxed text-muted-foreground">
            Behavioral analytics for computer-vision and detection pipelines.
          </p>
          <div className="rounded-lg border bg-background p-3.5 font-mono text-xs leading-relaxed text-muted-foreground">
            <div>
              <span className="text-muted-foreground/70">POST</span> /v1/observations/analyze
            </div>
            <div className="mt-1">
              &quot;computed_confidence&quot;: <span className="text-primary">0.87</span>
            </div>
          </div>
        </div>

        <p className="text-xs text-muted-foreground">
          Deterministic analytics, explained in plain English.
        </p>
      </div>

      <div className="flex flex-col justify-center p-6 sm:p-10">
        <div className="mx-auto w-full max-w-sm">
          <Link href="/" className="mb-2 flex items-center gap-2 md:hidden">
            <Activity className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium">BehaviorPulse</span>
          </Link>
          <h1 className="text-xl font-semibold">Log in</h1>
          <p className="mb-6 text-sm text-muted-foreground">
            Access your BehaviorPulse dashboard.
          </p>
          <LoginForm />
          <p className="mt-6 text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-primary underline-offset-4 hover:underline">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}