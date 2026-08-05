import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CodeBlock } from "@/components/docs/code-block";
import { CodeExampleSwitcher } from "@/components/docs/code-example-switcher";

const BASE_URL = "https://api.behaviorpulse.com";

const CURL_EXAMPLE = `curl -X POST ${BASE_URL}/v1/observations/analyze \\
  -H "X-Client-Id: client_xxx" \\
  -H "X-Api-Key: bp_sk_xxx" \\
  -H "Content-Type: application/json" \\
  -d '{
    "observations": [
      {
        "observed_at": "2026-07-12T12:14:00Z",
        "subject": { "type": "animal", "label": "hummingbird" },
        "source": { "type": "camera", "id": "camera_04" },
        "confidence": 0.88,
        "metadata": { "location": "north_fence" }
      }
    ],
    "options": {
      "timezone": "America/Los_Angeles",
      "lookback_days": 30
    }
  }'`;

const PYTHON_EXAMPLE = `import requests

response = requests.post(
    "${BASE_URL}/v1/observations/analyze",
    headers={
        "X-Client-Id": "client_xxx",
        "X-Api-Key": "bp_sk_xxx",
    },
    json={
        "observations": [
            {
                "observed_at": "2026-07-12T12:14:00Z",
                "subject": {"type": "animal", "label": "hummingbird"},
                "source": {"type": "camera", "id": "camera_04"},
                "confidence": 0.88,
                "metadata": {"location": "north_fence"},
            }
        ],
        "options": {
            "timezone": "America/Los_Angeles",
            "lookback_days": 30,
        },
    },
)

print(response.json())`;

const JAVASCRIPT_EXAMPLE = `const response = await fetch("${BASE_URL}/v1/observations/analyze", {
  method: "POST",
  headers: {
    "X-Client-Id": "client_xxx",
    "X-Api-Key": "bp_sk_xxx",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    observations: [
      {
        observed_at: "2026-07-12T12:14:00Z",
        subject: { type: "animal", label: "hummingbird" },
        source: { type: "camera", id: "camera_04" },
        confidence: 0.88,
        metadata: { location: "north_fence" },
      },
    ],
    options: {
      timezone: "America/Los_Angeles",
      lookback_days: 30,
    },
  }),
});

const data = await response.json();`;

const REQUEST_SHAPE = `{
  "observations": [
    {
      "observed_at": "2026-07-12T12:14:00Z",
      "subject": { "type": "animal", "label": "hummingbird" },
      "source": { "type": "camera", "id": "camera_04" },
      "confidence": 0.88,
      "metadata": { "location": "north_fence" }
    }
  ],
  "options": {
    "timezone": "America/Los_Angeles",
    "date_from": "2026-06-15T00:00:00Z",
    "date_to": "2026-07-15T23:59:59Z",
    "lookback_days": 30
  }
}`;

const RESPONSE_SHAPE = `{
  "analysis_id": "ana_123",
  "status": "completed",
  "summary": "Birds dominate activity (92.9%)...",
  "prediction": "Next likely window: Saturday, 6-8 AM",
  "computed_confidence": 0.87,
  "pattern_table": [
    { "metric": "total_observations", "value": "47", "support": "..." }
  ],
  "computed_metrics": {
    "total_observations": 47,
    "average_confidence": 0.82,
    "top_subjects": [
      { "subject_label": "hummingbird", "count": 30, "percentage": 63.8 }
    ]
  },
  "recommendations": ["..."],
  "warnings": ["Predictions are pattern estimates, not guarantees."]
}`;

export default function DocsPage() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-semibold">Docs</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        How to authenticate and call the BehaviorPulse API.
      </p>

      <section className="mt-8">
        <h2 className="text-lg font-medium">Getting started</h2>
        <ol className="mt-3 flex flex-col gap-2 text-sm text-muted-foreground">
          <li>1. Create an app under Apps.</li>
          <li>2. Grant it the <code className="font-mono">observations.analyze</code> scope from the app&apos;s Settings tab.</li>
          <li>3. Generate an API key from the app&apos;s API Keys tab.</li>
          <li>4. Call the endpoint below using that key.</li>
        </ol>
        <Button className="mt-4" size="sm" asChild>
          <Link href="/dashboard/apps">Go to Apps</Link>
        </Button>
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-medium">Authentication</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Every request needs both headers. Missing or invalid credentials return a
          <code className="mx-1 font-mono">401</code> with an <code className="font-mono">error</code> field
          you can match on.
        </p>
        <div className="mt-3">
          <CodeBlock
            label="Headers"
            code={`X-Client-Id: client_xxx\nX-Api-Key: bp_sk_xxx`}
          />
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-medium">POST /v1/observations/analyze</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Accepts any mix of subjects in one request — wildlife, vehicles, people,
          whatever a camera or sensor detected. Deterministic analytics are computed
          first; the LLM only explains the already-computed facts.
        </p>

        <p className="mt-4 text-sm font-medium">Request body</p>
        <div className="mt-2">
          <CodeBlock code={REQUEST_SHAPE} />
        </div>

        <p className="mt-4 text-sm font-medium">Response body</p>
        <div className="mt-2">
          <CodeBlock code={RESPONSE_SHAPE} />
        </div>

        <p className="mt-4 text-sm font-medium">Example request</p>
        <div className="mt-2">
          <CodeExampleSwitcher
            examples={[
              { label: "cURL", code: CURL_EXAMPLE },
              { label: "Python", code: PYTHON_EXAMPLE },
              { label: "JavaScript", code: JAVASCRIPT_EXAMPLE },
            ]}
          />
        </div>
      </section>
    </div>
  );
}