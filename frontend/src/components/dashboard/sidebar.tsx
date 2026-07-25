"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  LayoutDashboard,
  Boxes,
  KeyRound,
  Layers,
  ScrollText,
  BarChart3,
  BookOpen,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { LogoutButton } from "@/components/dashboard/logout-button";

const NAV_ITEMS = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard, enabled: true },
  { label: "Apps", href: "/dashboard/apps", icon: Boxes, enabled: true },
  { label: "Services", href: "/dashboard/services", icon: Layers, enabled: false },
  { label: "Logs", href: "/dashboard/logs", icon: ScrollText, enabled: false },
  { label: "Usage", href: "/dashboard/usage", icon: BarChart3, enabled: false },
  { label: "Docs", href: "/dashboard/docs", icon: BookOpen, enabled: false },
] as const;

export function Sidebar({ userEmail }: { userEmail: string }) {
  const pathname = usePathname();

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden w-56 shrink-0 flex-col border-r lg:flex">
        <div className="flex h-14 items-center gap-2 border-b px-5">
          <Activity className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium">BehaviorPulse</span>
        </div>

        <nav className="flex flex-1 flex-col gap-0.5 p-3">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;

            if (!item.enabled) {
              return (
                <div
                  key={item.label}
                  className="flex cursor-not-allowed items-center justify-between rounded-md px-2.5 py-1.5 text-sm text-muted-foreground/50"
                >
                  <span className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </span>
                  <span className="rounded bg-muted px-1.5 py-0.5 text-[10px]">Soon</span>
                </div>
              );
            }

            const isActive = pathname === item.href;

            return (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2.5 py-1.5 text-sm transition-colors",
                  isActive ? "bg-primary/10 text-primary" : "text-foreground hover:bg-muted"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t p-3">
          <p className="truncate px-2.5 text-xs text-muted-foreground">{userEmail}</p>
          <LogoutButton />
        </div>
      </aside>

      {/* Mobile top bar + horizontal scrolling tabs */}
      <div className="flex flex-col border-b lg:hidden">
        <div className="flex h-14 items-center justify-between px-[5%]">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium">BehaviorPulse</span>
          </div>
          <LogoutButton compact />
        </div>

        <nav className="flex gap-2 overflow-x-auto px-[5%] pb-3">
          {NAV_ITEMS.map((item) => {
            if (!item.enabled) {
              return (
                <span
                  key={item.label}
                  className="shrink-0 whitespace-nowrap rounded-full border px-4 py-1.5 text-sm text-muted-foreground/50"
                >
                  {item.label}
                </span>
              );
            }

            const isActive = pathname === item.href;

            return (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "shrink-0 whitespace-nowrap rounded-full border px-4 py-1.5 text-sm transition-colors",
                  isActive
                    ? "border-primary/40 bg-primary/5 font-medium text-primary"
                    : "border-border text-muted-foreground"
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </>
  );
}