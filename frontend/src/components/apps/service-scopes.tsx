"use client";

import { useState, useTransition } from "react";
import { Switch } from "@/components/ui/switch";
import { setScope } from "@/lib/apps";

type Service = {
  service_key: string;
  name: string;
};

type Scope = {
  service_key: string;
  enabled: boolean;
};

export function ServiceScopes({
  clientAppId,
  services,
  initialScopes,
}: {
  clientAppId: string;
  services: Service[];
  initialScopes: Scope[];
}) {
  const [scopeState, setScopeState] = useState<Record<string, boolean>>(() => {
    const map: Record<string, boolean> = {};
    for (const s of initialScopes) map[s.service_key] = s.enabled;
    return map;
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isPending, startTransition] = useTransition();

  function handleToggle(serviceKey: string, next: boolean) {
    setScopeState((prev) => ({ ...prev, [serviceKey]: next }));
    setErrors((prev) => ({ ...prev, [serviceKey]: "" }));

    startTransition(async () => {
      const result = await setScope(clientAppId, serviceKey, next);
      if (result?.error) {
        setScopeState((prev) => ({ ...prev, [serviceKey]: !next }));
        setErrors((prev) => ({ ...prev, [serviceKey]: result.error as string }));
      }
    });
  }

  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm font-medium">Services</p>
      <p className="mt-1 text-xs text-muted-foreground">
        Enable services this app is allowed to call.
      </p>

      <div className="mt-4 flex flex-col gap-3">
        {services.map((service) => (
          <div key={service.service_key} className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium">{service.name}</p>
              <p className="font-mono text-xs text-muted-foreground">{service.service_key}</p>
              {errors[service.service_key] && (
                <p className="text-xs text-destructive">{errors[service.service_key]}</p>
              )}
            </div>
            <Switch
              checked={scopeState[service.service_key] ?? false}
              onCheckedChange={(checked) => handleToggle(service.service_key, checked)}
              disabled={isPending}
            />
          </div>
        ))}
      </div>
    </div>
  );
}