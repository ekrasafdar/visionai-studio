"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.login(email, password);
      router.push("/upload");
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <div className="max-w-sm mx-auto px-6 py-16">
      <h1 className="font-display text-2xl font-bold mb-6">Log in</h1>
      <form onSubmit={submit} className="space-y-4">
        <Input label="Email" type="email" value={email} onChange={setEmail} />
        <Input label="Password" type="password" value={password} onChange={setPassword} />
        {error && <p className="text-sm text-red-400">{error}</p>}
        <button className="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-electric to-glow">Log in</button>
      </form>
      <p className="text-sm text-slate-500 mt-4">
        No account? <a href="/register" className="text-cyan">Register</a>
      </p>
    </div>
  );
}

function Input({ label, type, value, onChange }: { label: string; type: string; value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <label className="text-xs text-slate-400 block mb-1">{label}</label>
      <input
        type={type}
        required
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-bg2 border border-white/10 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-cyan/50"
      />
    </div>
  );
}
