"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function AppTabs({ appId }: { appId: string }) {
  const pathname = usePathname();

  const tabs = [
    { label: "API keys", href: `/dashboard/apps/${appId}` },
    { label: "Settings", href: `/dashboard/apps/${appId}/settings` },
  ];

  return (
    <div className="mt-6 flex gap-4 border-b">
      {tabs.map((tab) => {
        const isActive = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={cn(
              "border-b-2 pb-2 text-sm transition-colors",
              isActive
                ? "border-primary font-medium text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}