"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0F0F14] text-white">

      {/* Soft Gradient Mesh Background */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 left-1/2 h-[900px] w-[900px] -translate-x-1/2 rounded-full bg-gradient-to-br from-purple-500/25 via-pink-500/20 to-blue-500/25 blur-[220px]" />
        <div className="absolute bottom-[-300px] left-[-200px] h-[800px] w-[800px] rounded-full bg-blue-500/15 blur-[200px]" />
        <div className="absolute bottom-[-300px] right-[-200px] h-[800px] w-[800px] rounded-full bg-purple-500/15 blur-[200px]" />
      </div>

      <section className="relative mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center px-6 text-center">

        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8 rounded-full border border-white/20 bg-white/10 px-5 py-2 text-sm backdrop-blur-xl shadow-lg shadow-black/10"
        >
          AI-Powered Fitness Intelligence
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl text-5xl font-semibold leading-tight tracking-tight sm:text-7xl text-white/90"
        >
          Train Smarter.
          <span className="bg-gradient-to-r from-purple-300 via-purple-400 to-purple-500 bg-clip-text text-transparent">
            {" "}
            Perform Stronger.
          </span>
          <br />
          Powered by AI.
        </motion.h1>

        {/* Subtext */}
        <motion.p
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="mt-8 max-w-2xl text-lg text-white/60"
        >
          Personalized workout intelligence, adaptive recovery insights,
          and performance analytics — all powered by next-generation AI.
        </motion.p>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2 }}
          className="mt-12 flex flex-col gap-5 sm:flex-row"
        >
          <Link
            href="#"
            className="rounded-2xl bg-gradient-to-r from-purple-500 to-purple-600 px-10 py-4 font-medium transition-all duration-300 hover:scale-[1.03] hover:shadow-xl hover:shadow-purple-500/30"
          >
            Get Started
          </Link>

          <Link
            href="#"
            className="rounded-2xl border border-white/20 bg-white/10 px-10 py-4 font-medium backdrop-blur-xl transition hover:bg-white/20"
          >
            Sign In
          </Link>
        </motion.div>

        {/* Floating AI Dashboard Preview */}
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.4 }}
          className="relative mt-20 w-full max-w-4xl"
        >
          <div className="rounded-3xl border border-white/20 bg-white/10 backdrop-blur-2xl p-8 shadow-2xl shadow-purple-500/20">

            {/* Top Stats */}
            <div className="grid grid-cols-2 gap-6 sm:grid-cols-3">

              <div className="rounded-2xl bg-white/10 p-5 backdrop-blur-lg border border-white/10">
                <p className="text-sm text-white/60">Workout Score</p>
                <h3 className="mt-2 text-2xl font-semibold text-white/90">87</h3>
              </div>

              <div className="rounded-2xl bg-white/10 p-5 backdrop-blur-lg border border-white/10">
                <p className="text-sm text-white/60">Recovery Index</p>
                <h3 className="mt-2 text-2xl font-semibold text-green-400">Optimal</h3>
              </div>

              <div className="rounded-2xl bg-white/10 p-5 backdrop-blur-lg border border-white/10 col-span-2 sm:col-span-1">
                <p className="text-sm text-white/60">AI Recommendation</p>
                <h3 className="mt-2 text-lg font-medium text-white/90">
                  Increase intensity by 5% this week
                </h3>
              </div>

            </div>

            {/* Progress Bar */}
            <div className="mt-8">
              <p className="mb-2 text-sm text-white/60">Weekly Progress</p>
              <div className="h-3 w-full rounded-full bg-white/10">
                <div className="h-3 w-[70%] rounded-full bg-gradient-to-r from-purple-400 to-purple-600" />
              </div>
            </div>

          </div>
        </motion.div>

      </section>
    </main>
  );
}