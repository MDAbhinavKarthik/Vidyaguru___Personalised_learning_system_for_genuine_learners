"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { GraduationCap, Mail, Lock, User, Eye, EyeOff, ArrowRight, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/lib/store";

const registerSchema = z.object({
  full_name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number")
    .regex(/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/, "Password must contain at least one special character"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

const passwordRequirements = [
  { regex: /.{8,}/, label: "At least 8 characters" },
  { regex: /[A-Z]/, label: "One uppercase letter" },
  { regex: /[a-z]/, label: "One lowercase letter" },
  { regex: /[0-9]/, label: "One number" },
  { regex: /[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/, label: "One special character" },
];

export default function RegisterPage() {
  const router = useRouter();
  const { register: registerUser } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const password = watch("password", "");

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setError(null);
      await registerUser({
        full_name: data.full_name,
        email: data.email,
        password: data.password,
      });
      router.push("/dashboard");
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      let errorMessage = "Registration failed. Please try again.";

      if (typeof detail === "string") {
        errorMessage = detail;
      } else if (detail?.message) {
        const issues = Array.isArray(detail.issues) ? ` (${detail.issues.join(", ")})` : "";
        errorMessage = `${detail.message}${issues}`;
      } else if (typeof err?.message === "string") {
        errorMessage = err.message;
      } else if (typeof err === "string") {
        errorMessage = err;
      }

      setError(errorMessage);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-sky-400/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-amber-400/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }}></div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-sky-700 via-cyan-700 to-amber-500 shadow-lg shadow-sky-700/40">
              <GraduationCap className="h-8 w-8 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-sky-700 to-cyan-700 bg-clip-text text-transparent">
                VidyaGuru
              </h1>
              <p className="text-xs text-slate-500">विद्यागुरु</p>
            </div>
          </Link>
        </div>

        {/* Form Card */}
        <div className="relative">
          {/* Gradient border */}
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-sky-700/35 via-cyan-700/25 to-amber-500/30 p-[1px]">
            <div className="absolute inset-[1px] rounded-[15px] bg-white/85 backdrop-blur-xl dark:bg-slate-900/75"></div>
          </div>

          <div className="relative p-8 rounded-2xl">
            <div className="space-y-1 mb-6">
              <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-100 text-center">Create Account</h2>
              <p className="text-center text-slate-600 dark:text-slate-400 text-sm">
                Begin your journey of genuine learning
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start gap-3"
                >
                  <div className="w-1 h-1 rounded-full bg-red-400 mt-2 flex-shrink-0"></div>
                  <span>{String(error)}</span>
                </motion.div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-800 dark:text-slate-200">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <Input
                    {...register("full_name")}
                    placeholder="John Doe"
                    className="pl-10 bg-white/70 border border-slate-200 text-slate-900 placeholder:text-slate-400 focus:border-sky-600/50 focus:bg-white dark:bg-slate-900/45 dark:border-slate-700 dark:text-slate-100"
                  />
                </div>
                {errors.full_name && (
                  <p className="text-xs text-red-400">{errors.full_name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-800 dark:text-slate-200">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <Input
                    {...register("email")}
                    type="email"
                    placeholder="you@example.com"
                    className="pl-10 bg-white/70 border border-slate-200 text-slate-900 placeholder:text-slate-400 focus:border-sky-600/50 focus:bg-white dark:bg-slate-900/45 dark:border-slate-700 dark:text-slate-100"
                  />
                </div>
                {errors.email && (
                  <p className="text-xs text-red-400">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-800 dark:text-slate-200">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <Input
                    {...register("password")}
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    className="pl-10 pr-10 bg-white/70 border border-slate-200 text-slate-900 placeholder:text-slate-400 focus:border-sky-600/50 focus:bg-white dark:bg-slate-900/45 dark:border-slate-700 dark:text-slate-100"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>

                {/* Password Requirements */}
                <div className="mt-3 space-y-2 p-3 rounded-lg bg-white/70 border border-slate-200 dark:bg-slate-900/35 dark:border-slate-700">
                  {passwordRequirements.map((req, index) => {
                    const isMet = req.regex.test(password);
                    return (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={`flex items-center gap-2 text-xs transition-colors ${
                          isMet ? "text-emerald-600 dark:text-emerald-400" : "text-slate-500"
                        }`}
                      >
                        <Check className={`h-3 w-3 flex-shrink-0 ${isMet ? "opacity-100" : "opacity-30"}`} />
                        {req.label}
                      </motion.div>
                    );
                  })}
                </div>

                {errors.password && (
                  <p className="text-xs text-red-400">{errors.password.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-800 dark:text-slate-200">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <Input
                    {...register("confirmPassword")}
                    type="password"
                    placeholder="••••••••"
                    className="pl-10 bg-white/70 border border-slate-200 text-slate-900 placeholder:text-slate-400 focus:border-sky-600/50 focus:bg-white dark:bg-slate-900/45 dark:border-slate-700 dark:text-slate-100"
                  />
                </div>
                {errors.confirmPassword && (
                  <p className="text-xs text-red-400">{errors.confirmPassword.message}</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full mt-6 h-11 bg-gradient-to-r from-sky-700 via-cyan-700 to-amber-500 hover:from-sky-800 hover:via-cyan-800 hover:to-amber-600 text-white font-semibold shadow-lg shadow-sky-700/40 transition-all group"
                loading={isSubmitting}
              >
                Create Account
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>

              <p className="text-xs text-center text-slate-600 dark:text-slate-400 mt-4">
                By signing up, you agree to our{" "}
                <Link href="/terms" className="text-sky-700 hover:text-sky-800 dark:text-sky-400 dark:hover:text-sky-300 transition-colors">
                  Terms
                </Link>
                {" "}and{" "}
                <Link href="/privacy" className="text-sky-700 hover:text-sky-800 dark:text-sky-400 dark:hover:text-sky-300 transition-colors">
                  Privacy Policy
                </Link>
              </p>
            </form>

            <div className="mt-6 relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10" />
              </div>
              <div className="relative flex justify-center">
                <span className="bg-white/80 dark:bg-slate-900/70 px-2 text-xs text-slate-500">or</span>
              </div>
            </div>

            <p className="mt-6 text-center text-sm">
              Already have an account?{" "}
              <Link href="/login" className="text-sky-700 hover:text-sky-800 dark:text-sky-400 dark:hover:text-sky-300 font-semibold transition-colors">
                Sign in here
              </Link>
            </p>
          </div>
        </div>

        <p className="mt-8 text-center text-xs text-slate-500">
          <span className="text-sky-700 dark:text-sky-300">विद्या ददाति विनयम्</span> - Knowledge gives humility
        </p>
      </motion.div>
    </div>
  );
}
