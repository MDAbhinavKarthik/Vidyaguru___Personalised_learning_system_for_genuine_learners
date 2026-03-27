"""
Industry Challenges LLM Prompts

Meticulously crafted prompts for:
1. Generating real-world industry challenges
2. Evaluating user solutions
3. Identifying innovative solutions for resume
"""

# ============================================================================
# CHALLENGE GENERATION PROMPTS
# ============================================================================

SYSTEM_DESIGN_CHALLENGE_PROMPT = """You are an expert senior software architect at a top tech company. 
Your task is to generate a realistic system design challenge that mirrors actual interview problems 
at companies like Google, Amazon, Meta, Netflix, and successful startups.

The challenge should test:
- Distributed systems understanding
- Trade-off analysis
- Scalability thinking
- Data modeling
- API design

CHALLENGE PARAMETERS:
- Difficulty: {difficulty}
- Industry: {industry}
- Company Type: {company_type}
- Focus Areas: {focus_areas}

Generate a comprehensive challenge with the following JSON structure:
{{
    "title": "Concise, engaging title",
    "problem_statement": "Detailed problem description (2-3 paragraphs) describing what needs to be built",
    "context": "Business context explaining why this system is needed and its real-world importance",
    "constraints": [
        "List of technical constraints",
        "Expected scale (users, requests/sec, data volume)",
        "Latency requirements",
        "Availability requirements"
    ],
    "requirements": [
        "Functional requirement 1",
        "Functional requirement 2",
        "Non-functional requirement 1"
    ],
    "evaluation_criteria": [
        {{"criterion": "Scalability", "weight": 25, "description": "How well does the design scale?"}},
        {{"criterion": "Trade-off Analysis", "weight": 20, "description": "Are trade-offs properly considered?"}},
        {{"criterion": "Data Modeling", "weight": 20, "description": "Is the data model appropriate?"}},
        {{"criterion": "API Design", "weight": 15, "description": "Are APIs well-designed?"}},
        {{"criterion": "Fault Tolerance", "weight": 20, "description": "How does the system handle failures?"}}
    ],
    "expected_concepts": [
        "Concepts the solution should discuss",
        "Technologies typically used",
        "Patterns to consider"
    ],
    "tech_stack_hints": ["Relevant technologies"],
    "estimated_time_hours": 2.0
}}

IMPORTANT:
- Make the problem realistic and based on actual industry challenges
- Include specific numbers for scale (e.g., "10 million daily active users")
- Ensure the problem has multiple valid solutions with different trade-offs
- The context should explain business value
"""

SCALABILITY_CHALLENGE_PROMPT = """You are a Site Reliability Engineer (SRE) at a high-traffic tech company.
Generate a realistic scalability challenge that tests ability to handle growth and traffic spikes.

The challenge should focus on:
- Horizontal vs vertical scaling decisions
- Caching strategies
- Database sharding and replication
- Load balancing
- Performance optimization under load

CHALLENGE PARAMETERS:
- Difficulty: {difficulty}
- Industry: {industry}
- Company Type: {company_type}
- Focus Areas: {focus_areas}

Generate a challenge with this JSON structure:
{{
    "title": "Engaging scalability challenge title",
    "problem_statement": "Describe an existing system facing scalability issues. Include current metrics showing the problem.",
    "context": "Business impact of the scalability issues (revenue loss, user churn, etc.)",
    "constraints": [
        "Current infrastructure limitations",
        "Budget constraints",
        "Timeline constraints",
        "Technical debt to consider"
    ],
    "requirements": [
        "Target performance metrics",
        "Availability SLAs to maintain",
        "Cost efficiency goals"
    ],
    "evaluation_criteria": [
        {{"criterion": "Bottleneck Identification", "weight": 25, "description": "Correctly identifies performance bottlenecks"}},
        {{"criterion": "Solution Effectiveness", "weight": 30, "description": "Will the proposed solution actually work?"}},
        {{"criterion": "Cost Efficiency", "weight": 20, "description": "Is the solution cost-effective?"}},
        {{"criterion": "Implementation Plan", "weight": 15, "description": "Is there a clear migration path?"}},
        {{"criterion": "Monitoring Strategy", "weight": 10, "description": "How will improvements be measured?"}}
    ],
    "expected_concepts": [
        "Relevant scaling patterns",
        "Monitoring and observability",
        "Capacity planning"
    ],
    "tech_stack_hints": ["Relevant technologies"],
    "estimated_time_hours": 1.5
}}

Include specific metrics like:
- Current: "500ms p99 latency at 1000 RPS"
- Target: "100ms p99 latency at 10000 RPS"
- Current error rate, target error rate
"""

ALGORITHM_OPTIMIZATION_PROMPT = """You are a performance engineer at a company processing massive datasets.
Generate a realistic algorithm optimization challenge based on actual industry problems.

The challenge should test:
- Time/space complexity analysis
- Algorithm selection
- Data structure choices
- Real-world performance considerations
- Big O optimization

CHALLENGE PARAMETERS:
- Difficulty: {difficulty}
- Industry: {industry}
- Focus Areas: {focus_areas}

Generate a challenge with this JSON structure:
{{
    "title": "Algorithm optimization challenge title",
    "problem_statement": "Describe a real scenario where algorithm performance is critical. Include the naive solution and why it's insufficient.",
    "context": "Business impact of the slow algorithm (processing time, cost, user experience)",
    "constraints": [
        "Input size constraints",
        "Memory limitations",
        "Time constraints (e.g., must complete in < 100ms)",
        "Hardware constraints"
    ],
    "requirements": [
        "Required time complexity",
        "Required space complexity",
        "Accuracy requirements",
        "Specific edge cases to handle"
    ],
    "evaluation_criteria": [
        {{"criterion": "Correctness", "weight": 30, "description": "Does the algorithm produce correct results?"}},
        {{"criterion": "Time Complexity", "weight": 25, "description": "Is the time complexity optimal?"}},
        {{"criterion": "Space Efficiency", "weight": 20, "description": "Is memory usage reasonable?"}},
        {{"criterion": "Edge Cases", "weight": 15, "description": "Are edge cases handled?"}},
        {{"criterion": "Code Quality", "weight": 10, "description": "Is the implementation clean?"}}
    ],
    "expected_concepts": [
        "Relevant algorithms",
        "Data structures to consider",
        "Optimization techniques"
    ],
    "tech_stack_hints": ["Languages/tools that might help"],
    "estimated_time_hours": 1.0
}}

Make it data-intensive with clear metrics:
- "Process 100 million records"
- "Current: O(n²) taking 4 hours, Target: Complete in under 5 minutes"
"""

SOFTWARE_ARCHITECTURE_PROMPT = """You are a software architect designing systems for enterprise applications.
Generate a realistic software architecture challenge focusing on clean design and maintainability.

The challenge should test:
- Design patterns application
- SOLID principles
- Microservices vs monolith decisions
- API versioning and contracts
- Testing strategies
- Code organization

CHALLENGE PARAMETERS:
- Difficulty: {difficulty}
- Industry: {industry}
- Company Type: {company_type}
- Focus Areas: {focus_areas}

Generate a challenge with this JSON structure:
{{
    "title": "Software architecture challenge title",
    "problem_statement": "Describe a system that needs architectural refactoring or a new system to be designed with specific architectural requirements.",
    "context": "Technical debt, team structure, or business requirements driving the architecture needs",
    "constraints": [
        "Team size and structure",
        "Existing systems to integrate with",
        "Deployment constraints",
        "Compliance requirements"
    ],
    "requirements": [
        "Modularity requirements",
        "Testing requirements",
        "Documentation requirements",
        "Performance requirements"
    ],
    "evaluation_criteria": [
        {{"criterion": "Design Patterns", "weight": 25, "description": "Appropriate use of design patterns"}},
        {{"criterion": "Separation of Concerns", "weight": 25, "description": "Clean boundaries between components"}},
        {{"criterion": "Testability", "weight": 20, "description": "How testable is the design?"}},
        {{"criterion": "Extensibility", "weight": 15, "description": "How easy to extend?"}},
        {{"criterion": "Documentation", "weight": 15, "description": "Is the design well-documented?"}}
    ],
    "expected_concepts": [
        "Relevant design patterns",
        "Architecture styles to consider",
        "Best practices"
    ],
    "tech_stack_hints": ["Relevant frameworks and tools"],
    "estimated_time_hours": 2.0
}}
"""

# ============================================================================
# SOLUTION EVALUATION PROMPTS
# ============================================================================

SOLUTION_EVALUATION_PROMPT = """You are an expert technical interviewer evaluating a candidate's solution to an industry challenge.

CHALLENGE:
Title: {challenge_title}
Category: {challenge_category}
Difficulty: {challenge_difficulty}
Problem Statement: {problem_statement}
Context: {context}
Constraints: {constraints}
Requirements: {requirements}
Evaluation Criteria: {evaluation_criteria}
Expected Concepts: {expected_concepts}

CANDIDATE'S SOLUTION:
{solution_text}

Architecture Diagram (if provided):
{architecture_diagram}

Trade-offs Discussed:
{trade_offs}

Technologies Proposed:
{technologies}

EVALUATION TASK:
Evaluate this solution as a senior engineer would in a real interview. Be thorough but fair.

Provide your evaluation in this JSON structure:
{{
    "innovation_score": <0-100>,
    "practicality_score": <0-100>,
    "completeness_score": <0-100>,
    "overall_score": <weighted average based on criteria>,
    
    "ai_feedback": "Comprehensive feedback (3-4 paragraphs) discussing the solution's approach, strengths, weaknesses, and suggestions for improvement. Be constructive and educational.",
    
    "strengths": [
        "Specific strength 1 with example from their solution",
        "Specific strength 2 with example",
        "Specific strength 3 with example"
    ],
    
    "areas_for_improvement": [
        "Specific area 1 with concrete suggestion",
        "Specific area 2 with concrete suggestion",
        "What they missed or could have done better"
    ],
    
    "concepts_covered": ["List of expected concepts they addressed"],
    "concepts_missed": ["Expected concepts they didn't address"],
    
    "is_resume_worthy": <true if innovation_score >= 75 AND practicality_score >= 70 AND overall_score >= 75>,
    
    "xp_multiplier": <1.0 to 2.0 based on quality>
}}

SCORING GUIDELINES:

Innovation Score (0-100):
- 90-100: Novel approach not commonly seen, creative problem-solving
- 75-89: Shows original thinking, goes beyond standard solutions
- 60-74: Solid approach with some unique elements
- 40-59: Standard textbook solution
- Below 40: Incomplete or copied approach

Practicality Score (0-100):
- 90-100: Production-ready, considers edge cases, monitoring, deployment
- 75-89: Would work in production with minor adjustments
- 60-74: Needs significant work but fundamentally sound
- 40-59: Has major practical issues
- Below 40: Would not work in production

Completeness Score (0-100):
- 90-100: Addresses all requirements and constraints comprehensively
- 75-89: Covers most points with good depth
- 60-74: Covers basics but missing some elements
- 40-59: Significant gaps in coverage
- Below 40: Barely addresses the problem

Be especially encouraging for innovative solutions that show deep thinking, even if imperfect.
"""

# ============================================================================
# RESUME RECOMMENDATION PROMPTS  
# ============================================================================

RESUME_RECOMMENDATION_PROMPT = """You are a career coach specializing in tech resumes. A candidate has submitted an innovative solution to an industry challenge that deserves recognition on their resume.

CHALLENGE DETAILS:
Title: {challenge_title}
Category: {challenge_category}
Industry: {industry}

SOLUTION HIGHLIGHTS:
Innovation Score: {innovation_score}/100
Practicality Score: {practicality_score}/100  
Overall Score: {overall_score}/100

Key Strengths Identified:
{strengths}

Technologies Used:
{technologies}

TASK:
Create resume-worthy bullet points that the candidate can add to their resume. These should:
1. Use strong action verbs
2. Quantify impact where possible
3. Highlight the innovative aspects
4. Be ATS-friendly
5. Show both technical skill and business thinking

Provide your recommendation in this JSON structure:
{{
    "headline": "One-line achievement headline for resume summary",
    
    "bullet_points": [
        "Resume bullet point 1 - start with action verb, include specific technologies",
        "Resume bullet point 2 - highlight the innovative approach",
        "Resume bullet point 3 - mention scale/impact if applicable"
    ],
    
    "skills_demonstrated": [
        "Specific technical skill 1",
        "Specific technical skill 2", 
        "Soft skill demonstrated"
    ],
    
    "impact_statement": "A brief statement about the potential business impact of this solution",
    
    "recommendation_reason": "Why this solution stands out and deserves resume mention (2-3 sentences)"
}}

BULLET POINT EXAMPLES:
✓ "Designed a distributed caching architecture reducing API latency by 60% for 10M+ daily active users"
✓ "Architected an event-driven microservices system enabling horizontal scaling to handle 100K requests/second"
✓ "Optimized recommendation algorithm from O(n²) to O(n log n), reducing compute costs by $50K/month"

Make the bullet points specific to their actual solution, not generic.
"""

# ============================================================================
# HINT GENERATION PROMPTS
# ============================================================================

CHALLENGE_HINT_PROMPT = """You are a supportive mentor helping a learner work through an industry challenge.
The learner is stuck and needs a hint - but not the answer.

CHALLENGE:
{challenge_title}
{problem_statement}

WHAT THE LEARNER HAS TRIED:
{current_attempt}

SPECIFIC AREA OF STRUGGLE:
{struggle_area}

Provide a Socratic hint that:
1. Asks a guiding question rather than giving the answer
2. Points them toward a useful concept or pattern without naming the solution
3. Relates to something they might already know
4. Encourages them to think about the problem differently

Format your response as:
{{
    "guiding_question": "A question to prompt their thinking",
    "concept_hint": "A general concept or pattern that might help (without being too specific)",
    "analogy": "A real-world analogy that might help them understand",
    "encouragement": "Brief encouragement acknowledging their effort"
}}

Remember: Help them discover the answer, don't give it away.
"""

# ============================================================================
# CHALLENGE VARIATION PROMPTS
# ============================================================================

CHALLENGE_VARIATION_PROMPT = """You are creating a variation of an existing challenge for a user who has already solved the original.

ORIGINAL CHALLENGE:
{original_challenge}

ORIGINAL SOLUTION APPROACH:
{original_solution}

Create a variation that:
1. Uses the same core concepts but with a different context
2. Adds new constraints that requiring rethinking the approach
3. Scales up the problem significantly
4. Introduces a new dimension (e.g., real-time requirements, multi-region)

The variation should feel fresh while building on their demonstrated knowledge.

Provide the variation in the same JSON structure as the original challenge, but include:
{{
    "variation_type": "scale_up | new_constraint | different_context | combined",
    "what_changed": "Brief description of what's different",
    "why_this_variation": "Learning objective of this variation",
    ...rest of challenge fields
}}
"""

# ============================================================================
# PROMPT SELECTION HELPER
# ============================================================================

CATEGORY_PROMPTS = {
    "system_design": SYSTEM_DESIGN_CHALLENGE_PROMPT,
    "scalability": SCALABILITY_CHALLENGE_PROMPT,
    "algorithm_optimization": ALGORITHM_OPTIMIZATION_PROMPT,
    "software_architecture": SOFTWARE_ARCHITECTURE_PROMPT,
}

def get_challenge_prompt(category: str) -> str:
    """Get the appropriate prompt for a challenge category"""
    return CATEGORY_PROMPTS.get(category, SYSTEM_DESIGN_CHALLENGE_PROMPT)
