import type { Metadata } from "next";
import { Manrope, Fraunces } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-sans",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "VidyaGuru - AI Learning Platform",
  description: "Personalized AI-powered learning platform for genuine learners. विद्या ददाति विनयम् - Knowledge gives humility.",
  keywords: ["learning", "AI", "education", "personalized learning", "VidyaGuru"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${manrope.variable} ${fraunces.variable} app-shell`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
