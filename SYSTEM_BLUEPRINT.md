# AI-Powered Interactive Learning Platform
## Complete System Blueprint

---

## 1. System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Web App    │  │  Mobile App  │  │  Desktop App │  │   Browser    │        │
│  │   (React)    │  │ (React Native)│  │  (Electron)  │  │  Extension   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                    Kong / AWS API Gateway / Nginx                        │  │
│  │         • Rate Limiting  • Auth Validation  • Load Balancing            │  │
│  │         • Request Routing  • SSL Termination  • Logging                 │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MICROSERVICES LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │    Auth     │ │   User      │ │   Learning  │ │  AI Mentor  │              │
│  │   Service   │ │   Service   │ │   Engine    │ │   Service   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │    Task     │ │  Industry   │ │   Idea      │ │  Progress   │              │
│  │  Management │ │  Challenge  │ │   Journal   │ │  Tracker    │              │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │  Reminder   │ │ Anti-Cheat  │ │   Ancient   │ │ Notification│              │
│  │   Service   │ │   Engine    │ │  Knowledge  │ │   Service   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MESSAGE QUEUE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │              Apache Kafka / RabbitMQ / Redis Pub/Sub                     │  │
│  │    • Event Streaming  • Async Processing  • Service Communication       │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  PostgreSQL  │  │   MongoDB    │  │    Redis     │  │ Elasticsearch│        │
│  │  (Primary)   │  │  (Content)   │  │   (Cache)    │  │  (Search)    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                                  │
│  ┌──────────────┐  ┌──────────────┐                                             │
│  │   AWS S3     │  │   Pinecone   │                                             │
│  │(File Storage)│  │  (Vectors)   │                                             │
│  └──────────────┘  └──────────────┘                                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI/ML LAYER                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  LLM APIs    │  │   Custom     │  │   ML Model   │  │   Speech     │        │
│  │ (GPT/Claude) │  │   Models     │  │   Pipeline   │  │  Processing  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

| Principle | Description |
|-----------|-------------|
| **Microservices** | Each feature as independent deployable service |
| **Event-Driven** | Asynchronous communication via message queues |
| **Domain-Driven Design** | Bounded contexts for each learning domain |
| **CQRS** | Separate read/write operations for scalability |
| **Zero Trust Security** | Verify every request, no implicit trust |

---

## 2. Technology Stack

### Frontend Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | React 18 + TypeScript | Component-based UI |
| **State Management** | Zustand / Redux Toolkit | Global state |
| **Styling** | Tailwind CSS + Shadcn/UI | Modern UI components |
| **Code Editor** | Monaco Editor | In-browser coding |
| **Charts** | Recharts / D3.js | Progress visualization |
| **Real-time** | Socket.io Client | Live chat/updates |
| **Mobile** | React Native | Cross-platform mobile |

### Backend Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Runtime** | Node.js / Python FastAPI | API Services |
| **Framework** | NestJS / Express | Microservices |
| **Auth** | JWT + OAuth 2.0 + Passport.js | Authentication |
| **ORM** | Prisma / TypeORM | Database abstraction |
| **Validation** | Zod / Joi | Request validation |
| **Documentation** | Swagger/OpenAPI | API docs |

### AI/ML Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Primary LLM** | GPT-4o / Claude 3.5 | Mentor conversations |
| **Embeddings** | OpenAI Ada / Cohere | Semantic search |
| **Vector DB** | Pinecone / Weaviate | Knowledge retrieval |
| **Fine-tuning** | LoRA / QLoRA | Domain-specific models |
| **Speech** | Whisper + TTS | Voice interactions |
| **Plagiarism** | Custom ML Pipeline | Anti-cheat detection |

### Infrastructure Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Cloud** | AWS / GCP / Azure | Hosting |
| **Containers** | Docker + Kubernetes | Orchestration |
| **CI/CD** | GitHub Actions | Deployment pipeline |
| **Monitoring** | Prometheus + Grafana | Observability |
| **Logging** | ELK Stack | Centralized logging |
| **CDN** | Cloudflare | Global content delivery |

### Database Stack

| Database | Type | Use Case |
|----------|------|----------|
| **PostgreSQL** | Relational | Users, transactions, structured data |
| **MongoDB** | Document | Learning content, journal entries |
| **Redis** | In-memory | Caching, sessions, rate limiting |
| **Elasticsearch** | Search | Full-text search, analytics |
| **Pinecone** | Vector | Semantic search, RAG |
| **TimescaleDB** | Time-series | Progress analytics |

---

## 3. Service Modules

### 3.1 Authentication Service

```
┌────────────────────────────────────────────────────────────┐
│                   AUTH SERVICE                             │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── POST /auth/register                                   │
│  ├── POST /auth/login                                      │
│  ├── POST /auth/logout                                     │
│  ├── POST /auth/refresh-token                              │
│  ├── POST /auth/forgot-password                            │
│  ├── POST /auth/reset-password                             │
│  ├── POST /auth/verify-email                               │
│  ├── GET  /auth/oauth/google                               │
│  ├── GET  /auth/oauth/github                               │
│  └── POST /auth/2fa/enable                                 │
├────────────────────────────────────────────────────────────┤
│  Features:                                                 │
│  • Multi-factor authentication (TOTP/SMS)                  │
│  • OAuth integration (Google, GitHub, LinkedIn)            │
│  • Session management with Redis                           │
│  • Rate limiting per IP/user                               │
│  • Password strength validation                            │
│  • Account lockout after failed attempts                   │
└────────────────────────────────────────────────────────────┘
```

### 3.2 User Service

```
┌────────────────────────────────────────────────────────────┐
│                   USER SERVICE                             │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── GET    /users/me                                      │
│  ├── PATCH  /users/me                                      │
│  ├── GET    /users/me/profile                              │
│  ├── PUT    /users/me/preferences                          │
│  ├── GET    /users/me/learning-style                       │
│  ├── POST   /users/me/onboarding                           │
│  └── DELETE /users/me                                      │
├────────────────────────────────────────────────────────────┤
│  Features:                                                 │
│  • Learning style assessment (VAK model)                   │
│  • Skill level profiling                                   │
│  • Interest categorization                                 │
│  • Goal setting and tracking                               │
│  • Notification preferences                                │
│  • Privacy settings management                             │
└────────────────────────────────────────────────────────────┘
```

### 3.3 AI Mentor Service

```
┌────────────────────────────────────────────────────────────┐
│                 AI MENTOR SERVICE                          │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── POST   /mentor/chat                                   │
│  ├── POST   /mentor/chat/stream                            │
│  ├── GET    /mentor/conversations                          │
│  ├── GET    /mentor/conversations/:id                      │
│  ├── DELETE /mentor/conversations/:id                      │
│  ├── POST   /mentor/explain                                │
│  ├── POST   /mentor/quiz                                   │
│  ├── POST   /mentor/code-review                            │
│  ├── POST   /mentor/voice                                  │
│  └── GET    /mentor/suggestions                            │
├────────────────────────────────────────────────────────────┤
│  Core Components:                                          │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              MENTOR ORCHESTRATOR                    │  │
│  │  • Context Management                               │  │
│  │  • Intent Classification                            │  │
│  │  • Response Generation                              │  │
│  │  • Socratic Questioning Engine                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                          │                                 │
│            ┌─────────────┼─────────────┐                  │
│            ▼             ▼             ▼                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │   Teaching   │ │   Concept    │ │    Code      │      │
│  │    Agent     │ │   Explainer  │ │   Reviewer   │      │
│  └──────────────┘ └──────────────┘ └──────────────┘      │
├────────────────────────────────────────────────────────────┤
│  Teaching Strategies:                                      │
│  • Socratic Method - Guide through questions               │
│  • Scaffolding - Build on existing knowledge               │
│  • Spaced Repetition - Optimal review timing               │
│  • Active Recall - Encourage retrieval practice            │
│  • Elaborative Interrogation - "Why does this work?"       │
│  • Interleaving - Mix related topics                       │
└────────────────────────────────────────────────────────────┘
```

**Mentor Prompt Engineering System:**

```python
MENTOR_SYSTEM_PROMPT = """
You are VidyaGuru (विद्यागुरु), an AI learning mentor designed to promote 
genuine understanding over memorization.

CORE TEACHING PRINCIPLES:
1. NEVER give direct answers - guide through Socratic questioning
2. Assess current understanding before explaining
3. Break complex topics into digestible chunks
4. Use analogies from student's domain of interest
5. Celebrate effort, not just correctness
6. Identify and address misconceptions gently
7. Encourage the learner to verbalize their thinking

RESPONSE FRAMEWORK:
- Acknowledge: Recognize what the student understands
- Question: Ask probing questions to deepen thinking
- Guide: Provide hints, not answers
- Connect: Link to previously learned concepts
- Challenge: Push for deeper exploration

ANTI-CHEATING INTEGRATION:
- If student shows sudden expertise jump, probe deeper
- Request explanations of solutions in own words
- Vary question formats to ensure real understanding
- Track reasoning process, not just final answers

COMMUNICATION STYLE:
- Warm but intellectually challenging
- Patient with genuine struggles
- Firm against shortcut-seeking
- Culturally relevant examples
- Include wisdom from Indian philosophical traditions when appropriate
"""
```

### 3.4 Learning Engine Service

```
┌────────────────────────────────────────────────────────────┐
│                 LEARNING ENGINE SERVICE                    │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── GET    /learning/paths                                │
│  ├── POST   /learning/paths/generate                       │
│  ├── GET    /learning/paths/:id                            │
│  ├── GET    /learning/modules                              │
│  ├── GET    /learning/modules/:id/content                  │
│  ├── POST   /learning/modules/:id/complete                 │
│  ├── GET    /learning/recommendations                      │
│  ├── POST   /learning/assessment                           │
│  └── GET    /learning/knowledge-graph                      │
├────────────────────────────────────────────────────────────┤
│  Adaptive Learning Algorithm:                              │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           LEARNING PATH GENERATOR                   │  │
│  │                                                     │  │
│  │  Input:                                             │  │
│  │  • User skill assessment                            │  │
│  │  • Learning goals                                   │  │
│  │  • Learning style (visual/auditory/kinesthetic)    │  │
│  │  • Available time commitment                        │  │
│  │  • Prior knowledge graph                            │  │
│  │                                                     │  │
│  │  Output:                                            │  │
│  │  • Personalized curriculum                          │  │
│  │  • Milestone-based progression                      │  │
│  │  • Dynamic difficulty adjustment                    │  │
│  │  • Spaced repetition schedule                       │  │
│  └─────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────┤
│  Content Types:                                            │
│  • Interactive lessons with embedded exercises             │
│  • Video explanations with comprehension checks           │
│  • Hands-on coding environments (sandboxed)               │
│  • Visual concept maps                                     │
│  • Audio explanations for accessibility                   │
│  • Gamified quizzes                                        │
└────────────────────────────────────────────────────────────┘
```

### 3.5 Task Management Service

```
┌────────────────────────────────────────────────────────────┐
│               TASK MANAGEMENT SERVICE                      │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── GET    /tasks                                         │
│  ├── POST   /tasks                                         │
│  ├── GET    /tasks/:id                                     │
│  ├── PATCH  /tasks/:id                                     │
│  ├── DELETE /tasks/:id                                     │
│  ├── POST   /tasks/:id/submit                              │
│  ├── GET    /tasks/:id/feedback                            │
│  ├── POST   /tasks/:id/request-hint                        │
│  └── GET    /tasks/daily                                   │
├────────────────────────────────────────────────────────────┤
│  Task Types:                                               │
│                                                            │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │   LEARNING    │  │   PRACTICE    │  │   PROJECT     │  │
│  │    TASKS      │  │    TASKS      │  │    TASKS      │  │
│  ├───────────────┤  ├───────────────┤  ├───────────────┤  │
│  │ • Read module │  │ • Code kata   │  │ • Mini project│  │
│  │ • Watch video │  │ • Debug code  │  │ • Build app   │  │
│  │ • Complete    │  │ • Refactor    │  │ • System      │  │
│  │   tutorial    │  │ • Algorithm   │  │   design      │  │
│  │ • Review      │  │   challenge   │  │ • Capstone    │  │
│  │   concept     │  │ • MCQ quiz    │  │   project     │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
├────────────────────────────────────────────────────────────┤
│  Evaluation System:                                        │
│  • Automated code testing (unit tests)                     │
│  • AI-powered code review                                  │
│  • Peer review matching                                    │
│  • Rubric-based assessment                                 │
│  • Explanation requirement (anti-cheat)                    │
└────────────────────────────────────────────────────────────┘
```

### 3.6 Industry Challenge Service

```
┌────────────────────────────────────────────────────────────┐
│             INDUSTRY CHALLENGE SERVICE                     │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── GET    /challenges                                    │
│  ├── GET    /challenges/categories                         │
│  ├── GET    /challenges/:id                                │
│  ├── POST   /challenges/:id/start                          │
│  ├── POST   /challenges/:id/submit                         │
│  ├── GET    /challenges/:id/leaderboard                    │
│  ├── POST   /challenges/generate                           │
│  └── GET    /challenges/sponsored                          │
├────────────────────────────────────────────────────────────┤
│  Challenge Generator Pipeline:                             │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                                                      │ │
│  │   Industry Trends  ──►  Problem                      │ │
│  │        API              Generator ──► Validation ──► │ │
│  │                              │          Engine       │ │
│  │   Job Postings ────►        │                        │ │
│  │                              │                        │ │
│  │   Tech News ───────►        │                        │ │
│  │                              ▼                        │ │
│  │                     Difficulty Calibration           │ │
│  │                              │                        │ │
│  │                              ▼                        │ │
│  │                     Challenge Repository             │ │
│  │                                                      │ │
│  └──────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│  Challenge Categories:                                     │
│  • System Design (e.g., "Design Twitter's trending algo")  │
│  • Data Engineering (e.g., "Build ETL pipeline")           │
│  • API Development (e.g., "Rate limiter implementation")   │
│  • Algorithm Optimization (e.g., "Search autocomplete")    │
│  • Security Challenges (e.g., "Find vulnerabilities")      │
│  • DevOps Scenarios (e.g., "Zero-downtime deployment")     │
│  • ML Problems (e.g., "Recommendation system")             │
└────────────────────────────────────────────────────────────┘
```

### 3.7 Idea Journal Service

```
┌────────────────────────────────────────────────────────────┐
│                IDEA JOURNAL SERVICE                        │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── GET    /journal/entries                               │
│  ├── POST   /journal/entries                               │
│  ├── GET    /journal/entries/:id                           │
│  ├── PATCH  /journal/entries/:id                           │
│  ├── DELETE /journal/entries/:id                           │
│  ├── POST   /journal/entries/:id/reflect                   │
│  ├── GET    /journal/insights                              │
│  ├── GET    /journal/tags                                  │
│  └── POST   /journal/voice-to-text                         │
├────────────────────────────────────────────────────────────┤
│  Entry Types:                                              │
│  • 💡 Idea - New concept or project idea                   │
│  • 📝 Note - Quick learning note                           │
│  • 🔗 Connection - Link between concepts                   │
│  • ❓ Question - Unanswered curiosity                      │
│  • 💪 Achievement - Milestone reached                      │
│  • 🐛 Bug Log - Debugging journey                          │
│  • 🎯 Goal - Future target                                 │
├────────────────────────────────────────────────────────────┤
│  AI-Powered Features:                                      │
│  • Auto-tagging and categorization                         │
│  • Weekly reflection summaries                             │
│  • Pattern detection in learning journey                   │
│  • Connection suggestions between entries                  │
│  • "Today's Insight" based on journal analysis             │
│  • Export as portfolio/documentation                       │
└────────────────────────────────────────────────────────────┘
```

### 3.8 Progress Tracker Service

```
┌────────────────────────────────────────────────────────────┐
│               PROGRESS TRACKER SERVICE                     │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── GET    /progress/overview                             │
│  ├── GET    /progress/skills                               │
│  ├── GET    /progress/timeline                             │
│  ├── GET    /progress/streaks                              │
│  ├── GET    /progress/achievements                         │
│  ├── GET    /progress/analytics                            │
│  ├── GET    /progress/compare                              │
│  └── POST   /progress/milestone                            │
├────────────────────────────────────────────────────────────┤
│  Metrics Tracked:                                          │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  LEARNING METRICS                                    │ │
│  │  • Time spent learning (active vs passive)           │ │
│  │  • Modules completed / in progress                   │ │
│  │  • Quiz scores and improvement trends                │ │
│  │  • Code quality scores over time                     │ │
│  │  • Concept mastery levels (Bloom's taxonomy)         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  ENGAGEMENT METRICS                                  │ │
│  │  • Daily/weekly streaks                              │ │
│  │  • Consistency score                                 │ │
│  │  • Challenge participation                           │ │
│  │  • Mentor interaction frequency                      │ │
│  │  • Journal entry frequency                           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  SKILL METRICS                                       │ │
│  │  • Skill radar chart                                 │ │
│  │  • Strength/weakness analysis                        │ │
│  │  • Industry readiness score                          │ │
│  │  • Communication skill rating                        │ │
│  │  • Problem-solving proficiency                       │ │
│  └──────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│  Gamification Elements:                                    │
│  • XP points for activities                                │
│  • Achievement badges                                      │
│  • Skill trees visualization                               │
│  • Leaderboards (optional, privacy-aware)                  │
│  • Milestone celebrations                                  │
└────────────────────────────────────────────────────────────┘
```

### 3.9 Anti-Cheat Detection Service

```
┌────────────────────────────────────────────────────────────┐
│              ANTI-CHEAT DETECTION SERVICE                  │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── POST   /integrity/analyze-submission                  │
│  ├── POST   /integrity/verify-understanding                │
│  ├── GET    /integrity/user-profile/:id                    │
│  ├── POST   /integrity/flag-review                         │
│  └── GET    /integrity/reports                             │
├────────────────────────────────────────────────────────────┤
│  Detection Mechanisms:                                     │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  BEHAVIORAL ANALYSIS                                 │ │
│  │  • Typing pattern analysis                           │ │
│  │  • Time-to-solution correlation                      │ │
│  │  • Copy-paste detection                              │ │
│  │  • Tab switching monitoring (with consent)           │ │
│  │  • Sudden skill level jumps                          │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  CODE ANALYSIS                                       │ │
│  │  • Plagiarism detection (MOSS-like)                  │ │
│  │  • Style consistency checking                        │ │
│  │  • Solution fingerprinting                           │ │
│  │  • AI-generated code detection                       │ │
│  │  • Code complexity vs skill level matching           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  UNDERSTANDING VERIFICATION                          │ │
│  │  • Follow-up questioning                             │ │
│  │  • Explain-your-code challenges                      │ │
│  │  • Variation problems                                │ │
│  │  • Verbal explanation requests                       │ │
│  │  • Random concept probing                            │ │
│  └──────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│  Philosophy:                                               │
│  "Not to punish, but to guide back to genuine learning"    │
│                                                            │
│  Response Actions:                                         │
│  • Gentle reminder about learning goals                    │
│  • Redirect to foundational concepts                       │
│  • Increase verification frequency temporarily             │
│  • Suggest easier challenge level                          │
│  • Human mentor flag for persistent cases                  │
└────────────────────────────────────────────────────────────┘
```

### 3.10 Ancient Indian Knowledge Service

```
┌────────────────────────────────────────────────────────────┐
│           ANCIENT INDIAN KNOWLEDGE SERVICE                 │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── GET    /wisdom/daily                                  │
│  ├── GET    /wisdom/topic/:topic                           │
│  ├── GET    /wisdom/random                                 │
│  ├── GET    /wisdom/search                                 │
│  └── POST   /wisdom/contextualize                          │
├────────────────────────────────────────────────────────────┤
│  Knowledge Categories:                                     │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  LEARNING & WISDOM                                   │ │
│  │  • Vidya (विद्या) - Knowledge traditions             │ │
│  │  • Guru-Shishya Parampara - Teacher-student bond     │ │
│  │  • Shruti & Smriti - Ways of knowing                 │ │
│  │  • Nyaya - Logic and reasoning                       │ │
│  │  • Mimamsa - Critical inquiry                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  SCIENTIFIC CONTRIBUTIONS                            │ │
│  │  • Mathematics (Aryabhata, Brahmagupta)              │ │
│  │  • Astronomy (Surya Siddhanta)                       │ │
│  │  • Medicine (Ayurveda, Sushruta)                     │ │
│  │  • Metallurgy (Iron pillar, Wootz steel)             │ │
│  │  • Architecture (Vastu Shastra)                      │ │
│  │  • Linguistics (Panini's grammar)                    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  PHILOSOPHICAL INSIGHTS                              │ │
│  │  • Karma - Action and consequence                    │ │
│  │  • Dharma - Righteous conduct                        │ │
│  │  • Tapas - Disciplined effort                        │ │
│  │  • Shraddha - Faith with understanding               │ │
│  │  • Viveka - Discrimination/discernment               │ │
│  └──────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│  Integration Points:                                       │
│  • Daily wisdom notification                               │
│  • Context-relevant quotes during learning                 │
│  • Historical context for CS concepts                      │
│  • Meditation/focus techniques for study                   │
│  • Ethical AI discussions with philosophical roots         │
└────────────────────────────────────────────────────────────┘
```

### 3.11 Reminder & Notification Service

```
┌────────────────────────────────────────────────────────────┐
│            REMINDER & NOTIFICATION SERVICE                 │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── GET    /reminders                                     │
│  ├── POST   /reminders                                     │
│  ├── PATCH  /reminders/:id                                 │
│  ├── DELETE /reminders/:id                                 │
│  ├── GET    /notifications                                 │
│  ├── PATCH  /notifications/:id/read                        │
│  └── PUT    /notifications/preferences                     │
├────────────────────────────────────────────────────────────┤
│  Reminder Types:                                           │
│  • Study session reminders                                 │
│  • Spaced repetition reviews                               │
│  • Task deadline alerts                                    │
│  • Streak maintenance nudges                               │
│  • Challenge participation prompts                         │
│  • Weekly reflection prompts                               │
├────────────────────────────────────────────────────────────┤
│  Notification Channels:                                    │
│  • In-app notifications                                    │
│  • Push notifications (PWA/mobile)                         │
│  • Email digests (daily/weekly)                            │
│  • SMS (optional, critical only)                           │
│  • Calendar integration (Google/Outlook)                   │
├────────────────────────────────────────────────────────────┤
│  Smart Scheduling:                                         │
│  • Optimal study time detection                            │
│  • Fatigue-aware scheduling                                │
│  • Time zone handling                                      │
│  • Focus mode integration                                  │
└────────────────────────────────────────────────────────────┘
```

### 3.12 Communication Skills Service

```
┌────────────────────────────────────────────────────────────┐
│            COMMUNICATION SKILLS SERVICE                    │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                │
│  ├── POST   /communication/analyze-text                    │
│  ├── POST   /communication/mock-interview                  │
│  ├── POST   /communication/presentation-feedback           │
│  ├── GET    /communication/exercises                       │
│  ├── POST   /communication/voice-analysis                  │
│  └── GET    /communication/progress                        │
├────────────────────────────────────────────────────────────┤
│  Features:                                                 │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  WRITTEN COMMUNICATION                               │ │
│  │  • Technical writing exercises                       │ │
│  │  • Documentation review                              │ │
│  │  • Email etiquette training                          │ │
│  │  • Code comment quality analysis                     │ │
│  │  • README writing practice                           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  VERBAL COMMUNICATION                                │ │
│  │  • Mock technical interviews                         │ │
│  │  • System design explanation practice                │ │
│  │  • Code walkthrough simulation                       │ │
│  │  • Presentation skills training                      │ │
│  │  • Voice clarity analysis                            │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  COLLABORATIVE COMMUNICATION                         │ │
│  │  • Code review etiquette                             │ │
│  │  • Feedback giving/receiving                         │ │
│  │  • Team discussion simulation                        │ │
│  │  • Conflict resolution scenarios                     │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 4. Interaction Flow

### 4.1 User Onboarding Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER ONBOARDING FLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

     ┌──────────┐
     │  START   │
     └────┬─────┘
          │
          ▼
┌─────────────────────┐     ┌─────────────────────┐
│   Registration      │────►│   Email/OAuth       │
│   • Email           │     │   Verification      │
│   • OAuth (Google,  │     └──────────┬──────────┘
│     GitHub)         │                │
└─────────────────────┘                ▼
                            ┌─────────────────────┐
                            │  Welcome Screen     │
                            │  • Platform intro   │
                            │  • Value proposition│
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  Profile Setup      │
                            │  • Name, photo      │
                            │  • Current role     │
                            │  • Experience level │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  Learning Style     │
                            │  Assessment         │
                            │  • Visual/Auditory/ │
                            │    Kinesthetic quiz │
                            │  • Time availability│
                            │  • Learning pace    │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  Skill Assessment   │
                            │  • Topic selection  │
                            │  • Diagnostic quiz  │
                            │  • Code challenge   │
                            │    (optional)       │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  Goal Setting       │
                            │  • Learning goals   │
                            │  • Timeline         │
                            │  • Career objective │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  AI Mentor Intro    │
                            │  • Meet VidyaGuru   │
                            │  • Sample convo     │
                            │  • Set expectations │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  Learning Path      │
                            │  Generated          │
                            │  • Personalized     │
                            │    curriculum       │
                            │  • First tasks      │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  DASHBOARD          │
                            │  (Learning begins)  │
                            └─────────────────────┘
```

### 4.2 Daily Learning Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DAILY LEARNING FLOW                               │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│    User Login                                                             │
│        │                                                                  │
│        ▼                                                                  │
│   ┌─────────────────────────────────────────────────────────────────┐    │
│   │                      DASHBOARD                                   │    │
│   ├─────────────────────────────────────────────────────────────────┤    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │    │
│   │  │ Daily       │  │ Streak      │  │ Ancient Wisdom Quote    │ │    │
│   │  │ Progress    │  │ Counter     │  │ of the Day              │ │    │
│   │  │ Ring        │  │ 🔥 15 days  │  │ "विद्या ददाति विनयम्"  │ │    │
│   │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │    │
│   │                                                                  │    │
│   │  ┌───────────────────────────────────────────────────────────┐ │    │
│   │  │  TODAY'S RECOMMENDED ACTIVITIES                           │ │    │
│   │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │ │    │
│   │  │  │ □ Continue   │ │ □ Review     │ │ □ Practice   │      │ │    │
│   │  │  │   Module 3   │ │   Concepts   │ │   Challenge  │      │ │    │
│   │  │  │   (25 min)   │ │   (10 min)   │ │   (15 min)   │      │ │    │
│   │  │  └──────────────┘ └──────────────┘ └──────────────┘      │ │    │
│   │  └───────────────────────────────────────────────────────────┘ │    │
│   └─────────────────────────────────────────────────────────────────┘    │
│        │                                                                  │
│        ├────────────────┬────────────────┬────────────────┐              │
│        ▼                ▼                ▼                ▼              │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌──────────┐          │
│   │ Learn   │     │ Practice│     │Challenge│     │ AI Mentor│          │
│   │ Module  │     │ Task    │     │ Arena   │     │ Chat     │          │
│   └────┬────┘     └────┬────┘     └────┬────┘     └────┬─────┘          │
│        │               │               │               │                 │
│        ▼               ▼               ▼               ▼                 │
│   ┌──────────────────────────────────────────────────────────┐          │
│   │              INTERACTION LOOP                             │          │
│   │                                                           │          │
│   │   ┌─────────┐    ┌─────────┐    ┌─────────┐             │          │
│   │   │ Content │───►│ Practice│───►│ Verify  │             │          │
│   │   │ Consume │    │ Apply   │    │ Underst.│             │          │
│   │   └─────────┘    └────┬────┘    └────┬────┘             │          │
│   │                       │              │                   │          │
│   │                       ▼              ▼                   │          │
│   │               ┌───────────────────────────┐             │          │
│   │               │   Anti-Cheat Check        │             │          │
│   │               │   • Explanation required  │             │          │
│   │               │   • Follow-up questions   │             │          │
│   │               └───────────────────────────┘             │          │
│   │                           │                              │          │
│   │                           ▼                              │          │
│   │               ┌───────────────────────────┐             │          │
│   │               │   Progress Update         │             │          │
│   │               │   • XP earned             │             │          │
│   │               │   • Skill level adjusted  │             │          │
│   │               │   • Next recommendation   │             │          │
│   │               └───────────────────────────┘             │          │
│   └──────────────────────────────────────────────────────────┘          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 4.3 AI Mentor Conversation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AI MENTOR CONVERSATION FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

   User Input (Text/Voice)
          │
          ▼
   ┌──────────────────────┐
   │  Input Processing    │
   │  • Speech-to-text    │
   │  • Intent detection  │
   │  • Entity extraction │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐     ┌──────────────────────┐
   │  Context Builder     │────►│  User Profile        │
   │  • Conversation hist │     │  • Skill level       │
   │  • Current topic     │     │  • Learning style    │
   │  • Recent activities │     │  • Progress data     │
   └──────────┬───────────┘     └──────────────────────┘
              │
              ▼
   ┌──────────────────────┐
   │  Intent Router       │
   └──────────┬───────────┘
              │
    ┌─────────┼─────────┬─────────────┬──────────────┐
    ▼         ▼         ▼             ▼              ▼
┌────────┐┌────────┐┌────────┐  ┌────────┐    ┌────────┐
│Concept ││ Debug  ││ Code   │  │ Quiz   │    │General │
│Explain ││ Help   ││ Review │  │Request │    │  Chat  │
└───┬────┘└───┬────┘└───┬────┘  └───┬────┘    └───┬────┘
    │         │         │           │             │
    └─────────┴─────────┴─────┬─────┴─────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │    SOCRATIC ENGINE        │
              │                           │
              │  Before giving info:      │
              │  1. "What do you already  │
              │     know about X?"        │
              │  2. "Why do you think     │
              │     this happens?"        │
              │  3. "Can you explain      │
              │     your approach?"       │
              │                           │
              │  Teaching strategy:       │
              │  • Guide, don't tell      │
              │  • Ask leading questions  │
              │  • Encourage exploration  │
              └───────────┬───────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │   RAG Retrieval           │
              │   • Learning content      │
              │   • Ancient wisdom        │
              │   • Code examples         │
              │   • User's past notes     │
              └───────────┬───────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │   Response Generation     │
              │   (LLM with system prompt)│
              └───────────┬───────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │   Response Enhancement    │
              │   • Add relevant quote    │
              │   • Suggest next step     │
              │   • Include reflection Q  │
              └───────────┬───────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │   Integrity Check         │
              │   • Is student seeking    │
              │     shortcut?             │
              │   • Schedule follow-up    │
              │     verification          │
              └───────────┬───────────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │   Response Delivery       │
              │   • Text / Voice          │
              │   • Code highlighting     │
              │   • Visual aids           │
              └───────────────────────────┘
```

### 4.4 Task Submission & Evaluation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   TASK SUBMISSION & EVALUATION FLOW                      │
└─────────────────────────────────────────────────────────────────────────┘

   Task Assignment
          │
          ▼
   ┌──────────────────────┐
   │  User Works on Task  │
   │  • Code editor       │
   │  • Time tracking     │
   │  • Hint requests     │
   │  • Typing patterns   │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │  Submission          │
   │  • Code/Answer       │
   │  • Self-assessment   │
   │  • Confidence level  │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────────────────────────────────┐
   │              EVALUATION PIPELINE                  │
   │                                                   │
   │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
   │  │ Automated   │  │ Plagiarism  │  │ AI Code  │ │
   │  │ Tests       │  │ Check       │  │ Review   │ │
   │  │ (Unit/Int)  │  │ (MOSS-like) │  │          │ │
   │  └──────┬──────┘  └──────┬──────┘  └────┬─────┘ │
   │         │                │               │       │
   │         └────────────────┼───────────────┘       │
   │                          │                       │
   │                          ▼                       │
   │              ┌───────────────────────┐          │
   │              │ Combined Score        │          │
   │              │ • Correctness (40%)   │          │
   │              │ • Code quality (30%)  │          │
   │              │ • Originality (20%)   │          │
   │              │ • Efficiency (10%)    │          │
   │              └───────────┬───────────┘          │
   └──────────────────────────┼──────────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  Understanding Check      │
              │  (if flagged or random)   │
              │                           │
              │  "Explain line 15-20"     │
              │  "What would happen if X?"│
              │  "Can you modify it to Y?"│
              └───────────┬───────────────┘
                          │
           ┌──────────────┴──────────────┐
           ▼                             ▼
   ┌───────────────┐            ┌───────────────┐
   │   Passed      │            │   Needs Work  │
   │   ✓ XP earned │            │   • Feedback  │
   │   ✓ Progress  │            │   • Hints     │
   │   ✓ Next task │            │   • Retry     │
   └───────────────┘            └───────────────┘
```

---

## 5. Database Overview

### 5.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ENTITY RELATIONSHIP DIAGRAM                           │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌──────────────────┐
│      USERS       │          │   USER_PROFILES  │
├──────────────────┤          ├──────────────────┤
│ id (PK)          │──────────│ user_id (FK)     │
│ email            │          │ display_name     │
│ password_hash    │          │ avatar_url       │
│ oauth_provider   │          │ learning_style   │
│ oauth_id         │          │ experience_level │
│ email_verified   │          │ time_commitment  │
│ two_factor_secret│          │ goals            │
│ created_at       │          │ preferences      │
│ last_login       │          │ timezone         │
└────────┬─────────┘          └──────────────────┘
         │
         │
         │ 1:N
         ▼
┌──────────────────┐          ┌──────────────────┐
│  LEARNING_PATHS  │          │    MODULES       │
├──────────────────┤          ├──────────────────┤
│ id (PK)          │──────────│ id (PK)          │
│ user_id (FK)     │   1:N    │ path_id (FK)     │
│ title            │          │ title            │
│ description      │          │ description      │
│ status           │          │ content_type     │
│ progress_pct     │          │ difficulty       │
│ created_at       │          │ estimated_time   │
│ target_date      │          │ order_index      │
└──────────────────┘          │ xp_reward        │
                              └────────┬─────────┘
                                       │
                                       │ 1:N
                                       ▼
                              ┌──────────────────┐
                              │  MODULE_CONTENT  │
                              ├──────────────────┤
                              │ id (PK)          │
                              │ module_id (FK)   │
                              │ content_type     │
                              │ content_data     │ ◄── JSON/JSONB
                              │ order_index      │
                              └──────────────────┘


┌──────────────────┐          ┌──────────────────┐
│      TASKS       │          │  SUBMISSIONS     │
├──────────────────┤          ├──────────────────┤
│ id (PK)          │──────────│ id (PK)          │
│ user_id (FK)     │   1:N    │ task_id (FK)     │
│ module_id (FK)   │          │ user_id (FK)     │
│ type             │          │ content          │
│ title            │          │ score            │
│ description      │          │ feedback         │
│ difficulty       │          │ time_spent       │
│ deadline         │          │ submitted_at     │
│ status           │          │ plagiarism_score │
│ xp_reward        │          │ verified         │
└──────────────────┘          └──────────────────┘


┌──────────────────┐          ┌──────────────────┐
│   CONVERSATIONS  │          │    MESSAGES      │
├──────────────────┤          ├──────────────────┤
│ id (PK)          │──────────│ id (PK)          │
│ user_id (FK)     │   1:N    │ conversation_id  │
│ title            │          │ role             │
│ context_type     │          │ content          │
│ created_at       │          │ tokens_used      │
│ last_message_at  │          │ created_at       │
└──────────────────┘          └──────────────────┘


┌──────────────────┐          ┌──────────────────┐
│ JOURNAL_ENTRIES  │          │  ENTRY_TAGS      │
├──────────────────┤          ├──────────────────┤
│ id (PK)          │──────────│ entry_id (FK)    │
│ user_id (FK)     │   N:N    │ tag_id (FK)      │
│ type             │          └──────────────────┘
│ title            │                   │
│ content          │                   │
│ mood             │          ┌────────┴─────────┐
│ created_at       │          │      TAGS        │
│ updated_at       │          ├──────────────────┤
└──────────────────┘          │ id (PK)          │
                              │ name             │
                              │ color            │
                              └──────────────────┘


┌──────────────────┐          ┌──────────────────┐
│   CHALLENGES     │          │CHALLENGE_ATTEMPTS│
├──────────────────┤          ├──────────────────┤
│ id (PK)          │──────────│ id (PK)          │
│ title            │   1:N    │ challenge_id(FK) │
│ description      │          │ user_id (FK)     │
│ category         │          │ solution         │
│ difficulty       │          │ score            │
│ company_tag      │          │ time_taken       │
│ template_code    │          │ started_at       │
│ test_cases       │          │ completed_at     │
│ hints            │          │ rank             │
│ xp_reward        │          └──────────────────┘
└──────────────────┘


┌──────────────────┐          ┌──────────────────┐
│    PROGRESS      │          │   ACHIEVEMENTS   │
├──────────────────┤          ├──────────────────┤
│ id (PK)          │          │ id (PK)          │
│ user_id (FK)     │          │ name             │
│ date             │          │ description      │
│ xp_earned        │          │ icon             │
│ time_spent       │          │ xp_reward        │
│ modules_completed│          │ criteria         │
│ tasks_completed  │          └────────┬─────────┘
│ streak_count     │                   │
└──────────────────┘          ┌────────┴─────────┐
                              │USER_ACHIEVEMENTS │
                              ├──────────────────┤
                              │ user_id (FK)     │
                              │ achievement_id   │
                              │ earned_at        │
                              └──────────────────┘


┌──────────────────┐          ┌──────────────────┐
│   REMINDERS      │          │  WISDOM_QUOTES   │
├──────────────────┤          ├──────────────────┤
│ id (PK)          │          │ id (PK)          │
│ user_id (FK)     │          │ text_original    │
│ type             │          │ text_translation │
│ title            │          │ source           │
│ description      │          │ category         │
│ scheduled_at     │          │ topics           │ ◄── ARRAY
│ repeat_pattern   │          │ context_keywords │ ◄── ARRAY
│ is_active        │          └──────────────────┘
│ channel          │
└──────────────────┘


┌──────────────────┐
│   SKILL_LEVELS   │
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ skill_name       │
│ level            │ ◄── 0-100
│ confidence       │ ◄── Based on verification
│ last_assessed    │
│ history          │ ◄── JSONB time-series
└──────────────────┘
```

### 5.2 Database Schema Details

#### PostgreSQL Tables (Primary Database)

```sql
-- Core User Tables
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    account_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    bio TEXT,
    learning_style VARCHAR(20), -- visual, auditory, kinesthetic
    experience_level VARCHAR(20), -- beginner, intermediate, advanced
    weekly_time_commitment INTEGER, -- hours per week
    primary_goal VARCHAR(100),
    interests TEXT[], -- Array of interest tags
    timezone VARCHAR(50) DEFAULT 'UTC',
    notification_preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learning Structure Tables
CREATE TABLE learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    total_xp INTEGER DEFAULT 0,
    earned_xp INTEGER DEFAULT 0,
    estimated_duration_hours INTEGER,
    target_completion_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path_id UUID REFERENCES learning_paths(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content_type VARCHAR(50), -- theory, practice, project, quiz
    difficulty VARCHAR(20),
    estimated_minutes INTEGER,
    order_index INTEGER,
    xp_reward INTEGER DEFAULT 10,
    prerequisites UUID[], -- Array of prerequisite module IDs
    status VARCHAR(20) DEFAULT 'locked',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task & Assessment Tables
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    module_id UUID REFERENCES modules(id),
    type VARCHAR(50), -- learning, practice, project, daily
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    difficulty VARCHAR(20),
    deadline TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    xp_reward INTEGER DEFAULT 5,
    max_attempts INTEGER DEFAULT 3,
    hints TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    score DECIMAL(5,2),
    feedback JSONB,
    time_spent_seconds INTEGER,
    typing_pattern_data JSONB, -- For anti-cheat
    plagiarism_score DECIMAL(5,2),
    verification_status VARCHAR(20) DEFAULT 'pending',
    attempt_number INTEGER DEFAULT 1,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Progress & Analytics Tables
CREATE TABLE daily_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    date DATE NOT NULL,
    xp_earned INTEGER DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    modules_completed INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    challenges_attempted INTEGER DEFAULT 0,
    streak_maintained BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, date)
);

CREATE TABLE skill_levels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    skill_name VARCHAR(100) NOT NULL,
    current_level INTEGER DEFAULT 0, -- 0-100
    confidence_score DECIMAL(5,2) DEFAULT 50, -- Based on verification
    assessments_count INTEGER DEFAULT 0,
    last_assessed TIMESTAMP,
    level_history JSONB, -- Time-series data
    UNIQUE(user_id, skill_name)
);

-- Reminder & Notification Tables
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50), -- study, review, deadline, custom
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scheduled_at TIMESTAMP NOT NULL,
    repeat_pattern VARCHAR(50), -- daily, weekly, custom
    repeat_config JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    channels VARCHAR(50)[], -- push, email, sms
    last_sent TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Achievement System Tables
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    category VARCHAR(50),
    xp_reward INTEGER DEFAULT 0,
    criteria JSONB NOT NULL, -- Conditions to earn
    is_hidden BOOLEAN DEFAULT FALSE,
    rarity VARCHAR(20) DEFAULT 'common'
);

CREATE TABLE user_achievements (
    user_id UUID REFERENCES users(id),
    achievement_id UUID REFERENCES achievements(id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, achievement_id)
);

-- Indexes for Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_profiles_user ON user_profiles(user_id);
CREATE INDEX idx_learning_paths_user ON learning_paths(user_id);
CREATE INDEX idx_modules_path ON modules(path_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_submissions_task ON submissions(task_id);
CREATE INDEX idx_daily_progress_user_date ON daily_progress(user_id, date);
CREATE INDEX idx_skill_levels_user ON skill_levels(user_id);
CREATE INDEX idx_reminders_user_scheduled ON reminders(user_id, scheduled_at);
```

#### MongoDB Collections (Content & Flexible Data)

```javascript
// Learning Content Collection
db.createCollection("learning_content", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["module_id", "type", "content"],
      properties: {
        module_id: { bsonType: "string" },
        type: { enum: ["lesson", "video", "interactive", "code_exercise"] },
        title: { bsonType: "string" },
        content: { bsonType: "object" }, // Flexible content structure
        order_index: { bsonType: "int" },
        metadata: {
          bsonType: "object",
          properties: {
            author: { bsonType: "string" },
            version: { bsonType: "string" },
            tags: { bsonType: "array" },
            difficulty: { bsonType: "string" }
          }
        },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

// Journal Entries Collection
db.createCollection("journal_entries", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "type", "content"],
      properties: {
        user_id: { bsonType: "string" },
        type: { enum: ["idea", "note", "connection", "question", "achievement", "bug_log", "goal"] },
        title: { bsonType: "string" },
        content: { bsonType: "string" },
        rich_content: { bsonType: "object" }, // For attachments, code snippets
        tags: { bsonType: "array" },
        linked_entries: { bsonType: "array" }, // Related entry IDs
        mood: { bsonType: "string" },
        ai_generated_insights: { bsonType: "object" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

// Conversation History Collection
db.createCollection("conversations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "messages"],
      properties: {
        user_id: { bsonType: "string" },
        title: { bsonType: "string" },
        context: {
          bsonType: "object",
          properties: {
            topic: { bsonType: "string" },
            module_id: { bsonType: "string" },
            task_id: { bsonType: "string" }
          }
        },
        messages: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              role: { enum: ["user", "assistant", "system"] },
              content: { bsonType: "string" },
              timestamp: { bsonType: "date" },
              tokens_used: { bsonType: "int" },
              metadata: { bsonType: "object" }
            }
          }
        },
        total_tokens: { bsonType: "int" },
        created_at: { bsonType: "date" },
        last_message_at: { bsonType: "date" }
      }
    }
  }
});

// Ancient Wisdom Collection
db.createCollection("wisdom_quotes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["text_original", "source"],
      properties: {
        text_original: { bsonType: "string" }, // Sanskrit/original language
        text_transliteration: { bsonType: "string" },
        text_translation: { bsonType: "string" }, // English translation
        source: { bsonType: "string" }, // e.g., "Bhagavad Gita 2.47"
        category: { enum: ["learning", "wisdom", "ethics", "science", "philosophy", "discipline"] },
        topics: { bsonType: "array" }, // ["perseverance", "knowledge", "action"]
        context_keywords: { bsonType: "array" }, // For RAG matching
        explanation: { bsonType: "string" },
        related_modern_concept: { bsonType: "string" }
      }
    }
  }
});

// Industry Challenges Collection
db.createCollection("industry_challenges", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "description", "difficulty"],
      properties: {
        title: { bsonType: "string" },
        description: { bsonType: "string" },
        detailed_requirements: { bsonType: "string" },
        category: { bsonType: "string" },
        subcategory: { bsonType: "string" },
        difficulty: { enum: ["easy", "medium", "hard", "expert"] },
        company_tags: { bsonType: "array" }, // ["Google", "Amazon", "Startup"]
        skills_tested: { bsonType: "array" },
        template_code: { bsonType: "object" }, // Language-specific templates
        test_cases: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              input: { bsonType: "string" },
              expected_output: { bsonType: "string" },
              is_hidden: { bsonType: "bool" }
            }
          }
        },
        hints: { bsonType: "array" },
        solution_approach: { bsonType: "string" }, // Hidden, for verification
        xp_reward: { bsonType: "int" },
        time_limit_minutes: { bsonType: "int" },
        created_at: { bsonType: "date" }
      }
    }
  }
});

// Indexes
db.learning_content.createIndex({ "module_id": 1 });
db.learning_content.createIndex({ "metadata.tags": 1 });
db.journal_entries.createIndex({ "user_id": 1, "created_at": -1 });
db.journal_entries.createIndex({ "tags": 1 });
db.conversations.createIndex({ "user_id": 1, "last_message_at": -1 });
db.wisdom_quotes.createIndex({ "topics": 1 });
db.wisdom_quotes.createIndex({ "context_keywords": 1 });
db.industry_challenges.createIndex({ "difficulty": 1, "category": 1 });
```

### 5.3 Caching Strategy (Redis)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         REDIS CACHING STRATEGY                           │
└─────────────────────────────────────────────────────────────────────────┘

KEY PATTERNS:
─────────────
session:{user_id}                    → User session data (TTL: 24h)
user:{user_id}:profile               → User profile cache (TTL: 1h)
user:{user_id}:progress              → Daily progress cache (TTL: 5m)
user:{user_id}:streak                → Current streak info (TTL: 24h)
user:{user_id}:recommendations       → Personalized recs (TTL: 15m)

learning_path:{path_id}              → Path structure (TTL: 1h)
module:{module_id}:content           → Module content (TTL: 1h)
module:{module_id}:progress:{user}   → User's module progress (TTL: 5m)

challenge:{challenge_id}             → Challenge details (TTL: 6h)
challenge:leaderboard:{challenge_id} → Sorted set leaderboard (TTL: 1m)

wisdom:daily                         → Daily wisdom quote (TTL: 24h)
wisdom:topic:{topic}                 → Topic-wise quotes (TTL: 1h)

rate_limit:{user_id}:{endpoint}      → API rate limiting (TTL: 1m)
rate_limit:ai:{user_id}              → AI API rate limiting (TTL: 1h)

SORTED SETS:
────────────
leaderboard:global:xp                → Global XP leaderboard
leaderboard:weekly:xp                → Weekly XP leaderboard
leaderboard:challenge:{id}           → Challenge-specific leaderboard

LISTS:
──────
notifications:{user_id}              → Pending notifications queue
activity_feed:{user_id}              → Recent activity items

SETS:
─────
online_users                         → Currently active users
user:{user_id}:completed_modules     → Completed module IDs
```

### 5.4 Vector Database (Pinecone)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      VECTOR DATABASE STRUCTURE                           │
└─────────────────────────────────────────────────────────────────────────┘

INDEX: learning_content
───────────────────────
Dimensions: 1536 (OpenAI Ada)
Metric: Cosine Similarity

Namespaces:
├── concepts          → Learning concept embeddings
├── code_examples     → Code snippet embeddings  
├── wisdom            → Ancient wisdom embeddings
├── user_notes        → User journal/note embeddings
└── challenges        → Challenge description embeddings

Metadata Schema:
{
  "type": "concept|code|wisdom|note|challenge",
  "module_id": "uuid",
  "user_id": "uuid",           // For user-specific content
  "topic": "string",
  "difficulty": "string",
  "language": "string",        // Programming language for code
  "source": "string",          // For wisdom quotes
  "created_at": "timestamp"
}

USE CASES:
──────────
1. Semantic search for learning content
2. Finding related concepts during explanation
3. Contextually relevant wisdom quotes
4. Similar challenge recommendations
5. Connecting user notes to learning material
```

---

## 6. Security Architecture

### 6.1 Authentication & Authorization Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                                 │
└─────────────────────────────────────────────────────────────────────────┘

Authentication Flow:
───────────────────

    Client                API Gateway              Auth Service
      │                       │                         │
      │──── Login Request ───►│                         │
      │                       │──── Validate ──────────►│
      │                       │                         │
      │                       │◄─── JWT + Refresh ──────│
      │◄─── Tokens ───────────│                         │
      │                       │                         │

Token Structure:
───────────────
Access Token (JWT):
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "role": "learner",
  "permissions": ["read:content", "write:submissions"],
  "iat": 1234567890,
  "exp": 1234571490  // 1 hour
}

Refresh Token: Stored in HttpOnly cookie + Redis

Authorization Levels:
────────────────────
┌─────────────┬──────────────────────────────────────────────┐
│    Role     │              Permissions                      │
├─────────────┼──────────────────────────────────────────────┤
│   Guest     │ read:public_content                          │
│   Learner   │ read:content, write:submissions, use:mentor  │
│   Premium   │ + advanced:challenges, unlimited:mentor      │
│   Mentor    │ + review:submissions, create:content         │
│   Admin     │ Full access                                   │
└─────────────┴──────────────────────────────────────────────┘

Security Measures:
─────────────────
• HTTPS everywhere (TLS 1.3)
• CORS whitelist configuration
• Rate limiting per user/IP
• Input validation & sanitization
• SQL injection prevention (parameterized queries)
• XSS prevention (CSP headers)
• CSRF tokens for forms
• Secure password hashing (Argon2)
• API key rotation for external services
• Audit logging for sensitive operations
• Data encryption at rest (AES-256)
```

---

## 7. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────────────┘

                         ┌───────────────────┐
                         │    CloudFlare     │
                         │    (CDN + WAF)    │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Load Balancer   │
                         │   (AWS ALB/NLB)   │
                         └─────────┬─────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Kubernetes     │     │  Kubernetes     │     │  Kubernetes     │
│  Node Pool 1    │     │  Node Pool 2    │     │  Node Pool 3    │
│  (API Services) │     │  (AI Services)  │     │  (Background)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Service Mesh    │
                         │   (Istio/Linkerd) │
                         └─────────┬─────────┘
                                   │
    ┌──────────────┬───────────────┼───────────────┬──────────────┐
    │              │               │               │              │
    ▼              ▼               ▼               ▼              ▼
┌────────┐   ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│Postgres│   │MongoDB │     │ Redis  │     │Elastic │     │Pinecone│
│(RDS)   │   │ Atlas  │     │(Elasti │     │ Search │     │(Vector)│
│        │   │        │     │ cache) │     │        │     │        │
└────────┘   └────────┘     └────────┘     └────────┘     └────────┘

CI/CD Pipeline:
──────────────
GitHub → GitHub Actions → Docker Build → ECR → ArgoCD → Kubernetes

Environments:
────────────
• Development (dev.platform.com)
• Staging (staging.platform.com)  
• Production (platform.com)
```

---

## 8. Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MONITORING & OBSERVABILITY                            │
└─────────────────────────────────────────────────────────────────────────┘

Metrics (Prometheus + Grafana):
─────────────────────────────
• API response times (p50, p95, p99)
• Request throughput per service
• Error rates by endpoint
• Database query performance
• Cache hit/miss ratios
• AI API latency and token usage
• User engagement metrics

Logging (ELK Stack):
───────────────────
• Structured JSON logs
• Correlation IDs across services
• Log levels: DEBUG, INFO, WARN, ERROR
• Sensitive data masking
• 30-day retention

Tracing (Jaeger/Zipkin):
───────────────────────
• Distributed request tracing
• Service dependency mapping
• Latency breakdown analysis

Alerting:
────────
• PagerDuty/Opsgenie integration
• Slack notifications
• Automated incident creation
• Escalation policies

Key Dashboards:
──────────────
1. System Health Overview
2. User Engagement Metrics
3. AI Service Performance
4. Learning Progress Analytics
5. Security & Compliance
```

---

## 9. API Specification Summary

### Core API Endpoints

| Service | Endpoint | Method | Description |
|---------|----------|--------|-------------|
| **Auth** | `/auth/register` | POST | User registration |
| **Auth** | `/auth/login` | POST | User login |
| **Auth** | `/auth/refresh` | POST | Refresh tokens |
| **User** | `/users/me` | GET | Current user profile |
| **User** | `/users/me/preferences` | PUT | Update preferences |
| **Learning** | `/learning/paths` | GET | User's learning paths |
| **Learning** | `/learning/paths/generate` | POST | Generate personalized path |
| **Learning** | `/learning/modules/:id` | GET | Module content |
| **Mentor** | `/mentor/chat` | POST | Chat with AI mentor |
| **Mentor** | `/mentor/chat/stream` | POST | Streaming chat |
| **Tasks** | `/tasks` | GET | User's tasks |
| **Tasks** | `/tasks/:id/submit` | POST | Submit task solution |
| **Challenges** | `/challenges` | GET | Available challenges |
| **Challenges** | `/challenges/:id/start` | POST | Start a challenge |
| **Journal** | `/journal/entries` | GET/POST | Journal entries |
| **Progress** | `/progress/overview` | GET | Progress summary |
| **Reminders** | `/reminders` | GET/POST | Manage reminders |
| **Wisdom** | `/wisdom/daily` | GET | Daily wisdom quote |

---

## 10. Implementation Phases

### Phase 1: Foundation (Weeks 1-6)
- [ ] Project setup and infrastructure
- [ ] User authentication system
- [ ] Basic user profiles
- [ ] Database schema implementation
- [ ] Core API structure

### Phase 2: Learning Core (Weeks 7-12)
- [ ] Learning path engine
- [ ] Module content management
- [ ] Basic AI mentor integration
- [ ] Task management system
- [ ] Progress tracking basics

### Phase 3: AI & Intelligence (Weeks 13-18)
- [ ] Advanced AI mentor (Socratic method)
- [ ] Anti-cheat detection system
- [ ] Personalized recommendations
- [ ] RAG system with vector search
- [ ] Communication skills module

### Phase 4: Engagement (Weeks 19-24)
- [ ] Industry challenge generator
- [ ] Idea journal with AI insights
- [ ] Gamification system
- [ ] Ancient wisdom integration
- [ ] Reminder and notification system

### Phase 5: Polish & Scale (Weeks 25-30)
- [ ] Performance optimization
- [ ] Mobile app development
- [ ] Advanced analytics
- [ ] A/B testing framework
- [ ] Production deployment

---

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Daily Active Users | Growth 10% MoM | Analytics |
| Learning Completion Rate | >60% | Progress tracking |
| User Retention (30-day) | >40% | Cohort analysis |
| Average Session Duration | >20 min | Analytics |
| Concept Retention | >70% | Spaced repetition tests |
| User Satisfaction | >4.5/5 | Surveys |
| Anti-cheat Detection Rate | >95% | Verification system |

---

*Document Version: 1.0*
*Last Updated: March 2026*
*Architecture designed for scalability, learning effectiveness, and genuine knowledge acquisition*
