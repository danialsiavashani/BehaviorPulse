import Link from "next/link";
import { Navbar } from "@/components/navbar";

export default function AccountDeletedPage() {
  return (
    <div className="flex min-h-svh flex-col">
      <Navbar />

      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <h1 className="text-xl font-semibold">Your account has been deleted</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Everything tied to it — your apps, API keys, and analysis history — has been
            permanently removed.
          </p>
          <Link
            href="/signup"
            className="mt-6 inline-block text-sm text-primary underline-offset-4 hover:underline"
          >
            Create a new account
          </Link>
        </div>
      </div>
    </div>
  );
}