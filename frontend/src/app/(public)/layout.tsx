import Link from "next/link";

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen bg-[#0E0E12] text-white overflow-x-hidden">
      
      {/* Floating Navbar */}
      <header className="fixed top-6 left-1/2 z-50 w-full max-w-6xl -translate-x-1/2 px-6">
        <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-6 py-3 backdrop-blur-xl shadow-lg shadow-black/20">
          
          {/* Logo */}
          <Link
            href="/"
            className="text-lg font-semibold tracking-tight"
          >
            Fit<span className="text-purple-500">AI</span>
          </Link>

          {/* Nav Links */}
          <nav className="hidden items-center gap-8 text-sm text-white/70 md:flex">
            <Link href="#" className="hover:text-white transition-colors">
              Features
            </Link>
            <Link href="#" className="hover:text-white transition-colors">
              Pricing
            </Link>
            <Link href="#" className="hover:text-white transition-colors">
              About
            </Link>
          </nav>

          {/* CTA */}
          <Link
            href="#"
            className="rounded-xl bg-purple-600 px-5 py-2 text-sm font-medium transition hover:bg-purple-500 hover:shadow-lg hover:shadow-purple-600/30"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="pt-32">{children}</main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-10 text-center text-sm text-white/50">
        © {new Date().getFullYear()} FitAI. All rights reserved.
      </footer>
    </div>
  );
}