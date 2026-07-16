import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VisionAI Studio",
  description: "AI-powered image classification platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-body min-h-screen">
        <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-10 py-4 glass">
          <a href="/" className="font-display font-semibold text-lg flex items-center gap-2">
            <span className="w-6 h-6 rounded-lg bg-gradient-to-br from-electric to-glow inline-block" />
            VisionAI Studio
          </a>
          <div className="flex gap-6 text-sm text-slate-300">
            <a href="/upload" className="hover:text-white">Classify</a>
            <a href="/dashboard" className="hover:text-white">Dashboard</a>
            <a href="/login" className="hover:text-white">Login</a>
          </div>
        </nav>
        <main className="pt-20">{children}</main>
      </body>
    </html>
  );
}
