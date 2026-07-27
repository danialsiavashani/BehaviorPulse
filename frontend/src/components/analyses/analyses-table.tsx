"use client";

import { useRouter } from "next/navigation";
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
    <div className="overflow-hidden rounded-lg border">
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
  );
}