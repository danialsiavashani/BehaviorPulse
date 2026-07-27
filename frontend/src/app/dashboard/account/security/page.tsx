import { getCurrentUser } from "@/lib/auth";
import { ChangeEmailForm } from "@/components/account/change-email-form";
import { ChangePasswordForm } from "@/components/account/change-password-form";

export default async function SecuritySettingsPage() {
  const user = await getCurrentUser();

  return (
    <div className="flex flex-col gap-6">
      <div className="max-w-md rounded-lg border p-5">
        <h2 className="text-sm font-medium">Change email</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Update the email address used to sign in.
        </p>
        <div className="mt-4 border-t pt-4">
          <ChangeEmailForm currentEmail={user?.email ?? ""} />
        </div>
      </div>

      <div className="max-w-md rounded-lg border p-5">
        <h2 className="text-sm font-medium">Change password</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose a strong password you don't use elsewhere.
        </p>
        <div className="mt-4 border-t pt-4">
          <ChangePasswordForm />
        </div>
      </div>
    </div>
  );
}