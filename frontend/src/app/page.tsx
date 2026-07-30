import { Navbar } from "@/components/navbar";
import { HeroSection } from "@/components/hero-section";

export default function HomePage() {
  return (
    <div className="flex min-h-dvh flex-col md:h-dvh md:overflow-hidden">
      <Navbar />
      <main className="flex flex-1 items-center md:overflow-hidden">
        <HeroSection />
      </main>
    </div>
  );
}