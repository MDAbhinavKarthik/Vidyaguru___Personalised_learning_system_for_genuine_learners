"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Plus,
  Filter,
  Search,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronRight,
  BookOpen,
  Code,
  Lightbulb,
  Target,
  FileText,
  Star,
  Calendar,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { tasksAPI } from "@/services/api";
import { useRouter } from "next/navigation";

interface Task {
  id: string;
  title: string;
  description?: string;
  type: "recall" | "explanation" | "problem" | "reflection" | "application";
  status: "pending" | "in-progress" | "completed" | "failed";
  xp?: number;
  dueDate?: string;
  skillAreas?: string[];
}

// Default mock data for fallback
const defaultTasks: Task[] = [
  {
    id: "1",
    type: "recall",
    title: "List 5 key principles of Object-Oriented Programming",
    description: "Write down the main OOP concepts from memory",
    status: "completed",
    xp: 50,
    dueDate: "2024-01-15",
    skillAreas: ["Memory", "Conceptual"],
  },
  {
    id: "2",
    type: "explanation",
    title: "Explain how recursion works to a beginner",
    description: "Use simple analogies and examples in your explanation",
    status: "in-progress",
    xp: 75,
    dueDate: "2024-01-18",
    skillAreas: ["Teaching", "Understanding"],
  },
  {
    id: "3",
    type: "problem",
    title: "Implement a Binary Search Tree",
    description: "Create a BST with insert, search, and delete operations",
    status: "pending",
    xp: 150,
    dueDate: "2024-01-20",
    skillAreas: ["Coding", "Problem-Solving"],
  },
];

const taskTypeIcons = {
  recall: BookOpen,
  explanation: FileText,
  problem: Code,
  reflection: Lightbulb,
  application: Target,
};

const taskTypeColors = {
  recall: "bg-blue-500",
  explanation: "bg-purple-500",
  problem: "bg-orange-500",
  reflection: "bg-emerald-500",
  application: "bg-rose-500",
};

const statusColors = {
  completed: "success",
  "in-progress": "warning",
  pending: "info",
  failed: "destructive",
} as const;

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setIsLoading(true);
        const data = await tasksAPI.getTasks();
        setTasks(data || defaultTasks);
      } catch (err) {
        console.error("Error fetching tasks:", err);
        setError("Failed to load tasks");
        // Use default tasks for new users
        setTasks(defaultTasks);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const handleCreateTask = () => {
    router.push("/dashboard/tasks/new");
  };

  const handleSubmitTask = async (taskId: string) => {
    try {
      await tasksAPI.submitTask(taskId);
      // Refresh tasks list
      const data = await tasksAPI.getTasks();
      setTasks(data || []);
    } catch (err) {
      console.error("Error submitting task:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          <p className="mt-4 text-gray-600">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  const completedCount = tasks.filter((t) => t.status === "completed").length;
  const inProgressCount = tasks.filter((t) => t.status === "in-progress").length;
  const pendingCount = tasks.filter((t) => t.status === "pending").length;
  const totalXP = tasks.reduce((sum, task) => sum + (task.xp || 0), 0);

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase());
    if (activeTab === "all") return matchesSearch;
    return matchesSearch && task.status === activeTab;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Tasks</h1>
          <p className="text-muted-foreground">Track and complete your learning tasks</p>
        </div>
        <Button 
          className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 gap-2"
          onClick={handleCreateTask}
        >
          <Plus className="w-5 h-5" />
          New Task
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{completedCount}</p>
                <p className="text-xs text-muted-foreground">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Clock className="h-5 w-5 text-amber-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{inProgressCount}</p>
                <p className="text-xs text-muted-foreground">In Progress</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <AlertCircle className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{pendingCount}</p>
                <p className="text-xs text-muted-foreground">Pending</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                <Star className="h-5 w-5 text-violet-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{totalXP}</p>
                <p className="text-xs text-muted-foreground">XP Earned</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All Tasks</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="in-progress">In Progress</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-6">
          <div className="space-y-4">
            {filteredTasks.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Target className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium">No tasks found</h3>
                  <p className="text-muted-foreground text-sm">
                    {tasks.length === 0 
                      ? "You have no tasks yet. Start by enrolling in a learning path!"
                      : "Try a different search or create a new task"}
                  </p>
                </CardContent>
              </Card>
            ) : (
              filteredTasks.map((task, index) => {
                const Icon = taskTypeIcons[task.type as keyof typeof taskTypeIcons];
                return (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card className="hover:shadow-lg transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-start gap-4">
                          <div
                            className={`h-10 w-10 rounded-lg flex items-center justify-center text-white shrink-0 ${
                              taskTypeColors[task.type as keyof typeof taskTypeColors]
                            }`}
                          >
                            <Icon className="h-5 w-5" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge variant={statusColors[task.status as keyof typeof statusColors]}>
                                {task.status.replace("-", " ")}
                              </Badge>
                              <Badge variant="outline" className="capitalize">
                                {task.type}
                              </Badge>
                            </div>
                            <h3 className="font-medium">{task.title}</h3>
                            <p className="text-sm text-muted-foreground line-clamp-1 mt-1">
                              {task.description}
                            </p>
                            <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground flex-wrap">
                              <span className="flex items-center gap-1">
                                <Star className="h-3.5 w-3.5 text-amber-500" />
                                +{task.xp || 0} XP
                              </span>
                              {task.dueDate && (
                                <span className="flex items-center gap-1">
                                  <Calendar className="h-3.5 w-3.5" />
                                  Due: {new Date(task.dueDate).toLocaleDateString()}
                                </span>
                              )}
                              {task.skillAreas && task.skillAreas.length > 0 && (
                                <div className="flex items-center gap-1">
                                  {task.skillAreas.slice(0, 2).map((skill) => (
                                    <span
                                      key={skill}
                                      className="bg-muted px-2 py-0.5 rounded text-xs"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={() => handleSubmitTask(task.id)}
                          >
                            <ChevronRight className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Task Types Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Task Types</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(taskTypeIcons).map(([type, Icon]) => (
              <div key={type} className="flex items-center gap-2">
                <div
                  className={`h-8 w-8 rounded-lg flex items-center justify-center text-white ${
                    taskTypeColors[type as keyof typeof taskTypeColors]
                  }`}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <span className="text-sm capitalize">{type}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
