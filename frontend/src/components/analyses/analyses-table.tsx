"use client";

import { useRouter } from "next/navigation";
import { ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";

type AnalysisListItem = {
  analysis_id: string;
  app_name: string;
  subject_label: string;
  total_observations: number;
  computed_confidence: number;
  created_at: string;
};

export function AnalysesTable({ analyses }: { analyses: AnalysisListItem[] }) {
  const router = useRouter();

  if (analyses.length === 0) {
    return (
      <div className="rounded-lg border p-10 text-center text-sm text-muted-foreground">
        No analyses yet. Results appear here after calling observations.analyze.
      </div>
    );
  }

  return (
    <>
      {/* Mobile: stacked cards, no horizontal scroll */}
      <div className="space-y-2 md:hidden">
        {analyses.map((a) => (
          <button
            key={a.analysis_id}
            type="button"
            onClick={() => router.push(`/dashboard/analyses/${a.analysis_id}`)}
            className="flex w-full items-center justify-between gap-2 rounded-lg border p-3 text-left transition-colors hover:bg-muted/30"
          >
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium">{a.subject_label}</span>
                <Badge variant="secondary">{Math.round(a.computed_confidence * 100)}%</Badge>
              </div>
              <div className="mt-1 truncate text-xs text-muted-foreground">
                {a.app_name} · {a.total_observations} observations
              </div>
              <div className="mt-0.5 text-xs text-muted-foreground">
                {formatDate(a.created_at)}
              </div>
            </div>
            <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
          </button>
        ))}
      </div>

      {/* Desktop: full table */}
      <div className="hidden overflow-hidden rounded-lg border md:block">
        <table className="w-full text-sm">
          <thead className="border-b bg-muted/40 text-left text-xs text-muted-foreground">
            <tr>
              <th className="px-4 py-2 font-medium">Subject</th>
              <th className="px-4 py-2 font-medium">App</th>
              <th className="px-4 py-2 font-medium">Observations</th>
              <th className="px-4 py-2 font-medium">Confidence</th>
              <th className="px-4 py-2 font-medium">Created</th>
            </tr>
          </thead>
          <tbody>
            {analyses.map((a) => (
              <tr
                key={a.analysis_id}
                onClick={() => router.push(`/dashboard/analyses/${a.analysis_id}`)}
                className="cursor-pointer border-b transition-colors last:border-0 hover:bg-muted/30"
              >
                <td className="px-4 py-2.5 font-medium">{a.subject_label}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{a.app_name}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{a.total_observations}</td>
                <td className="px-4 py-2.5">
                  <Badge variant="secondary">{Math.round(a.computed_confidence * 100)}%</Badge>
                </td>
                <td className="px-4 py-2.5 text-muted-foreground">{formatDate(a.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}