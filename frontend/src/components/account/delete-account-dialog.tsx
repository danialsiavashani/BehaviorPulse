"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { deleteAccount } from "@/lib/auth";
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

export function DeleteAccountDialog({
  email,
  open,
  onOpenChange,
}: {
  email: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);

  const schema = z.object({
    confirmEmail: z.string().refine((val) => val === email, {
      message: "Doesn't match your email",
    }),
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<{ confirmEmail: string }>({
    resolver: zodResolver(schema),
    defaultValues: { confirmEmail: "" },
  });

  async function onSubmit() {
    setFormError(null);
    const result = await deleteAccount();

    if (result?.error) {
      setFormError(result.error);
      return;
    }

    reset();
    onOpenChange(false);
    router.push("/account-deleted");
  }

  function handleOpenChange(next: boolean) {
    if (!next) reset();
    onOpenChange(next);
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete your account</DialogTitle>
          <DialogDescription>This is permanent and cannot be undone.</DialogDescription>
        </DialogHeader>

        <div className="rounded-md border bg-muted/40 p-3 text-sm text-muted-foreground">
          <p className="font-medium text-foreground">This will permanently delete:</p>
          <ul className="mt-1.5 list-disc pl-4">
            <li>Your account and profile</li>
            <li>Every app you&apos;ve created, and their client IDs</li>
            <li>All API keys and service scopes</li>
            <li>All observation analysis history</li>
          </ul>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <FieldGroup>
            <Field data-invalid={!!errors.confirmEmail}>
              <FieldLabel htmlFor="confirmEmail">
                Type <span className="font-mono">{email}</span> to confirm
              </FieldLabel>
              <Input
                id="confirmEmail"
                autoComplete="off"
                aria-invalid={!!errors.confirmEmail}
                {...register("confirmEmail")}
              />
              <FieldError errors={errors.confirmEmail ? [errors.confirmEmail] : undefined} />
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
              {isSubmitting ? "Deleting..." : "Delete account"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}