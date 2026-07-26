"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { deleteApp } from "@/lib/apps";
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

type AppToDelete = { id: string; name: string };

export function DeleteAppDialog({
  app,
  open,
  onOpenChange,
  redirectTo,
}: {
  app: AppToDelete | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  redirectTo?: string;
}) {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);

  const schema = z.object({
    confirmName: z.string().refine((val) => val === app?.name, {
      message: "Doesn't match the app name",
    }),
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<{ confirmName: string }>({
    resolver: zodResolver(schema),
    defaultValues: { confirmName: "" },
  });

  async function onSubmit() {
    if (!app) return;
    setFormError(null);
    const result = await deleteApp(app.id);

    if (result?.error) {
      setFormError(result.error);
      return;
    }

    reset();
    onOpenChange(false);

    if (redirectTo) {
      router.push(redirectTo);
    } else {
      router.refresh();
    }
  }

  function handleOpenChange(next: boolean) {
    if (!next) reset();
    onOpenChange(next);
  }

  if (!app) return null;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete {app.name}</DialogTitle>
          <DialogDescription>
            This is permanent and cannot be undone.
          </DialogDescription>
        </DialogHeader>

        <div className="rounded-md border bg-muted/40 p-3 text-sm text-muted-foreground">
          <p className="font-medium text-foreground">This will permanently delete:</p>
          <ul className="mt-1.5 list-disc pl-4">
            <li>The app &quot;{app.name}&quot; and its client ID</li>
            <li>All API keys created for this app</li>
            <li>All service scopes granted to this app</li>
            <li>All observation analysis history for this app</li>
          </ul>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <FieldGroup>
            <Field data-invalid={!!errors.confirmName}>
              <FieldLabel htmlFor="confirmName">
                Type <span className="font-mono">{app.name}</span> to confirm
              </FieldLabel>
              <Input
                id="confirmName"
                autoComplete="off"
                aria-invalid={!!errors.confirmName}
                {...register("confirmName")}
              />
              <FieldError errors={errors.confirmName ? [errors.confirmName] : undefined} />
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
            <Button type="submit" variant="destructive" disabled={isSubmitting}>
              {isSubmitting ? "Deleting..." : "Delete app"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}