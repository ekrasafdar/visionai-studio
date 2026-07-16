"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Zap, Eye, BarChart3 } from "lucide-react";

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto px-6 text-center pt-16 pb-24">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="inline-flex items-center gap-2 text-xs font-mono text-cyan border border-cyan/30 bg-cyan/5 px-4 py-2 rounded-full mb-8"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-cyan animate-pulse" /> MULTI-MODEL · TRANSFER LEARNING
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="font-display font-bold text-5xl md:text-7xl leading-tight"
      >
        See what your{" "}
        <span className="bg-gradient-to-r from-electric via-glow to-cyan bg-clip-text text-transparent">
          images
        </span>{" "}
        are really made of.
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="max-w-xl mx-auto mt-6 text-slate-400"
      >
        Upload an image and get real-time predictions from ResNet50,
        EfficientNet-B3, or MobileNetV3 — complete with confidence scores,
        Grad-CAM explainability, and full prediction history.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex gap-4 justify-center mt-10"
      >
        <Link
          href="/upload"
          className="flex items-center gap-2 px-7 py-3.5 rounded-xl font-semibold text-sm bg-gradient-to-r from-electric to-glow shadow-lg shadow-glow/30 hover:-translate-y-0.5 transition"
        >
          Upload an image <ArrowRight size={16} />
        </Link>
        <Link
          href="/dashboard"
          className="px-7 py-3.5 rounded-xl font-semibold text-sm glass hover:border-white/25 transition"
        >
          View dashboard
        </Link>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-24 text-left">
        <Feature icon={<Zap size={20} />} title="Three architectures" desc="Switch between ResNet50, EfficientNet-B3, and MobileNetV3 fine-tuned via transfer learning." />
        <Feature icon={<Eye size={20} />} title="Real Grad-CAM" desc="Every prediction ships with a genuine class-activation heatmap showing what the model attended to." />
        <Feature icon={<BarChart3 size={20} />} title="Full analytics" desc="Accuracy, precision, recall, F1, confusion matrices, and per-model comparison, backed by Postgres." />
      </div>
    </div>
  );
}

function Feature({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="glass rounded-2xl p-6 hover:border-glow/40 transition">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-electric/20 to-glow/20 border border-glow/25 flex items-center justify-center mb-4 text-cyan">
        {icon}
      </div>
      <h3 className="font-display font-semibold mb-2">{title}</h3>
      <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
    </div>
  );
}
