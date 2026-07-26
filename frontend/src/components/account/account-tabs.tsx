"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const TABS = [
  { label: "Profile", href: "/dashboard/account" },
  { label: "Security", href: "/dashboard/account/security" },
  { label: "Notifications", href: "/dashboard/account/notifications" },
  { label: "Team", href: "/dashboard/account/team" },
  { label: "Danger zone", href: "/dashboard/account/danger-zone" },
] as const;

export function AccountTabs() {
  const pathname = usePathname();

  return (
    <div className="mt-4 flex gap-4 border-b">
      {TABS.map((tab) => {
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