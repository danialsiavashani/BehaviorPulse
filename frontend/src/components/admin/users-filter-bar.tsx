"use client";

import { useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function UsersFilterBar() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [search, setSearch] = useState(searchParams.get("search") ?? "");

  function updateParam(key: string, value: string | null) {
    const params = new URLSearchParams(searchParams.toString());
    if (value === null || value === "all") {
      params.delete(key);
    } else {
      params.set(key, value);
    }
    params.delete("page");
    router.push(`${pathname}?${params.toString()}`);
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    updateParam("search", search.trim() || null);
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by email..."
          className="w-56"
        />
        <Button type="submit" variant="outline" size="sm" aria-label="Search">
          <Search className="h-4 w-4" />
        </Button>
      </form>

      <Select
        value={searchParams.get("is_active") ?? "all"}
        onValueChange={(value) => updateParam("is_active", value)}
      >
        <SelectTrigger size="sm" className="w-[130px]">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All statuses</SelectItem>
          <SelectItem value="true">Active</SelectItem>
          <SelectItem value="false">Disabled</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={searchParams.get("is_demo") ?? "all"}
        onValueChange={(value) => updateParam("is_demo", value)}
      >
        <SelectTrigger size="sm" className="w-[140px]">
          <SelectValue placeholder="Account type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Real + demo</SelectItem>
          <SelectItem value="false">Real only</SelectItem>
          <SelectItem value="true">Demo only</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}