"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  BookOpen,
  Clock,
  Target,
  Plus,
  Search,
  Filter,
  ChevronRight,
  Star,
  Users,
  Loader,
  AlertCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface LearningPath {
  id: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  estimated_hours?: number;
  average_rating?: number;
  enrolled_students?: number;
  progress?: number;
  status?: string;
}

interface Enrollment {
  id: string;
  user_id: string;
  path_id: string;
  status: string;
  progress_percentage: number;
  xp_earned: number;
  modules_completed: number;
  learning_path?: LearningPath;
}

const levelColors: Record<string, string> = {
  beginner: "success",
  intermediate: "warning",
  advanced: "purple",
  expert: "destructive",
};

const difficultyLabels: Record<string, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
  expert: "Expert",
};

export default function LearnPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("my-paths");
  
  // State management
  const [enrolledPaths, setEnrolledPaths] = useState<Enrollment[]>([]);
  const [availablePaths, setAvailablePaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch user's enrolled paths
  const fetchEnrolledPaths = async () => {
    try {
      const response = await fetch("/api/v1/learning/paths?status=active", {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch enrolled paths");
      const data = await response.json();
      setEnrolledPaths(data.data || []);
    } catch (err) {
      console.error("Error fetching enrolled paths:", err);
      setError("Could not load your learning paths");
    }
  };

  // Fetch available paths for exploration
  const fetchAvailablePaths = async () => {
    try {
      const response = await fetch("/api/v1/learning/paths/explore?limit=20", {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch available paths");
      const data = await response.json();
      setAvailablePaths(data.data || []);
    } catch (err) {
      console.error("Error fetching available paths:", err);
    }
  };

  // Fetch data on mount
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        await Promise.all([fetchEnrolledPaths(), fetchAvailablePaths()]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Handle enrollment
  const handleEnroll = async (pathId: string) => {
    try {
      const response = await fetch(`/api/v1/learning/paths/${pathId}/enroll`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) throw new Error("Failed to enroll");
      
      // Refresh enrolled paths
      await fetchEnrolledPaths();
      // Refresh available paths
      await fetchAvailablePaths();
    } catch (err) {
      console.error("Error enrolling:", err);
      setError("Could not enroll in this path");
    }
  };

  const myPaths = enrolledPaths.filter((path) =>
    path.learning_path?.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const explorePaths = availablePaths.filter((path) =>
    path.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader className="h-8 w-8 animate-spin mx-auto mb-4 text-sky-700" />
          <p className="text-muted-foreground">Loading your learning paths...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Learning Paths</h1>
          <p className="text-muted-foreground">
            {enrolledPaths.length === 0
              ? "Start your learning journey today"
              : `Continue your ${enrolledPaths.length} active path${enrolledPaths.length !== 1 ? "s" : ""}`}
          </p>
        </div>
        <Button variant="gradient">
          <Plus className="h-4 w-4 mr-2" />
          Create Custom Path
        </Button>
      </div>

      {/* Error handling */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="flex items-center gap-3 p-4">
            <AlertCircle className="h-5 w-5 text-destructive" />
            <p className="text-sm text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search learning paths..."
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
          <TabsTrigger value="my-paths">
            My Paths ({enrolledPaths.length})
          </TabsTrigger>
          <TabsTrigger value="explore">
            Explore ({availablePaths.length})
          </TabsTrigger>
        </TabsList>

        {/* My Paths Tab */}
        <TabsContent value="my-paths" className="mt-6">
          {myPaths.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No enrolled paths yet</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  Start your learning journey by exploring available paths
                </p>
                <Button
                  variant="gradient"
                  onClick={() => setActiveTab("explore")}
                >
                  Explore Paths
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {myPaths.map((enrollment, index) => (
                <motion.div
                  key={enrollment.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  {enrollment.learning_path && (
                    <Link href={`/learn/${enrollment.path_id}`}>
                      <Card className="h-full cursor-pointer group hover:shadow-lg transition-shadow">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge
                                  variant={levelColors[enrollment.learning_path.difficulty] || "secondary"}
                                >
                                  {difficultyLabels[enrollment.learning_path.difficulty] || "Intermediate"}
                                </Badge>
                                {enrollment.learning_path.average_rating && (
                                  <div className="flex items-center gap-1 text-xs text-amber-500">
                                    <Star className="h-3 w-3 fill-current" />
                                    {enrollment.learning_path.average_rating.toFixed(1)}
                                  </div>
                                )}
                              </div>
                              <h3 className="font-semibold text-lg group-hover:text-sky-600 transition-colors">
                                {enrollment.learning_path.title}
                              </h3>
                              <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                                {enrollment.learning_path.description}
                              </p>
                            </div>
                          </div>

                          {/* Stats */}
                          <div className="my-4 flex items-center gap-4 text-xs text-muted-foreground">
                            {enrollment.learning_path.estimated_hours && (
                              <span className="flex items-center gap-1">
                                <Clock className="h-3.5 w-3.5" />
                                {enrollment.learning_path.estimated_hours}h
                              </span>
                            )}
                            {enrollment.modules_completed !== undefined && (
                              <span className="flex items-center gap-1">
                                <Target className="h-3.5 w-3.5" />
                                {enrollment.modules_completed} modules done
                              </span>
                            )}
                            {enrollment.learning_path.enrolled_students && (
                              <span className="flex items-center gap-1">
                                <Users className="h-3.5 w-3.5" />
                                {enrollment.learning_path.enrolled_students.toLocaleString()}
                              </span>
                            )}
                          </div>

                          {/* Progress */}
                          <div className="mt-4">
                            <div className="flex items-center justify-between text-xs mb-2">
                              <span className="text-muted-foreground">Progress</span>
                              <span className="font-medium text-sky-600">
                                {Math.round(enrollment.progress_percentage)}%
                              </span>
                            </div>
                            <Progress
                              value={enrollment.progress_percentage}
                              className="h-2"
                            />
                          </div>

                          {/* XP earned */}
                          {enrollment.xp_earned > 0 && (
                            <div className="mt-3 text-xs text-sky-600 font-medium">
                              +{enrollment.xp_earned} XP earned
                            </div>
                          )}

                          <div className="mt-4 flex gap-2">
                            <Button
                              variant="gradient"
                              size="sm"
                              className="group-hover:shadow-md"
                            >
                              Continue
                              <ChevronRight className="h-4 w-4 ml-1" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Explore Tab */}
        <TabsContent value="explore" className="mt-6">
          {explorePaths.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No paths available</h3>
                <p className="text-muted-foreground text-sm">
                  Try a different search term
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {explorePaths.map((path, index) => (
                <motion.div
                  key={path.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="h-full cursor-pointer group hover:shadow-lg transition-shadow">
                    <CardContent className="p-6 flex flex-col h-full">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge
                            variant={levelColors[path.difficulty] || "secondary"}
                          >
                            {difficultyLabels[path.difficulty] || "Intermediate"}
                          </Badge>
                          {path.average_rating && (
                            <div className="flex items-center gap-1 text-xs text-amber-500">
                              <Star className="h-3 w-3 fill-current" />
                              {path.average_rating.toFixed(1)}
                            </div>
                          )}
                        </div>
                        <h3 className="font-semibold text-lg group-hover:text-sky-600 transition-colors">
                          {path.title}
                        </h3>
                        <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                          {path.description}
                        </p>
                      </div>

                      {/* Stats */}
                      <div className="my-4 flex items-center gap-4 text-xs text-muted-foreground">
                        {path.estimated_hours && (
                          <span className="flex items-center gap-1">
                            <Clock className="h-3.5 w-3.5" />
                            ~{path.estimated_hours}h
                          </span>
                        )}
                        {path.enrolled_students && (
                          <span className="flex items-center gap-1">
                            <Users className="h-3.5 w-3.5" />
                            {path.enrolled_students.toLocaleString()}
                          </span>
                        )}
                      </div>

                      <div className="mt-auto pt-4">
                        <Button
                          variant="gradient"
                          size="sm"
                          className="w-full"
                          onClick={() => handleEnroll(path.id)}
                        >
                          Enroll Now
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
