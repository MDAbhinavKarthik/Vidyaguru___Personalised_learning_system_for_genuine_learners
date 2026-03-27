/**
 * API Service for dashboard and learning data
 */

const API_BASE = "/api/v1";

const getAuthHeaders = () => ({
  "Authorization": `Bearer ${
    typeof window !== "undefined" ? localStorage.getItem("token") : ""
  }`,
  "Content-Type": "application/json",
});

// Progress API
export const progressAPI = {
  getOverview: async () => {
    const res = await fetch(`${API_BASE}/progress/overview`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch progress overview");
    return res.json();
  },

  getAnalytics: async () => {
    const res = await fetch(`${API_BASE}/progress/analytics`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch analytics");
    return res.json();
  },

  getSkills: async () => {
    const res = await fetch(`${API_BASE}/progress/skills`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch skills");
    return res.json();
  },

  getAchievements: async () => {
    const res = await fetch(`${API_BASE}/progress/achievements`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch achievements");
    return res.json();
  },

  getStreak: async () => {
    const res = await fetch(`${API_BASE}/progress/streak`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch streak");
    return res.json();
  },
};

// Learning Paths API
export const learningAPI = {
  getPaths: async (params?: Record<string, any>) => {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          query.append(key, String(value));
        }
      });
    }
    const res = await fetch(`${API_BASE}/learning/paths?${query}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch learning paths");
    return res.json();
  },

  getPathDetail: async (pathId: string) => {
    const res = await fetch(`${API_BASE}/learning/paths/${pathId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch path details");
    return res.json();
  },

  enrollPath: async (pathId: string) => {
    const res = await fetch(`${API_BASE}/learning/paths/${pathId}/enroll`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to enroll");
    return res.json();
  },

  explorePaths: async (params?: Record<string, any>) => {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          query.append(key, String(value));
        }
      });
    }
    const res = await fetch(`${API_BASE}/learning/paths/explore?${query}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch explore paths");
    return res.json();
  },
};

// Tasks API
export const tasksAPI = {
  getTasks: async (params?: Record<string, any>) => {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          query.append(key, String(value));
        }
      });
    }
    const res = await fetch(`${API_BASE}/tasks?${query}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch tasks");
    return res.json();
  },

  getDailyTasks: async () => {
    const res = await fetch(`${API_BASE}/tasks/daily`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch daily tasks");
    return res.json();
  },

  getTaskDetail: async (taskId: string) => {
    const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch task detail");
    return res.json();
  },

  submitTask: async (taskId: string, solution: any) => {
    const res = await fetch(`${API_BASE}/tasks/${taskId}/submit`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(solution),
    });
    if (!res.ok) throw new Error("Failed to submit task");
    return res.json();
  },
};

// Journal API
export const journalAPI = {
  getEntries: async (params?: Record<string, any>) => {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          query.append(key, String(value));
        }
      });
    }
    const res = await fetch(`${API_BASE}/journal/entries?${query}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch journal entries");
    return res.json();
  },

  getEntryDetail: async (entryId: string) => {
    const res = await fetch(`${API_BASE}/journal/entries/${entryId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch entry");
    return res.json();
  },

  createEntry: async (data: any) => {
    const res = await fetch(`${API_BASE}/journal/entries`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create entry");
    return res.json();
  },

  updateEntry: async (entryId: string, data: any) => {
    const res = await fetch(`${API_BASE}/journal/entries/${entryId}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update entry");
    return res.json();
  },

  deleteEntry: async (entryId: string) => {
    const res = await fetch(`${API_BASE}/journal/entries/${entryId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete entry");
    return res.json();
  },

  getInsights: async () => {
    const res = await fetch(`${API_BASE}/journal/insights`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch insights");
    return res.json();
  },
};

// Mentor API
export const mentorAPI = {
  chat: async (message: string, conversationId?: string) => {
    const res = await fetch(`${API_BASE}/mentor/chat`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        include_wisdom: true,
      }),
    });
    if (!res.ok) throw new Error("Failed to send message");
    return res.json();
  },

  getConversations: async (limit = 10, offset = 0) => {
    const res = await fetch(`${API_BASE}/mentor/conversations?limit=${limit}&offset=${offset}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch conversations");
    return res.json();
  },

  getConversationDetail: async (conversationId: string) => {
    const res = await fetch(`${API_BASE}/mentor/conversations/${conversationId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch conversation");
    return res.json();
  },
};
