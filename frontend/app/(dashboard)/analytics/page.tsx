"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  TrendingUp,
  Calendar,
  Target,
  Clock,
  Award,
  BookOpen,
  Brain,
  Flame,
  Star,
  ChevronDown,
  Download,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { progressAPI } from "@/services/api";

// Default/mock data for charts (will be replaced with API calls)
const defaultWeeklyProgress = [
  { day: "Mon", xp: 120, hours: 2, tasks: 3 },
  { day: "Tue", xp: 180, hours: 3, tasks: 4 },
  { day: "Wed", xp: 90, hours: 1.5, tasks: 2 },
  { day: "Thu", xp: 250, hours: 4, tasks: 5 },
  { day: "Fri", xp: 200, hours: 3.5, tasks: 4 },
  { day: "Sat", xp: 150, hours: 2.5, tasks: 3 },
  { day: "Sun", xp: 80, hours: 1, tasks: 2 },
];

const defaultMonthlyXP = [
  { week: "Week 1", xp: 500 },
  { week: "Week 2", xp: 750 },
  { week: "Week 3", xp: 620 },
  { week: "Week 4", xp: 890 },
];

const defaultSkillDistribution = [
  { name: "Problem Solving", value: 35, color: "#8b5cf6" },
  { name: "Conceptual", value: 25, color: "#06b6d4" },
  { name: "Memory", value: 20, color: "#10b981" },
  { name: "Application", value: 20, color: "#f59e0b" },
];

const defaultLearningByTopic = [
  { topic: "Python", hours: 15, completed: 75 },
  { topic: "DSA", hours: 10, completed: 40 },
  { topic: "React", hours: 8, completed: 60 },
  { topic: "System Design", hours: 5, completed: 25 },
  { topic: "Databases", hours: 4, completed: 30 },
];

const defaultAchievements = [
  { id: 1, title: "First Steps", description: "Complete your first lesson", icon: "🎯", earned: true },
  { id: 2, title: "Week Warrior", description: "7-day learning streak", icon: "🔥", earned: true },
  { id: 3, title: "Problem Solver", description: "Solve 10 coding challenges", icon: "💡", earned: true },
  { id: 4, title: "Knowledge Sharer", description: "Explain concepts 5 times", icon: "📚", earned: false },
  { id: 5, title: "Idea Machine", description: "Log 20 learning insights", icon: "✨", earned: false },
  { id: 6, title: "Master Learner", description: "Complete 5 learning paths", icon: "🏆", earned: false },
];

const defaultStats = {
  totalXP: 0,
  level: 1,
  streak: 0,
  hoursLearned: 0,
  tasksCompleted: 0,
  pathsCompleted: 0,
  ideasLogged: 0,
  averageDaily: 0,
};

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState("week");
  const [analytics, setAnalytics] = useState<any>(null);
  const [skills, setSkills] = useState<any[]>([]);
  const [achievements, setAchievements] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(defaultStats);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setIsLoading(true);
        const [analyticsData, skillsData, achievementsData, overviewData] = await Promise.all([
          progressAPI.getAnalytics(),
          progressAPI.getSkills(),
          progressAPI.getAchievements(),
          progressAPI.getOverview(),
        ]);

        // Update stats from overview
        setStats({
          totalXP: overviewData?.total_xp || 0,
          level: overviewData?.current_level || 1,
          streak: overviewData?.current_streak || 0,
          hoursLearned: overviewData?.total_hours_learned || 0,
          tasksCompleted: overviewData?.total_tasks_completed || 0,
          pathsCompleted: overviewData?.total_paths_completed || 0,
          ideasLogged: overviewData?.total_ideas_logged || 0,
          averageDaily: (overviewData?.total_hours_learned || 0) / 7,
        });

        setAnalytics(analyticsData || { weekly: defaultWeeklyProgress, monthly: defaultMonthlyXP });
        setSkills(skillsData && skillsData.length > 0 ? skillsData : defaultSkillDistribution);
        setAchievements(achievementsData && achievementsData.length > 0 ? achievementsData : defaultAchievements);
      } catch (err) {
        console.error("Error fetching analytics:", err);
        // Use defaults on error
        setAnalytics({ weekly: defaultWeeklyProgress, monthly: defaultMonthlyXP });
        setSkills(defaultSkillDistribution);
        setAchievements(defaultAchievements);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const weeklyProgress = analytics?.weekly || defaultWeeklyProgress;
  const monthlyXP = analytics?.monthly || defaultMonthlyXP;
  const skillDistribution = skills || defaultSkillDistribution;
  const learningByTopic = analytics?.byTopic || defaultLearningByTopic;
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Progress Analytics</h1>
          <p className="text-muted-foreground">Track your learning journey</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Calendar className="h-4 w-4 mr-2" />
            This Week
            <ChevronDown className="h-4 w-4 ml-2" />
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0 }}
        >
          <Card className="bg-gradient-to-br from-violet-500/10 to-indigo-500/10 border-violet-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
                  <Star className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="text-3xl font-bold">{stats.totalXP.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">Total XP</p>
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span>Level {stats.level}</span>
                  <span>Level {stats.level + 1}</span>
                </div>
                <Progress value={65} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-orange-500/10 flex items-center justify-center">
                  <Flame className="h-6 w-6 text-orange-500" />
                </div>
                <div>
                  <p className="text-3xl font-bold">{stats.streak}</p>
                  <p className="text-sm text-muted-foreground">Day Streak</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-cyan-500/10 flex items-center justify-center">
                  <Clock className="h-6 w-6 text-cyan-500" />
                </div>
                <div>
                  <p className="text-3xl font-bold">{stats.hoursLearned}</p>
                  <p className="text-sm text-muted-foreground">Hours Learned</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                  <Target className="h-6 w-6 text-emerald-500" />
                </div>
                <div>
                  <p className="text-3xl font-bold">{stats.tasksCompleted}</p>
                  <p className="text-sm text-muted-foreground">Tasks Done</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* XP Progress Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-violet-500" />
              Weekly XP Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={weeklyProgress}>
                <defs>
                  <linearGradient id="xpGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="day" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="xp"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  fill="url(#xpGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Skill Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-cyan-500" />
              Skill Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center">
              <ResponsiveContainer width="50%" height={200}>
                <PieChart>
                  <Pie
                    data={skillDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {skillDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex-1 space-y-3">
                {skillDistribution.map((skill) => (
                  <div key={skill.name} className="flex items-center gap-2">
                    <div
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: skill.color }}
                    />
                    <span className="text-sm flex-1">{skill.name}</span>
                    <span className="text-sm font-medium">{skill.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Learning by Topic */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-emerald-500" />
            Learning Progress by Topic
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={learningByTopic} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis type="number" className="text-xs" />
              <YAxis dataKey="topic" type="category" className="text-xs" width={100} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Bar dataKey="hours" name="Hours" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              <Bar dataKey="completed" name="% Completed" fill="#10b981" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Achievements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5 text-amber-500" />
            Achievements
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {achievements.map((achievement) => (
              <motion.div
                key={achievement.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ scale: 1.05 }}
                className={`relative p-4 rounded-xl text-center transition-colors ${
                  achievement.earned
                    ? "bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20"
                    : "bg-muted/30 opacity-50"
                }`}
              >
                <div className="text-3xl mb-2">{achievement.icon}</div>
                <h4 className="font-medium text-sm">{achievement.title}</h4>
                <p className="text-xs text-muted-foreground mt-1">
                  {achievement.description}
                </p>
                {achievement.earned && (
                  <Badge variant="success" className="absolute -top-2 -right-2 text-xs">
                    Earned
                  </Badge>
                )}
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Learning Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-10 w-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                <Clock className="h-5 w-5 text-violet-500" />
              </div>
              <div>
                <p className="font-medium">Best Learning Time</p>
                <p className="text-sm text-muted-foreground">When you're most productive</p>
              </div>
            </div>
            <p className="text-2xl font-bold">9 AM - 12 PM</p>
            <p className="text-xs text-muted-foreground mt-1">
              You complete 40% more tasks during morning hours
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-emerald-500" />
              </div>
              <div>
                <p className="font-medium">Strongest Skill</p>
                <p className="text-sm text-muted-foreground">Based on task performance</p>
              </div>
            </div>
            <p className="text-2xl font-bold">Problem Solving</p>
            <p className="text-xs text-muted-foreground mt-1">
              35% of your XP comes from coding challenges
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                <Target className="h-5 w-5 text-cyan-500" />
              </div>
              <div>
                <p className="font-medium">Weekly Goal</p>
                <p className="text-sm text-muted-foreground">Progress this week</p>
              </div>
            </div>
            <div className="flex items-end gap-2">
              <p className="text-2xl font-bold">750</p>
              <p className="text-muted-foreground mb-1">/ 1000 XP</p>
            </div>
            <Progress value={75} className="h-2 mt-2" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
