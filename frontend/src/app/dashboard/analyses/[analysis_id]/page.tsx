import { notFound } from "next/navigation";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";

type AnalysisDetail = {
  analysis_id: string;
  app_name: string;
  subject_label: string;
  total_observations: number;
  computed_confidence: number;
  summary: string;
  prediction: string;
  pattern_table: { metric: string; value: string; support: string }[];
  recommendations: string[];
  warnings: string[];
  created_at: string;
};

export default async function AnalysisDetailPage({
  params,
}: {
  params: Promise<{ analysis_id: string }>;
}) {
  const { analysis_id } = await params;

  const res = await apiFetch(`/v1/analyses/${analysis_id}`);
  if (!res.ok) notFound();
  const analysis: AnalysisDetail = await res.json();

  return (
    <div className="max-w-2xl">
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Link href="/dashboard/analyses" className="hover:text-foreground">
          Analyses
        </Link>
        <ChevronRight className="h-3.5 w-3.5" />
        <span className="text-foreground">{analysis.subject_label}</span>
      </div>

      <div className="mt-3 flex items-center gap-3">
        <h1 className="text-2xl font-semibold">{analysis.subject_label}</h1>
        <Badge variant="secondary">
          {Math.round(analysis.computed_confidence * 100)}% confidence
        </Badge>
      </div>

      <p className="mt-1 text-sm text-muted-foreground">
        {analysis.app_name} · {analysis.total_observations} observations ·{" "}
        {formatDate(analysis.created_at)}
      </p>

      <section className="mt-6">
        <h2 className="text-sm font-medium">Summary</h2>
        <p className="mt-1.5 text-sm text-muted-foreground">{analysis.summary}</p>
      </section>

      <section className="mt-4">
        <h2 className="text-sm font-medium">Prediction</h2>
        <p className="mt-1.5 text-sm text-muted-foreground">{analysis.prediction}</p>
      </section>

      <section className="mt-4">
        <h2 className="text-sm font-medium">Pattern table</h2>
        <div className="mt-1.5 overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <tbody>
              {analysis.pattern_table.map((row) => (
                <tr key={row.metric} className="border-b last:border-0">
                  <td className="px-3 py-2 font-medium">{row.metric}</td>
                  <td className="px-3 py-2">{row.value}</td>
                  <td className="px-3 py-2 text-xs text-muted-foreground">{row.support}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {analysis.recommendations.length > 0 && (
        <section className="mt-4">
          <h2 className="text-sm font-medium">Recommendations</h2>
          <ul className="mt-1.5 list-disc pl-4 text-sm text-muted-foreground">
            {analysis.recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </section>
      )}

      {analysis.warnings.length > 0 && (
        <section className="mt-4 rounded-md border border-amber-600/20 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-500/20 dark:bg-amber-500/10 dark:text-amber-400">
          {analysis.warnings.map((w, i) => (
            <p key={i}>{w}</p>
          ))}
        </section>
      )}
    </div>
  );
}