import { NextResponse } from "next/server";
import { apiFetch } from "@/lib/api";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ analysis_id: string }> }
) {
  const { analysis_id } = await params;

  const res = await apiFetch(`/v1/analyses/${analysis_id}/export`);

  if (!res.ok || !res.body) {
    return NextResponse.json(
      { error: "Could not export this analysis." },
      { status: res.status || 500 }
    );
  }

  return new NextResponse(res.body, {
    status: 200,
    headers: {
      "Content-Type":
        res.headers.get("content-type") ??
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "Content-Disposition":
        res.headers.get("content-disposition") ??
        `attachment; filename="analysis_${analysis_id}.xlsx"`,
    },
  });
}