"""
VidyaGuru Cheating Detection System
Advanced detection of copy-paste, plagiarism, and verification of genuine understanding
"""
import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import difflib
import asyncio

from pydantic import BaseModel


class SuspicionLevel(str, Enum):
    """Levels of cheating suspicion"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ResponsePattern:
    """Pattern information about a user's responses"""
    avg_length: float = 0
    avg_response_time_seconds: float = 0
    vocabulary_complexity: float = 0
    code_style_signature: str = ""
    common_phrases: List[str] = field(default_factory=list)


@dataclass
class CheatingAnalysis:
    """Complete analysis of potential cheating"""
    suspicion_level: SuspicionLevel
    confidence: float  # 0.0 to 1.0
    indicators: List[str]
    evidence: Dict[str, Any]
    recommended_action: str
    verification_questions: List[str]
    bypass_probability: float  # Probability this is false positive


class CheatingDetector:
    """
    Detects various forms of academic dishonesty including:
    - Copy-paste from external sources
    - AI-generated responses
    - Plagiarism from previous submissions
    - Unexplained complexity jumps
    - Suspiciously fast responses
    """
    
    # Known tutorial/documentation patterns
    TUTORIAL_PATTERNS = [
        r"in this tutorial",
        r"let's see how",
        r"as shown below",
        r"the output will be",
        r"run the following",
        r"you should see",
        r"congratulations! you have",
        r"copy and paste",
        r"step \d+:",
        r"first, we need to",
        r"let me explain",
        r"here's how",
        r"this is how you",
        r"to do this,",
        r"we'll start by",
        r"notice that",
        r"this ensures that",
        r"this way,",
        r"in summary,",
        r"finally,",
    ]
    
    # AI writing patterns
    AI_PATTERNS = [
        r"as an ai",
        r"i apologize",
        r"i'd be happy to",
        r"here's a comprehensive",
        r"let me break this down",
        r"there are several",
        r"it's worth noting",
        r"in essence,",
        r"to summarize,",
        r"key takeaways",
        r"^\d+\.\s+\*\*[^*]+\*\*",  # Numbered bold headings
        r"importantly,",
        r"additionally,",
        r"furthermore,",
        r"however,",  # Overuse
    ]
    
    # Code quality indicators that suggest professional/copied code
    PRO_CODE_PATTERNS = [
        r"(?:type hints|annotations) throughout",
        r"docstrings? with",
        r"error handling for",
        r"edge cases handled",
        r"time complexity:?\s+O\(",
        r"space complexity:?\s+O\(",
        r"SOLID principles",
        r"design pattern",
        r"dependency injection",
        r"factory method",
    ]
    
    def __init__(self):
        self.user_patterns: Dict[str, ResponsePattern] = {}
        self.submission_hashes: Dict[str, List[str]] = {}
    
    async def analyze_response(
        self,
        user_id: str,
        message: str,
        context: Dict[str, Any]
    ) -> CheatingAnalysis:
        """
        Comprehensive analysis of a user's response for cheating indicators
        
        Args:
            user_id: User identifier
            message: The message to analyze
            context: Additional context (phase, history, timestamp, etc.)
        """
        indicators = []
        evidence = {}
        scores = {}
        
        # 1. Timing Analysis
        timing_result = self._analyze_timing(message, context)
        scores["timing"] = timing_result["score"]
        if timing_result["suspicious"]:
            indicators.append(f"Response timing: {timing_result['reason']}")
            evidence["timing"] = timing_result
        
        # 2. Content Analysis
        content_result = self._analyze_content(message)
        scores["content"] = content_result["score"]
        indicators.extend(content_result["indicators"])
        evidence["content"] = content_result
        
        # 3. Code Analysis (if contains code)
        if self._contains_code(message):
            code_result = self._analyze_code(message, user_id)
            scores["code"] = code_result["score"]
            indicators.extend(code_result["indicators"])
            evidence["code"] = code_result
        
        # 4. Pattern Deviation Analysis
        pattern_result = await self._analyze_pattern_deviation(user_id, message)
        scores["pattern"] = pattern_result["score"]
        if pattern_result["deviation_significant"]:
            indicators.append(f"Pattern deviation: {pattern_result['reason']}")
            evidence["pattern"] = pattern_result
        
        # 5. Plagiarism Check (against known submissions)
        plagiarism_result = self._check_plagiarism(message, user_id)
        scores["plagiarism"] = plagiarism_result["score"]
        if plagiarism_result["matches"]:
            indicators.append("Similar content found in other submissions")
            evidence["plagiarism"] = plagiarism_result
        
        # 6. AI Detection
        ai_result = self._detect_ai_generated(message)
        scores["ai"] = ai_result["score"]
        if ai_result["likely_ai"]:
            indicators.append("Response shows AI-generated patterns")
            evidence["ai"] = ai_result
        
        # Calculate overall suspicion
        overall_score = self._calculate_overall_score(scores)
        suspicion_level = self._score_to_level(overall_score)
        
        # Generate verification questions
        verification_questions = self._generate_verification_questions(
            message, context, indicators
        )
        
        # Calculate false positive probability
        bypass_probability = self._calculate_bypass_probability(
            scores, context, len(indicators)
        )
        
        # Determine recommended action
        recommended_action = self._get_recommended_action(
            suspicion_level, indicators, context
        )
        
        # Update user patterns
        self._update_user_pattern(user_id, message, context)
        
        # Store submission hash
        self._store_submission_hash(user_id, message)
        
        return CheatingAnalysis(
            suspicion_level=suspicion_level,
            confidence=1 - bypass_probability,
            indicators=indicators,
            evidence=evidence,
            recommended_action=recommended_action,
            verification_questions=verification_questions,
            bypass_probability=bypass_probability
        )
    
    # =========================================================================
    # ANALYSIS COMPONENTS
    # =========================================================================
    
    def _analyze_timing(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze response timing for suspicious patterns"""
        result = {
            "score": 0.0,
            "suspicious": False,
            "reason": None,
            "data": {}
        }
        
        last_message_time = context.get("last_message_time")
        if not last_message_time:
            return result
        
        # Calculate response time
        if isinstance(last_message_time, str):
            last_message_time = datetime.fromisoformat(last_message_time)
        
        response_time = (datetime.utcnow() - last_message_time).total_seconds()
        message_length = len(message)
        
        # Calculate expected typing time (rough estimate: 5 chars/second for typing)
        expected_min_time = message_length / 10  # Generous 10 chars/second
        
        result["data"]["response_time_seconds"] = response_time
        result["data"]["message_length"] = message_length
        result["data"]["expected_min_time"] = expected_min_time
        
        # Check for suspiciously fast response
        if response_time < expected_min_time * 0.5 and message_length > 200:
            result["score"] = min((expected_min_time - response_time) / expected_min_time, 0.8)
            result["suspicious"] = True
            result["reason"] = f"Response submitted in {response_time:.0f}s for {message_length} chars"
        
        # Check for complex code submitted very quickly
        if self._contains_code(message) and response_time < 60 and message_length > 300:
            result["score"] = max(result["score"], 0.5)
            result["suspicious"] = True
            result["reason"] = "Complex code submitted very quickly"
        
        return result
    
    def _analyze_content(self, message: str) -> Dict[str, Any]:
        """Analyze content for copy-paste indicators"""
        result = {
            "score": 0.0,
            "indicators": [],
            "data": {}
        }
        
        message_lower = message.lower()
        
        # Check for tutorial patterns
        tutorial_matches = sum(
            1 for pattern in self.TUTORIAL_PATTERNS
            if re.search(pattern, message_lower)
        )
        if tutorial_matches >= 2:
            result["indicators"].append(
                f"Contains tutorial-style language ({tutorial_matches} indicators)"
            )
            result["score"] += min(tutorial_matches * 0.1, 0.3)
        
        # Check for leftover URLs
        urls = re.findall(r'https?://[^\s]+', message)
        if urls:
            result["indicators"].append(f"Contains URLs: {urls[:3]}")
            result["score"] += 0.2
        
        # Check for unusual formatting
        if re.search(r'\t{2,}', message):
            result["indicators"].append("Contains unusual tab formatting")
            result["score"] += 0.1
        
        # Check for non-ASCII characters (might indicate rich text paste)
        non_ascii = re.findall(r'[^\x00-\x7F]+', message)
        if len(non_ascii) > 5:
            result["indicators"].append("Contains multiple non-ASCII sequences")
            result["score"] += 0.1
        
        # Check for overly perfect structure
        if re.search(r'^[\d]+\.\s+\*\*[^*]+\*\*', message, re.MULTILINE):
            count = len(re.findall(r'^[\d]+\.\s+\*\*[^*]+\*\*', message, re.MULTILINE))
            if count >= 3:
                result["indicators"].append(f"Very structured response ({count} formatted points)")
                result["score"] += 0.15
        
        result["data"]["tutorial_matches"] = tutorial_matches
        result["data"]["url_count"] = len(urls)
        
        return result
    
    def _analyze_code(
        self,
        message: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Analyze code for suspicious patterns"""
        result = {
            "score": 0.0,
            "indicators": [],
            "data": {}
        }
        
        # Extract code blocks
        code_blocks = re.findall(r'```[\w]*\n?([\s\S]*?)```', message)
        if not code_blocks:
            code_blocks = re.findall(r'`([^`]+)`', message)
        
        if not code_blocks:
            return result
        
        code = '\n'.join(code_blocks)
        
        # Check for professional code patterns
        pro_matches = sum(
            1 for pattern in self.PRO_CODE_PATTERNS
            if re.search(pattern, code.lower())
        )
        if pro_matches >= 2:
            result["indicators"].append(
                f"Code shows advanced patterns unusual for learning context"
            )
            result["score"] += min(pro_matches * 0.1, 0.3)
        
        # Check for comprehensive error handling
        try_count = len(re.findall(r'\btry\s*:', code))
        except_count = len(re.findall(r'\bexcept\b', code))
        if try_count >= 2 and except_count >= try_count:
            result["indicators"].append("Comprehensive error handling present")
            result["score"] += 0.15
        
        # Check for docstrings
        docstrings = len(re.findall(r'"""[\s\S]*?"""', code))
        if docstrings >= 2:
            result["indicators"].append(f"Contains {docstrings} docstrings")
            result["score"] += 0.1
        
        # Check for import statements (might indicate copy from larger project)
        imports = re.findall(r'^(?:from|import)\s+\w+', code, re.MULTILINE)
        if len(imports) >= 5:
            result["indicators"].append(f"Contains {len(imports)} import statements")
            result["score"] += 0.1
        
        # Calculate code style signature
        style_sig = self._calculate_code_signature(code)
        user_pattern = self.user_patterns.get(user_id)
        
        if user_pattern and user_pattern.code_style_signature:
            # Compare with user's historical style
            similarity = self._compare_signatures(
                style_sig,
                user_pattern.code_style_signature
            )
            if similarity < 0.5:  # Very different from usual style
                result["indicators"].append("Code style differs from user's historical pattern")
                result["score"] += 0.2
        
        result["data"]["pro_pattern_matches"] = pro_matches
        result["data"]["docstring_count"] = docstrings
        result["data"]["import_count"] = len(imports)
        result["data"]["style_signature"] = style_sig
        
        return result
    
    async def _analyze_pattern_deviation(
        self,
        user_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Analyze how much this response deviates from user's patterns"""
        result = {
            "score": 0.0,
            "deviation_significant": False,
            "reason": None,
            "data": {}
        }
        
        user_pattern = self.user_patterns.get(user_id)
        if not user_pattern or user_pattern.avg_length == 0:
            return result
        
        current_length = len(message)
        avg_length = user_pattern.avg_length
        
        # Check length deviation
        length_ratio = current_length / avg_length if avg_length > 0 else 1
        result["data"]["length_ratio"] = length_ratio
        result["data"]["user_avg_length"] = avg_length
        result["data"]["current_length"] = current_length
        
        if length_ratio > 3:  # More than 3x their average
            result["score"] = min((length_ratio - 3) * 0.1, 0.4)
            result["deviation_significant"] = True
            result["reason"] = f"Response {length_ratio:.1f}x longer than average"
        
        # Check vocabulary complexity deviation
        current_complexity = self._calculate_vocabulary_complexity(message)
        if user_pattern.vocabulary_complexity > 0:
            complexity_ratio = current_complexity / user_pattern.vocabulary_complexity
            result["data"]["complexity_ratio"] = complexity_ratio
            
            if complexity_ratio > 1.5:
                result["score"] = max(result["score"], min((complexity_ratio - 1.5) * 0.2, 0.3))
                result["deviation_significant"] = True
                result["reason"] = f"Vocabulary complexity {complexity_ratio:.1f}x higher than usual"
        
        return result
    
    def _check_plagiarism(
        self,
        message: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Check for plagiarism against stored submissions"""
        result = {
            "score": 0.0,
            "matches": [],
            "data": {}
        }
        
        message_hash = self._hash_content(message)
        
        # Check against all stored submissions
        for stored_user_id, hashes in self.submission_hashes.items():
            if stored_user_id == user_id:
                continue  # Skip own submissions
            
            for stored_hash in hashes:
                similarity = self._compare_hashes(message_hash, stored_hash)
                if similarity > 0.8:  # 80% similarity threshold
                    result["score"] = max(result["score"], similarity)
                    result["matches"].append({
                        "similarity": similarity,
                        "source": "other_submission"
                    })
        
        result["data"]["hash"] = message_hash[:16]  # Truncated for logging
        result["data"]["match_count"] = len(result["matches"])
        
        return result
    
    def _detect_ai_generated(self, message: str) -> Dict[str, Any]:
        """Detect if response appears to be AI-generated"""
        result = {
            "score": 0.0,
            "likely_ai": False,
            "indicators": [],
            "data": {}
        }
        
        message_lower = message.lower()
        
        # Check for AI patterns
        ai_matches = sum(
            1 for pattern in self.AI_PATTERNS
            if re.search(pattern, message_lower)
        )
        
        result["data"]["ai_pattern_matches"] = ai_matches
        
        if ai_matches >= 3:
            result["score"] = min(ai_matches * 0.15, 0.6)
            result["likely_ai"] = True
            result["indicators"].append(f"Contains {ai_matches} AI-typical phrases")
        
        # Check for unusual sentence length consistency (AI tends to be uniform)
        sentences = re.split(r'[.!?]+', message)
        if len(sentences) >= 5:
            lengths = [len(s.split()) for s in sentences if s.strip()]
            if lengths:
                avg_len = sum(lengths) / len(lengths)
                variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
                
                # Low variance = very consistent = potentially AI
                if variance < 10 and avg_len > 10:
                    result["score"] = max(result["score"], 0.3)
                    result["likely_ai"] = True
                    result["indicators"].append("Unusually consistent sentence structure")
                
                result["data"]["sentence_length_variance"] = variance
        
        # Check for excessive use of transition words
        transition_words = [
            "furthermore", "additionally", "moreover", "however",
            "consequently", "therefore", "nevertheless", "subsequently"
        ]
        transition_count = sum(
            len(re.findall(rf'\b{word}\b', message_lower))
            for word in transition_words
        )
        
        if transition_count >= 4:
            result["score"] = max(result["score"], 0.25)
            result["likely_ai"] = True
            result["indicators"].append(f"Excessive transition words ({transition_count})")
        
        result["data"]["transition_word_count"] = transition_count
        
        return result
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _contains_code(self, message: str) -> bool:
        """Check if message contains code"""
        return bool(
            re.search(r'```[\s\S]*?```', message) or
            re.search(r'def \w+\(', message) or
            re.search(r'function \w+\(', message) or
            re.search(r'class \w+', message)
        )
    
    def _calculate_vocabulary_complexity(self, text: str) -> float:
        """Calculate vocabulary complexity score"""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0
        
        unique_words = set(words)
        avg_word_length = sum(len(w) for w in words) / len(words)
        lexical_diversity = len(unique_words) / len(words)
        
        return (avg_word_length * 0.3 + lexical_diversity * 100 * 0.7)
    
    def _calculate_code_signature(self, code: str) -> str:
        """Calculate a signature representing code style"""
        features = []
        
        # Indentation style
        if re.search(r'^\t', code, re.MULTILINE):
            features.append("tabs")
        elif re.search(r'^  ', code, re.MULTILINE):
            features.append("2space")
        elif re.search(r'^    ', code, re.MULTILINE):
            features.append("4space")
        
        # Brace style
        if re.search(r'\)\s*{', code):
            features.append("same-line-brace")
        elif re.search(r'\)\s*\n\s*{', code):
            features.append("newline-brace")
        
        # Quote style
        single_quotes = len(re.findall(r"'[^']*'", code))
        double_quotes = len(re.findall(r'"[^"]*"', code))
        if single_quotes > double_quotes:
            features.append("single-quote")
        else:
            features.append("double-quote")
        
        # Comment style
        if re.search(r'#.*$', code, re.MULTILINE):
            features.append("hash-comments")
        if re.search(r'//.*$', code, re.MULTILINE):
            features.append("slash-comments")
        
        return hashlib.md5('|'.join(features).encode()).hexdigest()[:16]
    
    def _compare_signatures(self, sig1: str, sig2: str) -> float:
        """Compare two code signatures"""
        if not sig1 or not sig2:
            return 1.0
        
        # Simple character overlap
        set1 = set(sig1)
        set2 = set(sig2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0
    
    def _hash_content(self, content: str) -> str:
        """Create a content hash for plagiarism checking"""
        # Normalize whitespace and case
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _compare_hashes(self, hash1: str, hash2: str) -> float:
        """Compare two hashes (simplified similarity)"""
        # In production, use simhash or minhash for similarity
        return 1.0 if hash1 == hash2 else 0.0
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall suspicion score"""
        weights = {
            "timing": 0.15,
            "content": 0.20,
            "code": 0.25,
            "pattern": 0.15,
            "plagiarism": 0.15,
            "ai": 0.10
        }
        
        total_weight = sum(weights.get(k, 0) for k in scores)
        if total_weight == 0:
            return 0
        
        weighted_sum = sum(
            scores.get(k, 0) * weights.get(k, 0)
            for k in scores
        )
        
        return weighted_sum / total_weight
    
    def _score_to_level(self, score: float) -> SuspicionLevel:
        """Convert numeric score to suspicion level"""
        if score < 0.15:
            return SuspicionLevel.NONE
        elif score < 0.30:
            return SuspicionLevel.LOW
        elif score < 0.50:
            return SuspicionLevel.MEDIUM
        elif score < 0.70:
            return SuspicionLevel.HIGH
        else:
            return SuspicionLevel.CRITICAL
    
    def _calculate_bypass_probability(
        self,
        scores: Dict[str, float],
        context: Dict[str, Any],
        indicator_count: int
    ) -> float:
        """Calculate probability that this is a false positive"""
        base_probability = 0.1
        
        # Advanced users might legitimately have complex responses
        if context.get("experience_level") in ["advanced", "expert"]:
            base_probability += 0.2
        
        # In later phases, longer responses are expected
        phase = context.get("phase", "")
        if phase in ["practical_task", "industry_challenge"]:
            base_probability += 0.15
        
        # If only one indicator, more likely false positive
        if indicator_count == 1:
            base_probability += 0.2
        
        # If multiple strong indicators, less likely false positive
        if indicator_count >= 4:
            base_probability -= 0.15
        
        return max(0, min(base_probability, 0.9))
    
    def _get_recommended_action(
        self,
        level: SuspicionLevel,
        indicators: List[str],
        context: Dict[str, Any]
    ) -> str:
        """Get recommended action based on suspicion level"""
        actions = {
            SuspicionLevel.NONE: "Proceed normally",
            SuspicionLevel.LOW: "Continue monitoring, no intervention needed",
            SuspicionLevel.MEDIUM: "Ask clarifying questions to verify understanding",
            SuspicionLevel.HIGH: "Require verbal explanation of the response",
            SuspicionLevel.CRITICAL: "Request complete explanation before proceeding; consider flagging for review"
        }
        return actions.get(level, "Proceed with caution")
    
    def _generate_verification_questions(
        self,
        message: str,
        context: Dict[str, Any],
        indicators: List[str]
    ) -> List[str]:
        """Generate questions to verify genuine understanding"""
        questions = []
        
        # Generic questions
        questions.append("Can you explain this in your own words?")
        
        # If code was submitted
        if self._contains_code(message):
            questions.extend([
                "Walk me through how this code works step by step",
                "What would happen if we changed [X]?",
                "Why did you choose this approach over alternatives?",
                "What's the time complexity of this solution?",
                "Can you explain what this specific line does?"
            ])
        
        # If explanation was given
        if len(message) > 300 and not self._contains_code(message):
            questions.extend([
                "Can you give me a concrete example?",
                "How would you explain this to someone new to programming?",
                "What's the key insight that makes this work?"
            ])
        
        # Based on specific indicators
        if "tutorial-style language" in str(indicators):
            questions.append("Where did you learn this approach?")
        
        if "AI-generated patterns" in str(indicators):
            questions.append("Can you rephrase the key points in a different way?")
        
        return questions[:5]  # Return top 5 questions
    
    def _update_user_pattern(
        self,
        user_id: str,
        message: str,
        context: Dict[str, Any]
    ) -> None:
        """Update user's response pattern profile"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = ResponsePattern()
        
        pattern = self.user_patterns[user_id]
        
        # Update average length (exponential moving average)
        alpha = 0.3  # Weight for new observation
        current_length = len(message)
        if pattern.avg_length == 0:
            pattern.avg_length = current_length
        else:
            pattern.avg_length = alpha * current_length + (1 - alpha) * pattern.avg_length
        
        # Update vocabulary complexity
        current_complexity = self._calculate_vocabulary_complexity(message)
        if pattern.vocabulary_complexity == 0:
            pattern.vocabulary_complexity = current_complexity
        else:
            pattern.vocabulary_complexity = (
                alpha * current_complexity + (1 - alpha) * pattern.vocabulary_complexity
            )
        
        # Update code style signature
        if self._contains_code(message):
            code_blocks = re.findall(r'```[\w]*\n?([\s\S]*?)```', message)
            if code_blocks:
                pattern.code_style_signature = self._calculate_code_signature(
                    '\n'.join(code_blocks)
                )
    
    def _store_submission_hash(self, user_id: str, message: str) -> None:
        """Store submission hash for plagiarism checking"""
        if user_id not in self.submission_hashes:
            self.submission_hashes[user_id] = []
        
        content_hash = self._hash_content(message)
        
        # Keep only last 100 submissions per user
        if len(self.submission_hashes[user_id]) >= 100:
            self.submission_hashes[user_id].pop(0)
        
        self.submission_hashes[user_id].append(content_hash)


# =============================================================================
# VERIFICATION STRATEGIES
# =============================================================================

class VerificationStrategy:
    """
    Different strategies for verifying genuine understanding
    """
    
    @staticmethod
    def socratic_verification(topic: str, response: str) -> List[str]:
        """Generate Socratic questions to verify understanding"""
        return [
            f"If I changed [X], how would your approach differ?",
            f"What assumption is this based on?",
            f"Can you think of a case where this wouldn't work?",
            f"Why is this solution better than [alternative]?",
            f"What's the underlying principle here?"
        ]
    
    @staticmethod
    def modification_challenge(code: str) -> Dict[str, Any]:
        """Create a modification challenge to verify code understanding"""
        return {
            "type": "modification",
            "instruction": "Modify your solution to also handle [additional requirement]",
            "verify": "Ask to explain the changes"
        }
    
    @staticmethod
    def explanation_to_audience(topic: str) -> Dict[str, Any]:
        """Request explanation to different audience"""
        return {
            "type": "explain",
            "audiences": [
                "a 5-year-old",
                "a non-technical manager",
                "someone who's never programmed",
                "a senior engineer unfamiliar with this domain"
            ],
            "instruction": "Explain your solution as if talking to [audience]"
        }
    
    @staticmethod
    def trace_execution(code: str) -> Dict[str, Any]:
        """Request step-by-step execution trace"""
        return {
            "type": "trace",
            "instruction": "Walk me through what happens when this code runs with input [X]",
            "expected_elements": [
                "Variable states",
                "Decision points",
                "Loop iterations",
                "Final output"
            ]
        }


# Singleton detector instance
cheating_detector = CheatingDetector()
