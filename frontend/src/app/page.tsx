import { Navbar } from "@/components/navbar";
import { HeroSection } from "@/components/hero-section";

export default function HomePage() {
  return (
    <div className="flex h-dvh flex-col overflow-hidden">
      <Navbar />
      <main className="flex flex-1 items-center overflow-hidden">
        <HeroSection />
      </main>
    </div>
  );
}