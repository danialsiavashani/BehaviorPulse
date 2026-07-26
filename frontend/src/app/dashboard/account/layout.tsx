import { AccountTabs } from "@/components/account/account-tabs";

export default function AccountLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Account</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Manage your BehaviorPulse account.
      </p>

      <AccountTabs />

      <div className="mt-4">{children}</div>
    </div>
  );
}