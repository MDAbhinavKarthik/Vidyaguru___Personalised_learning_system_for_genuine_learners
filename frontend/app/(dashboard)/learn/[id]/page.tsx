"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import {
  ChevronLeft,
  BookOpen,
  CheckCircle2,
  Circle,
  Lock,
  Play,
  Send,
  Sparkles,
  RefreshCw,
  Lightbulb,
  AlertCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

// Mock data
const learningPath = {
  id: "1",
  title: "Python Fundamentals",
  description: "Learn Python from scratch",
  stages: [
    { id: "1", title: "Introduction to Python", status: "completed", xp: 100 },
    { id: "2", title: "Variables and Data Types", status: "completed", xp: 150 },
    { id: "3", title: "Control Flow", status: "completed", xp: 150 },
    { id: "4", title: "Lists and Dictionaries", status: "completed", xp: 200 },
    { id: "5", title: "Functions and Scope", status: "current", xp: 200 },
    { id: "6", title: "Object-Oriented Programming", status: "locked", xp: 250 },
    { id: "7", title: "Error Handling", status: "locked", xp: 200 },
    { id: "8", title: "File I/O and Modules", status: "locked", xp: 250 },
  ],
  currentStageContent: `
## Functions and Scope

Functions are reusable blocks of code that perform specific tasks. Understanding scope is crucial for writing clean, bug-free code.

### Learning Objectives
- Define and call functions
- Understand parameters and return values
- Master local vs global scope
- Use closures and nested functions

### Key Concept: Function Definition

\`\`\`python
def greet(name, greeting="Hello"):
    """A function that returns a greeting message."""
    return f"{greeting}, {name}!"

# Using the function
message = greet("Alice")
print(message)  # Output: Hello, Alice!
\`\`\`

### Understanding Scope

Variables defined inside a function are **local** to that function. They cannot be accessed from outside.

\`\`\`python
def calculate():
    result = 42  # local variable
    return result

# print(result)  # Error! 'result' is not defined outside
\`\`\`

Now, let's practice! Try answering the mentor's questions to solidify your understanding.
  `,
};

interface Message {
  id: string;
  role: "user" | "mentor";
  content: string;
  timestamp: Date;
}

const initialMessages: Message[] = [
  {
    id: "1",
    role: "mentor",
    content: `Welcome to the **Functions and Scope** stage! 🎯

I'm your AI mentor, and I'll guide you through this topic using the Socratic method - asking questions to help you discover the answers yourself.

Let's start with a fundamental question: **Why do you think we need functions in programming?** Think about a scenario where you might want to use the same code multiple times.`,
    timestamp: new Date(),
  },
];

export default function LearnPathPage() {
  const params = useParams();
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const currentStage = learningPath.stages.find((s) => s.status === "current");
  const completedCount = learningPath.stages.filter((s) => s.status === "completed").length;
  const progress = Math.round((completedCount / learningPath.stages.length) * 100);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const mentorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "mentor",
        content: `That's a great point! 🌟 

You mentioned reusability - that's one of the core benefits of functions. Let me build on that:

When you write code to calculate something, like the area of a circle, would you want to write that formula every time you need it? 

**Think about this:** If functions didn't exist, how would you handle a situation where you need to perform the same calculation 100 times with different values?

This leads us to understand not just *what* functions do, but *why* they're essential for:
1. **Code reusability** (as you mentioned)
2. **Code organization**
3. **Easier debugging**

Now, can you try writing a simple function that takes a number and returns its square? Share your attempt!`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, mentorResponse]);
      setIsTyping(false);
    }, 2000);
  };

  return (
    <div className="h-[calc(100vh-7rem)] flex gap-6">
      {/* Left Sidebar - Stages */}
      <div className="w-80 shrink-0 hidden lg:block">
        <Card className="h-full flex flex-col">
          <CardHeader className="pb-3">
            <Link href="/learn" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-2">
              <ChevronLeft className="h-4 w-4 mr-1" />
              Back to Paths
            </Link>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">🐍</span>
              {learningPath.title}
            </CardTitle>
            <div className="mt-2">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium text-violet-600">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden">
            <ScrollArea className="h-full pr-4">
              <div className="space-y-2">
                {learningPath.stages.map((stage, index) => (
                  <button
                    key={stage.id}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
                      stage.status === "current"
                        ? "bg-violet-500/10 border border-violet-500/20"
                        : stage.status === "completed"
                        ? "bg-muted/50 hover:bg-muted"
                        : "opacity-60 cursor-not-allowed"
                    }`}
                    disabled={stage.status === "locked"}
                  >
                    <div className="shrink-0">
                      {stage.status === "completed" ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                      ) : stage.status === "current" ? (
                        <Play className="h-5 w-5 text-violet-600" />
                      ) : (
                        <Lock className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium truncate ${
                        stage.status === "current" ? "text-violet-700 dark:text-violet-300" : ""
                      }`}>
                        {stage.title}
                      </p>
                      <p className="text-xs text-muted-foreground">+{stage.xp} XP</p>
                    </div>
                    {stage.status === "current" && (
                      <Badge variant="purple" className="shrink-0">Current</Badge>
                    )}
                  </button>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Card className="flex-1 flex flex-col overflow-hidden">
          {/* Stage Header */}
          <CardHeader className="border-b shrink-0">
            <div className="flex items-center justify-between">
              <div>
                <Badge variant="purple" className="mb-2">Stage {completedCount + 1}</Badge>
                <CardTitle>{currentStage?.title}</CardTitle>
              </div>
              <Button variant="gradient">
                Complete Stage
                <CheckCircle2 className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </CardHeader>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col min-h-0">
            <ScrollArea ref={scrollRef} className="flex-1 p-4">
              <div className="max-w-3xl mx-auto space-y-4">
                {/* Learning Content */}
                <div className="prose prose-sm dark:prose-invert max-w-none mb-6 p-4 rounded-xl bg-muted/30">
                  <ReactMarkdown>{learningPath.currentStageContent}</ReactMarkdown>
                </div>

                {/* Chat Messages */}
                <div className="border-t pt-4">
                  <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="h-4 w-4 text-violet-600" />
                    <span className="text-sm font-medium">Interactive Learning</span>
                  </div>

                  <AnimatePresence mode="popLayout">
                    {messages.map((message) => (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className={`flex gap-3 mb-4 ${
                          message.role === "user" ? "flex-row-reverse" : ""
                        }`}
                      >
                        <Avatar className="h-8 w-8 shrink-0">
                          <AvatarFallback className={
                            message.role === "mentor"
                              ? "bg-gradient-to-br from-violet-500 to-indigo-600 text-white"
                              : "bg-emerald-500 text-white"
                          }>
                            {message.role === "mentor" ? "🧠" : "U"}
                          </AvatarFallback>
                        </Avatar>
                        <div
                          className={`max-w-[80%] rounded-2xl p-4 ${
                            message.role === "mentor"
                              ? "bg-gradient-to-br from-violet-500/5 to-indigo-500/5 border"
                              : "bg-emerald-500/10 border border-emerald-500/20"
                          }`}
                        >
                          <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>

                  {isTyping && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex gap-3 mb-4"
                    >
                      <Avatar className="h-8 w-8 shrink-0">
                        <AvatarFallback className="bg-gradient-to-br from-violet-500 to-indigo-600 text-white">
                          🧠
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-muted/50 rounded-2xl p-4">
                        <div className="flex items-center gap-1">
                          <span className="h-2 w-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                          <span className="h-2 w-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                          <span className="h-2 w-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
              </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="border-t p-4 shrink-0">
              <div className="max-w-3xl mx-auto">
                <div className="flex gap-2">
                  <div className="flex-1 relative">
                    <Textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Share your thoughts or ask a question..."
                      className="min-h-[60px] pr-12 resize-none"
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                    />
                    <Button
                      size="icon"
                      variant="ghost"
                      className="absolute right-2 bottom-2"
                      onClick={handleSendMessage}
                      disabled={!input.trim() || isTyping}
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Button variant="ghost" size="sm" className="text-xs">
                    <Lightbulb className="h-3 w-3 mr-1" />
                    Get Hint
                  </Button>
                  <Button variant="ghost" size="sm" className="text-xs">
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Rephrase Question
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
