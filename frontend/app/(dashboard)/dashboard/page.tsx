"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  BookOpen,
  Target,
  Clock,
  TrendingUp,
  Flame,
  Trophy,
  ArrowRight,
  Play,
  CheckCircle2,
  Lightbulb,
  Loader,
  AlertCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/lib/store";
import { progressAPI, learningAPI, tasksAPI, journalAPI } from "@/services/api";

interface ProgressOverview {
  total_xp: number;
  current_level: number;
  current_streak: number;
  longest_streak: number;
  total_tasks_completed: number;
  total_hours_learned: number;
  last_activity: string;
}

interface Task {
  id: string;
  title: string;
  type: string;
  status: string;
  xp_reward: number;
  deadline?: string;
}

interface JournalEntry {
  id: string;
  title: string;
  created_at: string;
  entry_type: string;
}

interface LearningPath {
  id: string;
  title: string;
  progress_percentage: number;
  status: string;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [greeting, setGreeting] = useState("Hello");

  // State management
  const [overview, setOverview] = useState<ProgressOverview | null>(null);
  const [currentPaths, setCurrentPaths] = useState<LearningPath[]>([]);
  const [recentTasks, setRecentTasks] = useState<Task[]>([]);
  const [recentIdeas, setRecentIdeas] = useState<JournalEntry[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Time-based greeting
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [overviewData, pathsData, tasksData, journalData] = await Promise.all([
          progressAPI.getOverview().catch(() => null),
          learningAPI.getPaths({ status: "active", limit: 1 }).catch(() => ({ data: [] })),
          tasksAPI.getTasks({ status: "pending", limit: 3 }).catch(() => ({ data: [] })),
          journalAPI.getEntries({ limit: 2 }).catch(() => ({ data: [] })),
        ]);

        setOverview(overviewData || {
          total_xp: 0,
          current_level: 1,
          current_streak: 0,
          longest_streak: 0,
          total_tasks_completed: 0,
          total_hours_learned: 0,
        });

        setCurrentPaths(pathsData?.data || []);
        setRecentTasks(tasksData?.data || []);
        setRecentIdeas(journalData?.data || []);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    // Refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader className="h-8 w-8 animate-spin mx-auto mb-4 text-sky-700" />
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Calculate weekly statistics BEFORE using them
  const calculateWeeklyHours = (tasks: any[]) => {
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const weeklyTasks = tasks.filter((t) => {
      try {
        const taskDate = new Date(t.created_at || t.dueDate || now);
        return taskDate >= weekAgo && taskDate <= now;
      } catch {
        return false;
      }
    });
    // Estimate 0.5 hours per task
    return weeklyTasks.length * 0.5;
  };

  const weeklyCompletedTasks = recentTasks.filter((t) => {
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    try {
      const taskDate = new Date(t.created_at || t.dueDate || now);
      return t.status === "completed" && taskDate >= weekAgo && taskDate <= now;
    } catch {
      return false;
    }
  });

  const weeklyTotalTasks = recentTasks.filter((t) => {
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    try {
      const taskDate = new Date(t.created_at || t.dueDate || now);
      return taskDate >= weekAgo && taskDate <= now;
    } catch {
      return false;
    }
  });

  const weeklyHours = calculateWeeklyHours(recentTasks);
  const weeklyTasksProgress = weeklyTotalTasks.length > 0 ? (weeklyCompletedTasks.length / weeklyTotalTasks.length) * 100 : 0;

  const statCards = [
    {
      label: "XP Earned",
      value: overview?.total_xp || 0,
      change: "+120 today",
      icon: Trophy,
      color: "text-amber-500",
    },
    {
      label: "Current Streak",
      value: `${overview?.current_streak || 0} days`,
      change: "Keep going!",
      icon: Flame,
      color: "text-orange-500",
    },
    {
      label: "Tasks Completed",
      value: overview?.total_tasks_completed || 0,
      change: `${weeklyCompletedTasks.length} this week`,
      icon: Target,
      color: "text-emerald-500",
    },
    {
      label: "Hours Learned",
      value: (overview?.total_hours_learned || 0).toFixed(1),
      change: `+${weeklyHours.toFixed(1)} this week`,
      icon: Clock,
      color: "text-sky-500",
    },
  ];

  const currentPath = currentPaths[0];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold">
            {greeting}, {user?.full_name?.split(" ")[0] || "Learner"}! 👋
          </h1>
          <p className="text-muted-foreground">
            {overview?.total_xp === 0
              ? "Start your learning journey today"
              : "Welcome back! Ready to continue?"}
          </p>
        </div>
        <Link href="/learn">
          <Button variant="gradient">
            Continue Learning
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </motion.div>

      {/* Error Alert */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="flex items-center gap-3 p-4">
            <AlertCircle className="h-5 w-5 text-destructive" />
            <p className="text-sm text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                    <p className="text-xs text-muted-foreground mt-1">{stat.change}</p>
                  </div>
                  <div className={`p-2 rounded-lg bg-muted ${stat.color}`}>
                    <stat.icon className="h-5 w-5" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Current Learning Path */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-sky-600" />
                    Current Learning Path
                  </CardTitle>
                  <Link href="/learn">
                    <Button variant="ghost" size="sm">
                      View All
                      <ArrowRight className="ml-1 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {currentPath ? (
                  <div className="p-4 rounded-xl bg-gradient-to-br from-sky-500/5 to-cyan-500/5 border">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{currentPath.title}</h3>
                        <div className="mt-3">
                          <div className="flex items-center justify-between text-sm mb-2">
                            <span className="text-muted-foreground">
                              Progress:
                            </span>
                            <span className="font-medium text-sky-600">
                              {Math.round(currentPath.progress_percentage)}%
                            </span>
                          </div>
                          <Progress
                            value={currentPath.progress_percentage}
                            className="h-2"
                          />
                        </div>
                      </div>
                      <Link href={`/learn/${currentPath.id}`}>
                        <Button variant="gradient" size="sm">
                          Continue
                          <ArrowRight className="ml-1 h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ) : (
                  <div className="p-6 text-center">
                    <BookOpen className="h-10 w-10 text-muted-foreground mx-auto mb-2" />
                    <p className="text-muted-foreground mb-3">No active learning paths</p>
                    <Link href="/learn">
                      <Button variant="gradient" size="sm">
                        Explore Paths
                      </Button>
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Tasks */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-emerald-600" />
                    Pending Tasks
                  </CardTitle>
                  <Link href="/tasks">
                    <Button variant="ghost" size="sm">
                      View All
                      <ArrowRight className="ml-1 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {recentTasks.length > 0 ? (
                  <div className="space-y-3">
                    {recentTasks.map((task) => (
                      <div key={task.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                        <Play className="h-4 w-4 mt-1 text-sky-600 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm">{task.title}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline" className="text-xs">
                              {task.type}
                            </Badge>
                            <span className="text-xs text-amber-600 font-medium">
                              +{task.xp_reward} XP
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 text-center">
                    <CheckCircle2 className="h-10 w-10 text-emerald-500 mx-auto mb-2" />
                    <p className="text-muted-foreground">All caught up! No pending tasks</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="text-base">This Week</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Learning Time</span>
                    <span className="font-medium">{weeklyHours.toFixed(1)}h</span>
                  </div>
                  <Progress value={Math.min(weeklyHours * 10, 100)} className="h-1.5" />
                </div>
                <div>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Tasks Done</span>
                    <span className="font-medium">{weeklyCompletedTasks.length}/{weeklyTotalTasks.length}</span>
                  </div>
                  <Progress value={weeklyTasksProgress} className="h-1.5" />
                </div>
                <div>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Ideas Captured</span>
                    <span className="font-medium">{recentIdeas.length}</span>
                  </div>
                  <Progress value={recentIdeas.length * 25} className="h-1.5" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Ideas */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Lightbulb className="h-4 w-4 text-amber-500" />
                    Recent Ideas
                  </CardTitle>
                  <Link href="/journal">
                    <Button variant="ghost" size="icon">
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {recentIdeas.length > 0 ? (
                  <div className="space-y-3">
                    {recentIdeas.map((idea) => (
                      <Link key={idea.id} href={`/journal/${idea.id}`}>
                        <div className="p-3 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                          <p className="text-sm font-medium line-clamp-2">{idea.title}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {new Date(idea.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-xs text-muted-foreground">No ideas yet</p>
                    <Link href="/journal">
                      <Button variant="outline" size="sm" className="mt-2">
                        Add Idea
                      </Button>
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold">
            {greeting}, {user?.full_name?.split(" ")[0] || "Learner"}! 👋
          </h1>
          <p className="text-muted-foreground">
            Ready to continue your learning journey?
          </p>
        </div>
        <Link href="/learn">
          <Button variant="gradient">
            Continue Learning
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card hover>
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                    <p className="text-xs text-muted-foreground mt-1">{stat.change}</p>
                  </div>
                  <div className={`p-2 rounded-lg bg-muted ${stat.color}`}>
                    <stat.icon className="h-5 w-5" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Current Learning Path */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-violet-600" />
                    Current Learning Path
                  </CardTitle>
                  <Link href="/learn">
                    <Button variant="ghost" size="sm">
                      View All
                      <ArrowRight className="ml-1 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-xl bg-gradient-to-br from-violet-500/5 to-indigo-500/5 border">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{currentPath.title}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Current: {currentPath.currentStage}
                      </p>
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-muted-foreground">
                            {currentPath.completedStages} of {currentPath.totalStages} stages
                          </span>
                          <span className="font-medium text-violet-600">
                            {currentPath.progress}%
                          </span>
                        </div>
                        <Progress value={currentPath.progress} className="h-2" />
                      </div>
                    </div>
                    <Link href={`/learn/${currentPath.id}`}>
                      <Button variant="gradient" className="shrink-0">
                        <Play className="h-4 w-4 mr-2" />
                        Continue
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Tasks */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-emerald-600" />
                    Recent Tasks
                  </CardTitle>
                  <Link href="/tasks">
                    <Button variant="ghost" size="sm">
                      View All
                      <ArrowRight className="ml-1 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentTasks.map((task) => (
                    <div
                      key={task.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`h-8 w-8 rounded-lg flex items-center justify-center ${
                            task.status === "completed"
                              ? "bg-emerald-500/10 text-emerald-600"
                              : task.status === "in-progress"
                              ? "bg-amber-500/10 text-amber-600"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {task.status === "completed" ? (
                            <CheckCircle2 className="h-4 w-4" />
                          ) : (
                            <Target className="h-4 w-4" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-sm">{task.title}</p>
                          <p className="text-xs text-muted-foreground capitalize">{task.type}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={
                            task.status === "completed"
                              ? "success"
                              : task.status === "in-progress"
                              ? "warning"
                              : "secondary"
                          }
                        >
                          {task.status.replace("-", " ")}
                        </Badge>
                        <span className="text-xs font-medium text-violet-600">+{task.xp} XP</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Link href="/mentor" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center mr-3">
                      <span className="text-white text-sm">🧠</span>
                    </div>
                    Chat with AI Mentor
                  </Button>
                </Link>
                <Link href="/tasks" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <div className="h-8 w-8 rounded-lg bg-emerald-500/10 flex items-center justify-center mr-3">
                      <Target className="h-4 w-4 text-emerald-600" />
                    </div>
                    Start a New Task
                  </Button>
                </Link>
                <Link href="/journal" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <div className="h-8 w-8 rounded-lg bg-amber-500/10 flex items-center justify-center mr-3">
                      <Lightbulb className="h-4 w-4 text-amber-600" />
                    </div>
                    Add to Journal
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Ideas */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Lightbulb className="h-4 w-4 text-amber-500" />
                    Recent Ideas
                  </CardTitle>
                  <Link href="/journal">
                    <Button variant="ghost" size="sm">
                      View All
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentIdeas.map((idea) => (
                    <div
                      key={idea.id}
                      className="p-3 rounded-lg bg-amber-500/5 border border-amber-500/10"
                    >
                      <p className="text-sm font-medium">{idea.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">{idea.created}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Daily Wisdom */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Card className="bg-gradient-to-br from-violet-500/10 to-indigo-500/10 border-violet-200 dark:border-violet-800">
              <CardContent className="p-5">
                <p className="text-sm font-medium text-violet-700 dark:text-violet-300 mb-2">
                  💡 Daily Wisdom
                </p>
                <p className="text-sm italic">
                  "The more you learn, the more you realize how much you don't know."
                </p>
                <p className="text-xs text-muted-foreground mt-2">— Socrates</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
