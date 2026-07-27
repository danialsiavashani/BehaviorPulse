"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { changeEmail } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldGroup, FieldLabel, FieldError } from "@/components/ui/field";

const schema = z.object({
  currentPassword: z.string().min(1, "Current password is required"),
  newEmail: z.string().min(1, "Email is required").email("Enter a valid email"),
});

type FormValues = z.infer<typeof schema>;

export function ChangeEmailForm({ currentEmail }: { currentEmail: string }) {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setFormError(null);
    setSuccess(false);

    const result = await changeEmail(values.currentPassword, values.newEmail);

    if (result?.error) {
      setFormError(result.error);
      return;
    }

    setSuccess(true);
    reset();
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="max-w-sm">
      <FieldGroup>
        <p className="text-sm text-muted-foreground">
          Current email: <span className="font-medium text-foreground">{currentEmail}</span>
        </p>

        <Field data-invalid={!!errors.newEmail}>
          <FieldLabel htmlFor="newEmail">New email</FieldLabel>
          <Input
            id="newEmail"
            type="email"
            autoComplete="email"
            aria-invalid={!!errors.newEmail}
            {...register("newEmail")}
          />
          <FieldError errors={errors.newEmail ? [errors.newEmail] : undefined} />
        </Field>

        <Field data-invalid={!!errors.currentPassword}>
          <FieldLabel htmlFor="currentPassword">Current password</FieldLabel>
          <Input
            id="currentPassword"
            type="password"
            autoComplete="current-password"
            aria-invalid={!!errors.currentPassword}
            {...register("currentPassword")}
          />
          <FieldError errors={errors.currentPassword ? [errors.currentPassword] : undefined} />
        </Field>

        {formError && (
          <p role="alert" className="text-sm font-normal text-destructive">
            {formError}
          </p>
        )}

        {success && (
          <p className="text-sm font-normal text-emerald-600 dark:text-emerald-500">
            Email updated. Every other device has been signed out.
          </p>
        )}

        <Field>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Updating..." : "Update email"}
          </Button>
        </Field>
      </FieldGroup>
    </form>
  );
}