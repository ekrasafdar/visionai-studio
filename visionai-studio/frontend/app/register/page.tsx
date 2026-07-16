"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const router = useRouter();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.register(email, password, fullName);
      setDone(true);
      setTimeout(() => router.push("/login"), 1200);
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <div className="max-w-sm mx-auto px-6 py-16">
      <h1 className="font-display text-2xl font-bold mb-6">Create account</h1>
      {done ? (
        <p className="text-sm text-cyan">Account created — redirecting to login…</p>
      ) : (
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Full name</label>
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full bg-bg2 border border-white/10 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-cyan/50" />
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="w-full bg-bg2 border border-white/10 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-cyan/50" />
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Password (min 8 chars)</label>
            <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-bg2 border border-white/10 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-cyan/50" />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button className="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-electric to-glow">Create account</button>
        </form>
      )}
      <p className="text-sm text-slate-500 mt-4">
        Already have an account? <a href="/login" className="text-cyan">Log in</a>
      </p>
    </div>
  );
}
