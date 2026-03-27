"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Plus,
  Search,
  Lightbulb,
  BookOpen,
  Calendar,
  Tag,
  Star,
  Trash2,
  Edit2,
  ChevronRight,
  Filter,
  SortAsc,
  Sparkles,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

// Mock data
const ideas = [
  {
    id: "1",
    title: "Build a URL Shortener Service",
    content:
      "Create a full-stack URL shortener with analytics tracking. Could use Redis for caching and PostgreSQL for persistence. Would be a great way to practice system design concepts.",
    tags: ["Project", "Full-Stack", "System Design"],
    createdAt: new Date("2024-01-15"),
    isStarred: true,
    linkedPath: "Web Development with React",
  },
  {
    id: "2",
    title: "Understanding Closure in JavaScript",
    content:
      "Closures allow functions to access variables from their outer scope even after the outer function has returned. Key insight: the function maintains a reference to its lexical environment.",
    tags: ["JavaScript", "Concept", "Functions"],
    createdAt: new Date("2024-01-14"),
    isStarred: false,
    linkedPath: null,
  },
  {
    id: "3",
    title: "Why Recursion Sometimes Feels Magical",
    content:
      "Recursion is like a stack of Russian dolls - each one contains a smaller version of itself. The base case is the smallest doll. Understanding the call stack helps visualize what's happening.",
    tags: ["Recursion", "Mental Model", "DSA"],
    createdAt: new Date("2024-01-13"),
    isStarred: true,
    linkedPath: "Data Structures & Algorithms",
  },
  {
    id: "4",
    title: "API Rate Limiting Strategies",
    content:
      "Learned about different rate limiting approaches: Token Bucket, Leaky Bucket, Fixed Window, Sliding Window. Each has trade-offs between memory usage and accuracy.",
    tags: ["Backend", "System Design", "API"],
    createdAt: new Date("2024-01-12"),
    isStarred: false,
    linkedPath: null,
  },
  {
    id: "5",
    title: "The Feynman Technique for Learning",
    content:
      "1. Study the concept\n2. Teach it to a child\n3. Identify gaps in understanding\n4. Review and simplify\n\nThis is exactly what VidyaGuru's Socratic method does!",
    tags: ["Learning", "Technique", "Meta"],
    createdAt: new Date("2024-01-11"),
    isStarred: true,
    linkedPath: null,
  },
];

const allTags = ["Project", "Concept", "Learning", "DSA", "System Design", "Backend", "JavaScript"];

export default function JournalPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [showNewIdea, setShowNewIdea] = useState(false);
  const [newIdea, setNewIdea] = useState({ title: "", content: "", tags: [] as string[] });
  const [ideaList, setIdeaList] = useState(ideas);

  const filteredIdeas = ideaList.filter((idea) => {
    const matchesSearch =
      idea.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      idea.content.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTag = !selectedTag || idea.tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  const starredCount = ideaList.filter((i) => i.isStarred).length;

  const handleToggleStar = (id: string) => {
    setIdeaList((prev) =>
      prev.map((idea) =>
        idea.id === id ? { ...idea, isStarred: !idea.isStarred } : idea
      )
    );
  };

  return (
    <div className="h-[calc(100vh-7rem)] flex gap-6">
      {/* Sidebar */}
      <div className="w-72 shrink-0 hidden lg:block">
        <Card className="h-full flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-amber-500" />
              Idea Journal
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Capture your learning insights
            </p>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden">
            <div className="space-y-6">
              {/* Quick Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/50 text-center">
                  <p className="text-2xl font-bold">{ideaList.length}</p>
                  <p className="text-xs text-muted-foreground">Total Ideas</p>
                </div>
                <div className="p-3 rounded-lg bg-amber-500/10 text-center">
                  <p className="text-2xl font-bold text-amber-600">{starredCount}</p>
                  <p className="text-xs text-muted-foreground">Starred</p>
                </div>
              </div>

              {/* Tags Filter */}
              <div>
                <h4 className="text-sm font-medium mb-3">Filter by Tag</h4>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={selectedTag === null ? "gradient" : "outline"}
                    size="sm"
                    onClick={() => setSelectedTag(null)}
                  >
                    All
                  </Button>
                  {allTags.map((tag) => (
                    <Button
                      key={tag}
                      variant={selectedTag === tag ? "gradient" : "outline"}
                      size="sm"
                      onClick={() => setSelectedTag(tag)}
                    >
                      {tag}
                    </Button>
                  ))}
                </div>
              </div>

              {/* AI Suggestion */}
              <div className="p-4 rounded-xl bg-gradient-to-br from-violet-500/10 to-indigo-500/10 border border-violet-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="h-4 w-4 text-violet-600" />
                  <span className="text-sm font-medium">AI Insight</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  You've been exploring System Design topics. Consider connecting
                  your URL Shortener idea with rate limiting strategies!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search ideas..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <SortAsc className="h-4 w-4 mr-2" />
              Sort
            </Button>
            <Button variant="gradient" onClick={() => setShowNewIdea(true)}>
              <Plus className="h-4 w-4 mr-2" />
              New Idea
            </Button>
          </div>
        </div>

        {/* New Idea Form */}
        {showNewIdea && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="mb-6 border-violet-500/30">
              <CardContent className="p-4">
                <Input
                  placeholder="Idea title..."
                  value={newIdea.title}
                  onChange={(e) => setNewIdea({ ...newIdea, title: e.target.value })}
                  className="mb-3 font-medium"
                />
                <Textarea
                  placeholder="Capture your thought... What did you learn? What connection did you make?"
                  value={newIdea.content}
                  onChange={(e) => setNewIdea({ ...newIdea, content: e.target.value })}
                  className="mb-3 min-h-[100px]"
                />
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Tag className="h-4 w-4 text-muted-foreground" />
                    <div className="flex gap-1">
                      {allTags.slice(0, 4).map((tag) => (
                        <Button
                          key={tag}
                          variant={newIdea.tags.includes(tag) ? "gradient" : "outline"}
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() =>
                            setNewIdea({
                              ...newIdea,
                              tags: newIdea.tags.includes(tag)
                                ? newIdea.tags.filter((t) => t !== tag)
                                : [...newIdea.tags, tag],
                            })
                          }
                        >
                          {tag}
                        </Button>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setShowNewIdea(false)}>
                      Cancel
                    </Button>
                    <Button variant="gradient">Save Idea</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Ideas Grid */}
        <ScrollArea className="flex-1">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-4">
            {filteredIdeas.length === 0 ? (
              <Card className="col-span-full">
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Lightbulb className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium">No ideas found</h3>
                  <p className="text-muted-foreground text-sm">
                    Start capturing your learning insights
                  </p>
                </CardContent>
              </Card>
            ) : (
              filteredIdeas.map((idea, index) => (
                <motion.div
                  key={idea.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card hover className="h-full">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h3 className="font-medium line-clamp-1">{idea.title}</h3>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="shrink-0 h-8 w-8"
                          onClick={() => handleToggleStar(idea.id)}
                        >
                          <Star
                            className={`h-4 w-4 ${
                              idea.isStarred
                                ? "fill-amber-500 text-amber-500"
                                : "text-muted-foreground"
                            }`}
                          />
                        </Button>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
                        {idea.content}
                      </p>
                      <div className="flex flex-wrap gap-1 mb-3">
                        {idea.tags.map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3.5 w-3.5" />
                          {idea.createdAt.toLocaleDateString()}
                        </div>
                        {idea.linkedPath && (
                          <div className="flex items-center gap-1">
                            <BookOpen className="h-3.5 w-3.5" />
                            <span className="truncate max-w-[120px]">{idea.linkedPath}</span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
