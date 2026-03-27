"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BookOpen,
  Brain,
  GraduationCap,
  ShieldCheck,
  Sparkles,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  {
    icon: Brain,
    title: "AI Mentor",
    description:
      "Guidance that asks the right questions so learners build understanding.",
    delay: 0,
  },
  {
    icon: BookOpen,
    title: "Adaptive Paths",
    description:
      "Learning plans adjust to pace, goals, and current skill level.",
    delay: 0.1,
  },
  {
    icon: Zap,
    title: "Live Progress",
    description:
      "Clear milestones, streaks, and analytics to keep momentum stable.",
    delay: 0.2,
  },
  {
    icon: ShieldCheck,
    title: "Genuine Learning",
    description:
      "Built to reward depth, reflection, and long-term retention.",
    delay: 0.3,
  },
];

const stats = [
  { number: "10K+", label: "Learners" },
  { number: "500+", label: "Courses" },
  { number: "4.9", label: "Average Rating" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen overflow-hidden">
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/60 bg-background/85 backdrop-blur-xl">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sky-700 to-cyan-600 shadow-md shadow-sky-700/30">
              <GraduationCap className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">VidyaGuru</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button variant="gradient">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      <main className="px-4 pt-36 pb-16 sm:px-6 lg:px-8">
        <section className="mx-auto w-full max-w-6xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="space-y-6"
          >
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-2 text-sm text-primary">
              <Sparkles className="h-4 w-4" />
              AI-powered learning platform
            </div>

            <h1 className="text-5xl font-black tracking-tight sm:text-6xl lg:text-7xl">
              <span className="block">Learn with</span>
              <span className="block gradient-text">Genuine Understanding</span>
            </h1>

            <p className="mx-auto max-w-3xl text-lg leading-relaxed text-muted-foreground sm:text-xl">
              A clean, focused learning experience with adaptive paths, AI
              mentoring, and progress tools designed for real mastery.
            </p>

            <div className="flex flex-col items-center justify-center gap-4 pt-3 sm:flex-row">
              <Link href="/register" className="w-full sm:w-auto">
                <Button size="xl" variant="gradient" className="w-full group">
                  Start Learning
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <Link href="/login" className="w-full sm:w-auto">
                <Button size="xl" variant="outline" className="w-full">
                  Go to Login
                </Button>
              </Link>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="mx-auto mt-14 grid max-w-3xl grid-cols-1 gap-4 sm:grid-cols-3"
          >
            {stats.map((stat) => (
              <div key={stat.label} className="soft-card rounded-2xl p-5">
                <p className="text-3xl font-bold gradient-text">{stat.number}</p>
                <p className="mt-1 text-sm text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </motion.div>
        </section>

        <section className="mx-auto mt-20 w-full max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="text-4xl font-bold sm:text-5xl">Everything for your success</h2>
            <p className="mx-auto mt-3 max-w-3xl text-lg text-muted-foreground">
              Focused features that keep your learning journey clear,
              consistent, and motivating.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: feature.delay }}
                  viewport={{ once: true }}
                  className="soft-card rounded-2xl p-6"
                >
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-semibold">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </section>

        <section className="mx-auto mt-20 w-full max-w-4xl">
          <div className="soft-card rounded-3xl p-10 text-center sm:p-14">
            <h2 className="text-4xl font-bold sm:text-5xl">
              Ready to transform your learning journey?
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
              Join learners building deep knowledge with consistency, clarity,
              and guided practice.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
              <Link href="/register" className="w-full sm:w-auto">
                <Button size="xl" variant="gradient" className="w-full">
                  Start Free
                  <Sparkles className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="/login" className="w-full sm:w-auto">
                <Button size="xl" variant="outline" className="w-full">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-border/60 px-4 py-14 sm:px-6 lg:px-8">
        <div className="mx-auto grid w-full max-w-6xl grid-cols-1 gap-10 md:grid-cols-4">
          <div>
            <div className="mb-3 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-sky-700 to-cyan-600">
                <GraduationCap className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-bold">VidyaGuru</span>
            </div>
            <p className="text-sm text-muted-foreground">
              AI-powered learning for genuine understanding.
            </p>
          </div>

          <div>
            <h4 className="mb-3 font-semibold">Product</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  Learning Paths
                </Link>
              </li>
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  Mentor
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="mb-3 font-semibold">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  About
                </Link>
              </li>
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  Support
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="mb-3 font-semibold">Trust</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  Privacy
                </Link>
              </li>
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  Terms
                </Link>
              </li>
              <li>
                <Link href="#" className="transition-colors hover:text-primary">
                  Security
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <p className="mx-auto mt-10 w-full max-w-6xl border-t border-border/60 pt-6 text-center text-sm text-muted-foreground">
          Copyright 2026 VidyaGuru. Built for genuine learners.
        </p>
      </footer>
    </div>
  );
}
