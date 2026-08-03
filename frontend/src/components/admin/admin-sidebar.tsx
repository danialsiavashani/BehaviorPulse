"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, LayoutDashboard, Users, Home } from "lucide-react";
import { cn } from "@/lib/utils";
import { LogoutButton } from "@/components/dashboard/logout-button";

const NAV_ITEMS = [
  { label: "Overview", href: "/admin", icon: LayoutDashboard },
  { label: "Users", href: "/admin/users", icon: Users },
] as const;

export function AdminSidebar({ adminEmail }: { adminEmail: string }) {
  const pathname = usePathname();

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden w-56 shrink-0 flex-col border-r lg:flex">
        <div className="flex h-14 items-center gap-2 border-b px-5">
          <ShieldCheck className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium">Admin</span>
        </div>

        <nav className="flex flex-1 flex-col gap-0.5 p-3">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/admin" ? pathname === item.href : pathname.startsWith(item.href);

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
          <Link
            href="/dashboard"
            className="flex items-center gap-2 rounded-md px-2.5 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <Home className="h-4 w-4" />
            User Panel
          </Link>
        </div>

        <div className="border-t p-3">
          <p className="truncate px-2.5 text-xs text-muted-foreground">{adminEmail}</p>
          <LogoutButton />
        </div>
      </aside>

      {/* Mobile top bar + horizontal tabs */}
      <div className="flex flex-col border-b lg:hidden">
        <div className="flex h-14 items-center justify-between px-[5%]">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium">Admin</span>
          </div>
          <div className="flex items-center gap-1">
            <Link
              href="/dashboard"
              aria-label="User Panel"
              className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              <Home className="h-4 w-4" />
            </Link>
            <LogoutButton compact />
          </div>
        </div>

        <nav className="flex gap-2 overflow-x-auto px-[5%] pb-3">
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/admin" ? pathname === item.href : pathname.startsWith(item.href);

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