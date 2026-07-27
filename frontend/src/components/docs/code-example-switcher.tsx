"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { CodeBlock } from "@/components/docs/code-block";

type CodeExample = {
  label: string;
  code: string;
};

export function CodeExampleSwitcher({ examples }: { examples: CodeExample[] }) {
  const [active, setActive] = useState(0);

  return (
    <div>
      <div className="flex gap-1 rounded-t-lg border border-b-0 bg-muted/40 p-1">
        {examples.map((example, i) => (
          <button
            key={example.label}
            onClick={() => setActive(i)}
            className={cn(
              "rounded px-2.5 py-1 text-xs transition-colors",
              active === i
                ? "bg-background font-medium text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {example.label}
          </button>
        ))}
      </div>
      <CodeBlock code={examples[active].code} />
    </div>
  );
}