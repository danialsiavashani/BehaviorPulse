"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Check, Copy } from "lucide-react";

import { createApiKey } from "@/lib/api-keys";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldGroup, FieldLabel, FieldError } from "@/components/ui/field";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const schema = z.object({
  name: z.string().min(1, "Name is required").max(255),
});

type FormValues = z.infer<typeof schema>;

type CreatedKey = { raw_key: string; name: string; key_prefix: string };

export function CreateApiKeyDialog({ clientAppId }: { clientAppId: string }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [createdKey, setCreatedKey] = useState<CreatedKey | null>(null);
  const [copied, setCopied] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: "" },
  });

  async function onSubmit(values: FormValues) {
    setFormError(null);
    const result = await createApiKey(clientAppId, values.name);

    if (result?.error) {
      setFormError(result.error);
      return;
    }

    setCreatedKey(result.data);
  }

  async function handleCopy() {
    if (!createdKey) return;
    await navigator.clipboard.writeText(createdKey.raw_key);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  function handleDone() {
    setOpen(false);
    setCreatedKey(null);
    setCopied(false);
    reset();
    router.refresh();
  }

  function handleOpenChange(next: boolean) {
    if (!next && createdKey) {
      handleDone();
      return;
    }
    setOpen(next);
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <Button onClick={() => setOpen(true)}>
        <Plus />
        Create key
      </Button>
      <DialogContent>
        {createdKey ? (
          <>
            <DialogHeader>
              <DialogTitle>Key created</DialogTitle>
              <DialogDescription>
                Copy this key now — it won&apos;t be shown again.
              </DialogDescription>
            </DialogHeader>

            <div className="flex min-w-0 items-center gap-2 rounded-md border bg-muted/40 p-3">
              <code className="min-w-0 flex-1 truncate font-mono text-xs">
                {createdKey.raw_key}
              </code>
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={handleCopy}
                className="shrink-0"
              >
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>

            <DialogFooter>
              <Button onClick={handleDone}>Done</Button>
            </DialogFooter>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>Create API key</DialogTitle>
              <DialogDescription>
                Give the key a name that identifies where it&apos;s used.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <FieldGroup>
                <Field data-invalid={!!errors.name}>
                  <FieldLabel htmlFor="key-name">Name</FieldLabel>
                  <Input
                    id="key-name"
                    placeholder="production-server"
                    aria-invalid={!!errors.name}
                    {...register("name")}
                  />
                  <FieldError errors={errors.name ? [errors.name] : undefined} />
                </Field>

                {formError && (
                  <p role="alert" className="text-sm font-normal text-destructive">
                    {formError}
                  </p>
                )}
              </FieldGroup>

              <DialogFooter>
                <DialogClose asChild>
                  <Button type="button" variant="outline">
                    Cancel
                  </Button>
                </DialogClose>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Creating..." : "Create key"}
                </Button>
              </DialogFooter>
            </form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}