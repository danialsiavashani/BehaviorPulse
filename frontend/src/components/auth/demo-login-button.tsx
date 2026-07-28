"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { demoLogin } from "@/lib/auth";
import { Button } from "@/components/ui/button";

export function DemoLoginButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setLoading(true);
    setError(null);

    const result = await demoLogin();

    if (result?.error) {
      setError(result.error);
      setLoading(false);
      return;
    }

    router.push("/dashboard");
    router.refresh();
  }

  return (
    <div>
      <Button
        size="lg"
        onClick={handleClick}
        disabled={loading}
        className="h-12 px-6 text-base"
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Setting up your demo...
          </>
        ) : (
          "Try the live demo"
        )}
      </Button>
      {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
    </div>
  );
}