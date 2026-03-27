"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/lib/store";
import { progressAPI } from "@/services/api";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  LayoutDashboard,
  BookOpen,
  ClipboardCheck,
  Lightbulb,
  BarChart3,
  MessageCircle,
  Settings,
  LogOut,
  GraduationCap,
  Flame,
  Trophy,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Learning", href: "/learn", icon: BookOpen },
  { name: "Tasks", href: "/tasks", icon: ClipboardCheck },
  { name: "Idea Journal", href: "/journal", icon: Lightbulb },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "AI Mentor", href: "/mentor", icon: MessageCircle },
];

const bottomNav = [
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [stats, setStats] = useState<any>({ current_streak: 0, current_level: 1 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const overview = await progressAPI.getOverview();
        setStats({
          current_streak: overview?.current_streak || 0,
          current_level: overview?.current_level || 1,
        });
      } catch (err) {
        console.error("Error fetching user stats:", err);
      }
    };
    fetchStats();
  }, []);

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border/70 bg-card/90 backdrop-blur-xl">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b border-border/70 px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-sky-700 to-cyan-600 shadow-md shadow-cyan-700/30">
            <GraduationCap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-sky-700 to-cyan-600 bg-clip-text text-transparent">
              VidyaGuru
            </h1>
            <p className="text-[10px] text-muted-foreground -mt-0.5">विद्यागुरु</p>
          </div>
        </div>

        {/* User Section */}
        <div className="border-b border-border/70 p-4">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10">
              <AvatarImage src={user?.avatar_url} />
              <AvatarFallback>{user?.full_name ? getInitials(user.full_name) : "U"}</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name || "User"}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="mt-3 flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1 text-orange-600">
              <Flame className="h-3.5 w-3.5" />
              <span className="font-medium">{stats.current_streak} day streak</span>
            </div>
            <div className="flex items-center gap-1 text-amber-600">
              <Trophy className="h-3.5 w-3.5" />
              <span className="font-medium">Level {stats.current_level}</span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <ScrollArea className="flex-1 py-4">
          <nav className="space-y-1 px-3">
            {navigation.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                    isActive
                      ? "bg-gradient-to-r from-sky-700/10 to-cyan-600/10 text-sky-700 dark:text-sky-300"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <item.icon className={cn("h-5 w-5", isActive && "text-sky-700 dark:text-sky-300")} />
                  {item.name}
                  {isActive && (
                    <div className="ml-auto h-1.5 w-1.5 rounded-full bg-sky-700 dark:bg-sky-300" />
                  )}
                </Link>
              );
            })}
          </nav>
        </ScrollArea>

        {/* Bottom Navigation */}
        <div className="border-t border-border/70 p-3">
          <nav className="space-y-1">
            {bottomNav.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                    isActive
                      ? "bg-muted text-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
            <button
              onClick={logout}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-all"
            >
              <LogOut className="h-5 w-5" />
              Sign Out
            </button>
          </nav>
        </div>
      </div>
    </aside>
  );
}
