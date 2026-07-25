"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { logout } from "@/lib/auth";

export function LogoutButton({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleLogout() {
    setLoading(true);
    await logout();
    router.push("/login");
    router.refresh();
  }

  if (compact) {
    return (
      <Button
        variant="ghost"
        size="icon"
        onClick={handleLogout}
        disabled={loading}
        aria-label="Log out"
      >
        <LogOut className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      className="mt-1 w-full justify-start gap-2 px-2.5"
      onClick={handleLogout}
      disabled={loading}
    >
      <LogOut className="h-4 w-4" />
      {loading ? "Logging out..." : "Log out"}
    </Button>
  );
}