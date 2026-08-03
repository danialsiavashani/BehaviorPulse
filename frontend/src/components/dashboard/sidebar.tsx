"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  LayoutDashboard,
  Boxes,
  Layers,
  ScrollText,
  BarChart3,
  ClipboardList,
  BookOpen,
  UserCircle,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { LogoutButton } from "@/components/dashboard/logout-button";

const NAV_ITEMS = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard, enabled: true },
  { label: "Apps", href: "/dashboard/apps", icon: Boxes, enabled: true },
  { label: "Services", href: "/dashboard/services", icon: Layers, enabled: true },
  { label: "Logs", href: "/dashboard/logs", icon: ScrollText, enabled: true },
  { label: "Usage", href: "/dashboard/usage", icon: BarChart3, enabled: true },
  { label: "Analyses", href: "/dashboard/analyses", icon: ClipboardList, enabled: true },
  { label: "Docs", href: "/dashboard/docs", icon: BookOpen, enabled: true },
  { label: "Account", href: "/dashboard/account", icon: UserCircle, enabled: true },
] as const;

export function Sidebar({ userEmail, isAdmin }: { userEmail: string; isAdmin?: boolean }) {
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

            const isActive =
              item.href === "/dashboard" ? pathname === item.href : pathname.startsWith(item.href);

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

        {isAdmin && (
          <div className="border-t p-3">
            <Link
              href="/admin"
              className="flex items-center gap-2 rounded-md px-2.5 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <ShieldCheck className="h-4 w-4" />
              Admin Panel
            </Link>
          </div>
        )}

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
          <div className="flex items-center gap-1">
            {isAdmin && (
              <Link
                href="/admin"
                aria-label="Admin Panel"
                className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
              >
                <ShieldCheck className="h-4 w-4" />
              </Link>
            )}
            <LogoutButton compact />
          </div>
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

            const isActive =
              item.href === "/dashboard" ? pathname === item.href : pathname.startsWith(item.href);

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