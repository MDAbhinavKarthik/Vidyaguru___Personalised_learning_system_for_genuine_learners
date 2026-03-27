"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import {
  Send,
  Sparkles,
  RefreshCw,
  Lightbulb,
  BookOpen,
  Code,
  HelpCircle,
  MessageSquare,
  Plus,
  Trash2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

interface Message {
  id: string;
  role: "user" | "mentor";
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

const quickPrompts = [
  { icon: Code, label: "Explain a concept", prompt: "Can you explain the concept of..." },
  { icon: HelpCircle, label: "Debug my code", prompt: "I'm having trouble with this code..." },
  { icon: BookOpen, label: "Learning advice", prompt: "What's the best way to learn..." },
  { icon: Lightbulb, label: "Project ideas", prompt: "Can you suggest project ideas for..." },
];

const initialMessage: Message = {
  id: "1",
  role: "mentor",
  content: `नमस्ते! Welcome, learner! 🙏

I'm **VidyaGuru**, your AI learning mentor. I'm here to guide you on your learning journey using the **Socratic method** – helping you discover answers through thoughtful questions rather than just giving them away.

I believe in *विद्या ददाति विनयम्* – "Knowledge gives humility."

How can I help you today? You can:
- Ask me to explain any concept
- Share code you're struggling with
- Discuss your learning goals
- Get guidance on what to learn next

What would you like to explore?`,
  timestamp: new Date(),
};

export default function MentorPage() {
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: "1",
      title: "Current Conversation",
      messages: [initialMessage],
      createdAt: new Date(),
    },
  ]);
  const [activeConversationId, setActiveConversationId] = useState("1");
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const activeConversation = conversations.find((c) => c.id === activeConversationId);
  const messages = activeConversation?.messages || [];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (messageContent?: string) => {
    const content = messageContent || input;
    if (!content.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: content,
      timestamp: new Date(),
    };

    // Get current conversation messages for context
    const currentMessages = activeConversation?.messages || [];

    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === activeConversationId
          ? { ...conv, messages: [...conv.messages, userMessage] }
          : conv
      )
    );
    setInput("");
    setIsTyping(true);

    try {
      // Call backend API with auth header
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
      const response = await fetch("/api/v1/mentor/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { "Authorization": `Bearer ${token}` }),
        },
        body: JSON.stringify({
          message: content,
          conversation_id: activeConversationId !== "1" ? activeConversationId : undefined,
          context_type: "general",
          include_wisdom: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      const mentorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "mentor",
        content: data.message?.content || data.content || "I'm having trouble responding right now. Please try again.",
        timestamp: new Date(),
      };

      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === activeConversationId
            ? { ...conv, messages: [...conv.messages, mentorResponse] }
            : conv
        )
      );
    } catch (error) {
      console.error("Error sending message:", error);
      
      // Fallback error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "mentor",
        content: "I apologize, but I'm experiencing technical difficulties. Please check your connection and try again. 🙏",
        timestamp: new Date(),
      };

      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === activeConversationId
            ? { ...conv, messages: [...conv.messages, errorMessage] }
            : conv
        )
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: "New Conversation",
      messages: [initialMessage],
      createdAt: new Date(),
    };
    setConversations((prev) => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
  };

  return (
    <div className="h-[calc(100vh-7rem)] flex gap-6">
      {/* Sidebar - Conversation History */}
      <div className="w-72 shrink-0 hidden lg:block">
        <Card className="h-full flex flex-col">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Conversations</CardTitle>
              <Button variant="ghost" size="icon" onClick={handleNewConversation}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden p-0">
            <ScrollArea className="h-full">
              <div className="p-3 space-y-2">
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => setActiveConversationId(conv.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
                      conv.id === activeConversationId
                        ? "bg-violet-500/10 border border-violet-500/20"
                        : "hover:bg-muted"
                    }`}
                  >
                    <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{conv.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {conv.messages.length} messages
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Main Chat Area */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader className="border-b shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <span className="text-xl">🧠</span>
            </div>
            <div>
              <CardTitle className="flex items-center gap-2">
                VidyaGuru AI Mentor
                <Badge variant="purple">Socratic Method</Badge>
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Guiding you to discover answers through questions
              </p>
            </div>
          </div>
        </CardHeader>

        {/* Messages */}
        <ScrollArea ref={scrollRef} className="flex-1 p-4">
          <div className="max-w-3xl mx-auto space-y-4">
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className={`flex gap-3 ${
                    message.role === "user" ? "flex-row-reverse" : ""
                  }`}
                >
                  <Avatar className="h-8 w-8 shrink-0">
                    <AvatarFallback
                      className={
                        message.role === "mentor"
                          ? "bg-gradient-to-br from-violet-500 to-indigo-600 text-white"
                          : "bg-emerald-500 text-white"
                      }
                    >
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
                    <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none [&>p]:mb-2 [&>p:last-child]:mb-0">
                      {message.content}
                    </ReactMarkdown>
                    <p className="text-[10px] text-muted-foreground mt-2">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3"
              >
                <Avatar className="h-8 w-8 shrink-0">
                  <AvatarFallback className="bg-gradient-to-br from-violet-500 to-indigo-600 text-white">
                    🧠
                  </AvatarFallback>
                </Avatar>
                <div className="bg-muted/50 rounded-2xl p-4">
                  <div className="flex items-center gap-1">
                    <span
                      className="h-2 w-2 bg-violet-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    />
                    <span
                      className="h-2 w-2 bg-violet-500 rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    />
                    <span
                      className="h-2 w-2 bg-violet-500 rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </ScrollArea>

        {/* Quick Prompts */}
        {messages.length <= 1 && (
          <div className="px-4 pb-2">
            <div className="max-w-3xl mx-auto">
              <p className="text-xs text-muted-foreground mb-2">Quick prompts:</p>
              <div className="flex flex-wrap gap-2">
                {quickPrompts.map((prompt) => (
                  <Button
                    key={prompt.label}
                    variant="outline"
                    size="sm"
                    className="text-xs"
                    onClick={() => setInput(prompt.prompt)}
                  >
                    <prompt.icon className="h-3 w-3 mr-1" />
                    {prompt.label}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t p-4 shrink-0">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask your mentor anything..."
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
                  onClick={() => handleSendMessage()}
                  disabled={!input.trim() || isTyping}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              VidyaGuru uses the Socratic method to help you learn through discovery
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
