"""
VidyaGuru Anti-Cheating System - Detection Service
===================================================

Core detection algorithms and verification challenge generation.
"""

import hashlib
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.anti_cheat.models import (
    SubmissionAnalysis,
    VerificationChallenge,
    UserIntegrityProfile,
    SuspiciousActivityLog,
    SubmissionFingerprint,
    SuspicionLevel,
    SuspicionType,
    VerificationType,
    VerificationStatus
)
from app.anti_cheat.schemas import (
    SubmissionMetrics,
    SubmissionWithMetrics,
    SuspicionIndicator,
    SuspicionLevelEnum,
    SuspicionTypeEnum,
    VerificationTypeEnum,
    SubmissionAnalysisResult,
    VerificationChallengeResponse,
    VerificationResultResponse,
    GenuineLearnerReminder,
    REMINDER_MESSAGES
)


# ============================================================================
# Configuration Constants
# ============================================================================

class DetectionConfig:
    """Configuration for detection thresholds"""
    
    # Paste detection
    LARGE_PASTE_THRESHOLD = 200  # Characters
    PASTE_RATIO_THRESHOLD = 0.8  # 80% of content pasted
    
    # Timing thresholds (multipliers of expected time)
    MIN_TIME_FACTOR = 0.15  # Suspicious if completed in < 15% of expected time
    MAX_TIME_FACTOR = 5.0   # Very slow might indicate external help
    
    # Typing speed (chars per minute)
    MIN_REASONABLE_TYPING_SPEED = 30
    MAX_REASONABLE_TYPING_SPEED = 600  # Professional typist
    SUPERHUMAN_TYPING_SPEED = 1000
    
    # Similarity thresholds
    IDENTICAL_THRESHOLD = 0.98  # Near-identical
    HIGH_SIMILARITY_THRESHOLD = 0.85
    MODERATE_SIMILARITY_THRESHOLD = 0.65
    
    # Suspicion score thresholds
    LOW_SUSPICION_THRESHOLD = 0.25
    MEDIUM_SUSPICION_THRESHOLD = 0.50
    HIGH_SUSPICION_THRESHOLD = 0.75
    CRITICAL_SUSPICION_THRESHOLD = 0.90
    
    # Verification settings
    VERIFICATION_EXPIRY_HOURS = 24
    MAX_VERIFICATION_ATTEMPTS = 2
    PASSING_SCORE = 0.6
    
    # Trust score adjustments
    TRUST_DECREASE_ON_FLAG = 0.05
    TRUST_DECREASE_ON_FAILED_VERIFICATION = 0.10
    TRUST_INCREASE_ON_PASSED_VERIFICATION = 0.02
    TRUST_RECOVERY_PER_CLEAN_SUBMISSION = 0.01


# ============================================================================
# Utility Functions
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, remove extra whitespace)"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def normalize_code(code: str) -> str:
    """Normalize code for comparison (remove comments, normalize whitespace)"""
    # Remove single-line comments
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    
    # Remove multi-line comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
    
    # Normalize whitespace
    code = re.sub(r'\s+', ' ', code)
    return code.strip()


def compute_hash(text: str) -> str:
    """Compute SHA-256 hash of text"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def compute_simhash(text: str, hash_bits: int = 64) -> str:
    """
    Compute SimHash for similarity detection.
    SimHash produces similar hashes for similar content.
    """
    # Tokenize
    tokens = re.findall(r'\w+', text.lower())
    
    # Initialize bit counts
    bit_counts = [0] * hash_bits
    
    for token in tokens:
        # Hash each token
        token_hash = int(hashlib.md5(token.encode()).hexdigest(), 16)
        
        for i in range(hash_bits):
            if token_hash & (1 << i):
                bit_counts[i] += 1
            else:
                bit_counts[i] -= 1
    
    # Generate final hash
    simhash = 0
    for i in range(hash_bits):
        if bit_counts[i] > 0:
            simhash |= (1 << i)
    
    return hex(simhash)[2:]


def compute_ngram_hashes(text: str, n: int = 3, num_hashes: int = 50) -> List[str]:
    """Compute n-gram hashes for partial matching"""
    tokens = re.findall(r'\w+', text.lower())
    ngrams = []
    
    for i in range(len(tokens) - n + 1):
        ngram = ' '.join(tokens[i:i+n])
        ngrams.append(compute_hash(ngram)[:16])  # Use first 16 chars
    
    # Return most common ngrams (or all if fewer than num_hashes)
    return list(set(ngrams))[:num_hashes]


def hamming_distance(hash1: str, hash2: str) -> int:
    """Calculate Hamming distance between two hex hashes"""
    try:
        int1 = int(hash1, 16)
        int2 = int(hash2, 16)
        xor = int1 ^ int2
        return bin(xor).count('1')
    except ValueError:
        return 64  # Max distance if conversion fails


def calculate_similarity_from_hamming(distance: int, bits: int = 64) -> float:
    """Convert Hamming distance to similarity score (0-1)"""
    return 1.0 - (distance / bits)


# ============================================================================
# Detection Algorithms
# ============================================================================

class PasteDetector:
    """Detects copy-paste behavior from typing metrics"""
    
    @staticmethod
    def analyze(
        content: str,
        metrics: SubmissionMetrics,
        expected_time_seconds: Optional[int] = None
    ) -> Tuple[bool, SuspicionIndicator]:
        """
        Analyze submission for paste-related suspicious behavior.
        
        Returns:
            Tuple of (is_suspicious, indicator)
        """
        char_count = len(content)
        
        # Check paste events
        if metrics.paste_events > 0:
            paste_ratio = metrics.largest_paste_size / max(char_count, 1)
            
            # Large paste detected
            if metrics.largest_paste_size >= DetectionConfig.LARGE_PASTE_THRESHOLD:
                severity = SuspicionLevelEnum.MEDIUM
                if paste_ratio > 0.9:
                    severity = SuspicionLevelEnum.HIGH
                elif paste_ratio > 0.5:
                    severity = SuspicionLevelEnum.MEDIUM
                
                return True, SuspicionIndicator(
                    type=SuspicionTypeEnum.LARGE_PASTE,
                    severity=severity,
                    confidence=min(0.95, paste_ratio + 0.3),
                    evidence={
                        "paste_events": metrics.paste_events,
                        "largest_paste_size": metrics.largest_paste_size,
                        "paste_ratio": round(paste_ratio, 3),
                        "total_keystrokes": metrics.total_keystrokes
                    },
                    description=f"Large paste detected: {metrics.largest_paste_size} characters "
                               f"({round(paste_ratio * 100)}% of submission)"
                )
        
        # Check if virtually no typing but significant content
        if char_count > 100 and metrics.total_keystrokes < char_count * 0.2:
            return True, SuspicionIndicator(
                type=SuspicionTypeEnum.COPY_PASTE_PATTERN,
                severity=SuspicionLevelEnum.HIGH,
                confidence=0.85,
                evidence={
                    "char_count": char_count,
                    "keystrokes": metrics.total_keystrokes,
                    "keystroke_ratio": round(metrics.total_keystrokes / max(char_count, 1), 3)
                },
                description="Very few keystrokes for the amount of content submitted"
            )
        
        return False, None


class TimingAnalyzer:
    """Analyzes submission timing for anomalies"""
    
    @staticmethod
    def analyze(
        metrics: SubmissionMetrics,
        expected_time_seconds: int,
        user_profile: Optional[UserIntegrityProfile] = None
    ) -> Tuple[bool, Optional[SuspicionIndicator]]:
        """
        Analyze submission timing for suspicious patterns.
        """
        actual_time = (metrics.end_time - metrics.start_time).total_seconds()
        
        # Adjust expected time based on user profile
        if user_profile and user_profile.typical_submission_time_factor:
            expected_time_seconds *= user_profile.typical_submission_time_factor
        
        time_ratio = actual_time / max(expected_time_seconds, 1)
        
        # Suspiciously fast
        if time_ratio < DetectionConfig.MIN_TIME_FACTOR:
            severity = SuspicionLevelEnum.HIGH if time_ratio < 0.05 else SuspicionLevelEnum.MEDIUM
            
            return True, SuspicionIndicator(
                type=SuspicionTypeEnum.RAPID_SUBMISSION,
                severity=severity,
                confidence=min(0.9, 1.0 - time_ratio),
                evidence={
                    "actual_seconds": round(actual_time),
                    "expected_seconds": expected_time_seconds,
                    "time_ratio": round(time_ratio, 3)
                },
                description=f"Submission completed in {round(actual_time)}s, "
                           f"expected ~{expected_time_seconds}s ({round(time_ratio * 100)}% of expected time)"
            )
        
        # Check focus time vs total time
        if metrics.focus_time_seconds > 0:
            focus_ratio = metrics.focus_time_seconds / max(actual_time, 1)
            if focus_ratio < 0.3 and actual_time > 300:  # Less than 30% focus for tasks > 5min
                return True, SuspicionIndicator(
                    type=SuspicionTypeEnum.TIME_ANOMALY,
                    severity=SuspicionLevelEnum.LOW,
                    confidence=0.6,
                    evidence={
                        "focus_time": metrics.focus_time_seconds,
                        "total_time": round(actual_time),
                        "focus_ratio": round(focus_ratio, 3),
                        "tab_switches": metrics.tab_switches
                    },
                    description="User spent significant time away from the task window"
                )
        
        return False, None


class TypingPatternAnalyzer:
    """Analyzes typing patterns for anomalies"""
    
    @staticmethod
    def analyze(
        content: str,
        metrics: SubmissionMetrics,
        user_profile: Optional[UserIntegrityProfile] = None
    ) -> Tuple[bool, Optional[SuspicionIndicator]]:
        """
        Analyze typing patterns for suspicious behavior.
        """
        if len(metrics.typing_events) == 0:
            return False, None
        
        # Calculate actual typing speed (excluding paste events)
        typed_chars = metrics.total_keystrokes
        actual_time_minutes = max(
            (metrics.end_time - metrics.start_time).total_seconds() / 60,
            0.1
        )
        typing_speed = typed_chars / actual_time_minutes
        
        # Superhuman typing speed
        if typing_speed > DetectionConfig.SUPERHUMAN_TYPING_SPEED:
            return True, SuspicionIndicator(
                type=SuspicionTypeEnum.TYPING_PATTERN_ANOMALY,
                severity=SuspicionLevelEnum.HIGH,
                confidence=0.9,
                evidence={
                    "typing_speed": round(typing_speed),
                    "threshold": DetectionConfig.SUPERHUMAN_TYPING_SPEED,
                    "typed_chars": typed_chars,
                    "time_minutes": round(actual_time_minutes, 2)
                },
                description=f"Unusually high typing speed detected: {round(typing_speed)} chars/min"
            )
        
        # Compare to user's baseline if available
        if user_profile and user_profile.avg_typing_speed:
            baseline = user_profile.avg_typing_speed
            std_dev = user_profile.typing_speed_std_dev or (baseline * 0.3)
            
            z_score = abs(typing_speed - baseline) / max(std_dev, 1)
            
            if z_score > 3:  # More than 3 standard deviations
                return True, SuspicionIndicator(
                    type=SuspicionTypeEnum.TYPING_PATTERN_ANOMALY,
                    severity=SuspicionLevelEnum.MEDIUM,
                    confidence=min(0.8, z_score / 5),
                    evidence={
                        "typing_speed": round(typing_speed),
                        "baseline_speed": round(baseline),
                        "std_dev": round(std_dev),
                        "z_score": round(z_score, 2)
                    },
                    description=f"Typing pattern differs significantly from user's baseline"
                )
        
        return False, None


class SimilarityDetector:
    """Detects identical or very similar submissions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_similar_submissions(
        self,
        content: str,
        task_id: UUID,
        exclude_user_id: Optional[UUID] = None
    ) -> Tuple[List[UUID], float]:
        """
        Find submissions similar to the given content.
        
        Returns:
            Tuple of (similar_submission_ids, highest_similarity_score)
        """
        normalized = normalize_text(content)
        content_hash = compute_hash(normalized)
        simhash = compute_simhash(normalized)
        
        # Find fingerprints for the same task
        query = select(SubmissionFingerprint).where(
            SubmissionFingerprint.task_id == task_id
        )
        
        result = await self.db.execute(query)
        fingerprints = result.scalars().all()
        
        similar_ids = []
        highest_score = 0.0
        
        for fp in fingerprints:
            # Exact match
            if fp.content_hash == content_hash:
                if exclude_user_id:
                    # Check if it's from the same user
                    analysis = await self.db.get(SubmissionAnalysis, fp.submission_analysis_id)
                    if analysis and analysis.user_id == exclude_user_id:
                        continue
                
                similar_ids.append(fp.submission_analysis_id)
                highest_score = 1.0
                continue
            
            # SimHash similarity
            distance = hamming_distance(simhash, fp.simhash)
            similarity = calculate_similarity_from_hamming(distance)
            
            if similarity > DetectionConfig.HIGH_SIMILARITY_THRESHOLD:
                similar_ids.append(fp.submission_analysis_id)
                highest_score = max(highest_score, similarity)
        
        return similar_ids, highest_score
    
    async def analyze(
        self,
        content: str,
        task_id: UUID,
        user_id: UUID
    ) -> Tuple[bool, Optional[SuspicionIndicator]]:
        """
        Analyze content for similarity to existing submissions.
        """
        similar_ids, highest_score = await self.find_similar_submissions(
            content, task_id, exclude_user_id=user_id
        )
        
        if highest_score >= DetectionConfig.IDENTICAL_THRESHOLD:
            return True, SuspicionIndicator(
                type=SuspicionTypeEnum.IDENTICAL_ANSWER,
                severity=SuspicionLevelEnum.CRITICAL,
                confidence=highest_score,
                evidence={
                    "similarity_score": round(highest_score, 3),
                    "similar_submission_count": len(similar_ids)
                },
                description=f"Submission is nearly identical to {len(similar_ids)} existing submission(s)"
            )
        
        if highest_score >= DetectionConfig.HIGH_SIMILARITY_THRESHOLD:
            return True, SuspicionIndicator(
                type=SuspicionTypeEnum.IDENTICAL_ANSWER,
                severity=SuspicionLevelEnum.HIGH,
                confidence=highest_score,
                evidence={
                    "similarity_score": round(highest_score, 3),
                    "similar_submission_count": len(similar_ids)
                },
                description=f"Submission is highly similar to existing submissions ({round(highest_score * 100)}% match)"
            )
        
        return False, None


class SkillConsistencyChecker:
    """Checks if submission quality is consistent with user's skill level"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze(
        self,
        content: str,
        task_difficulty: str,
        user_id: UUID,
        task_type: str
    ) -> Tuple[bool, Optional[SuspicionIndicator]]:
        """
        Check if the quality of submission is consistent with user's demonstrated skill level.
        """
        # This would integrate with the skill tracking system
        # For now, we check basic heuristics
        
        # Get user's skill level from tasks module
        # (In production, this would query the UserSkill table)
        
        # Placeholder logic - in real implementation:
        # 1. Get user's skill level for relevant category
        # 2. Analyze submission complexity
        # 3. Check if there's a mismatch
        
        return False, None


# ============================================================================
# Main Detection Service
# ============================================================================

class SubmissionAnalyzer:
    """Main service for analyzing submissions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.similarity_detector = SimilarityDetector(db)
        self.skill_checker = SkillConsistencyChecker(db)
    
    async def analyze_submission(
        self,
        submission: SubmissionWithMetrics,
        task_id: UUID,
        expected_time_seconds: int = 600,
        task_type: str = "general",
        task_difficulty: str = "intermediate"
    ) -> SubmissionAnalysisResult:
        """
        Perform comprehensive analysis of a submission.
        """
        content = submission.content
        metrics = submission.metrics
        user_id = submission.task_assignment_id  # Would get from task assignment
        
        indicators: List[SuspicionIndicator] = []
        
        # Get user profile
        profile_result = await self.db.execute(
            select(UserIntegrityProfile).where(
                UserIntegrityProfile.user_id == user_id
            )
        )
        user_profile = profile_result.scalar_one_or_none()
        
        # 1. Paste Detection
        is_suspicious, indicator = PasteDetector.analyze(content, metrics, expected_time_seconds)
        if is_suspicious and indicator:
            indicators.append(indicator)
        
        # 2. Timing Analysis
        is_suspicious, indicator = TimingAnalyzer.analyze(metrics, expected_time_seconds, user_profile)
        if is_suspicious and indicator:
            indicators.append(indicator)
        
        # 3. Typing Pattern Analysis
        is_suspicious, indicator = TypingPatternAnalyzer.analyze(content, metrics, user_profile)
        if is_suspicious and indicator:
            indicators.append(indicator)
        
        # 4. Similarity Detection
        is_suspicious, indicator = await self.similarity_detector.analyze(
            content, task_id, user_id
        )
        if is_suspicious and indicator:
            indicators.append(indicator)
        
        # 5. Skill Consistency Check
        is_suspicious, indicator = await self.skill_checker.analyze(
            content, task_difficulty, user_id, task_type
        )
        if is_suspicious and indicator:
            indicators.append(indicator)
        
        # Calculate overall suspicion score
        suspicion_score = self._calculate_overall_score(indicators)
        suspicion_level = self._determine_suspicion_level(suspicion_score)
        
        # Determine if verification is required
        requires_verification = self._should_require_verification(
            suspicion_score, suspicion_level, user_profile
        )
        
        # Recommend verification type
        recommended_type = None
        if requires_verification:
            recommended_type = self._recommend_verification_type(indicators, task_type)
        
        # Create analysis record
        analysis = await self._create_analysis_record(
            submission, indicators, suspicion_score, suspicion_level, requires_verification
        )
        
        # Generate summary
        summary = self._generate_summary(indicators, suspicion_level)
        
        return SubmissionAnalysisResult(
            submission_analysis_id=analysis.id,
            task_assignment_id=submission.task_assignment_id,
            suspicion_level=suspicion_level,
            suspicion_score=suspicion_score,
            requires_verification=requires_verification,
            indicators=indicators,
            recommended_verification_type=recommended_type,
            summary=summary
        )
    
    def _calculate_overall_score(self, indicators: List[SuspicionIndicator]) -> float:
        """Calculate weighted suspicion score from indicators"""
        if not indicators:
            return 0.0
        
        # Weights based on severity
        severity_weights = {
            SuspicionLevelEnum.LOW: 0.15,
            SuspicionLevelEnum.MEDIUM: 0.35,
            SuspicionLevelEnum.HIGH: 0.65,
            SuspicionLevelEnum.CRITICAL: 1.0
        }
        
        # Calculate weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        for indicator in indicators:
            weight = severity_weights.get(indicator.severity, 0.5)
            weighted_sum += indicator.confidence * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Apply penalty for multiple indicators
        base_score = weighted_sum / total_weight
        indicator_penalty = min(0.3, len(indicators) * 0.05)
        
        return min(1.0, base_score + indicator_penalty)
    
    def _determine_suspicion_level(self, score: float) -> SuspicionLevelEnum:
        """Determine suspicion level from score"""
        if score >= DetectionConfig.CRITICAL_SUSPICION_THRESHOLD:
            return SuspicionLevelEnum.CRITICAL
        elif score >= DetectionConfig.HIGH_SUSPICION_THRESHOLD:
            return SuspicionLevelEnum.HIGH
        elif score >= DetectionConfig.MEDIUM_SUSPICION_THRESHOLD:
            return SuspicionLevelEnum.MEDIUM
        elif score >= DetectionConfig.LOW_SUSPICION_THRESHOLD:
            return SuspicionLevelEnum.LOW
        else:
            return SuspicionLevelEnum.NONE
    
    def _should_require_verification(
        self,
        score: float,
        level: SuspicionLevelEnum,
        profile: Optional[UserIntegrityProfile]
    ) -> bool:
        """Determine if verification should be required"""
        # Always require for high/critical
        if level in [SuspicionLevelEnum.HIGH, SuspicionLevelEnum.CRITICAL]:
            return True
        
        # Always require if user profile mandates it
        if profile and profile.requires_verification_always:
            return True
        
        # Medium suspicion with low trust score
        if level == SuspicionLevelEnum.MEDIUM:
            if profile and profile.trust_score < 0.7:
                return True
            return score > 0.6  # Higher threshold for medium
        
        return False
    
    def _recommend_verification_type(
        self,
        indicators: List[SuspicionIndicator],
        task_type: str
    ) -> VerificationTypeEnum:
        """Recommend most appropriate verification type"""
        # Check indicator types
        indicator_types = {ind.type for ind in indicators}
        
        # For identical/copied answers, ask to explain in own words
        if SuspicionTypeEnum.IDENTICAL_ANSWER in indicator_types:
            return VerificationTypeEnum.EXPLAIN_IN_OWN_WORDS
        
        # For paste detection on coding tasks, ask for modification
        if SuspicionTypeEnum.LARGE_PASTE in indicator_types:
            if task_type in ["coding_exercise", "coding"]:
                return VerificationTypeEnum.CODE_MODIFICATION
            else:
                return VerificationTypeEnum.FOLLOW_UP_QUESTION
        
        # For timing anomalies, ask concept questions
        if SuspicionTypeEnum.RAPID_SUBMISSION in indicator_types:
            return VerificationTypeEnum.CONCEPT_QUESTION
        
        # Default to follow-up question
        return VerificationTypeEnum.FOLLOW_UP_QUESTION
    
    async def _create_analysis_record(
        self,
        submission: SubmissionWithMetrics,
        indicators: List[SuspicionIndicator],
        score: float,
        level: SuspicionLevelEnum,
        requires_verification: bool
    ) -> SubmissionAnalysis:
        """Create and persist analysis record"""
        content = submission.content
        metrics = submission.metrics
        
        # Calculate submission metrics
        actual_time = int((metrics.end_time - metrics.start_time).total_seconds())
        
        # Compute hashes
        normalized = normalize_text(content)
        similarity_hash = compute_hash(normalized)
        
        # Create analysis
        analysis = SubmissionAnalysis(
            task_assignment_id=submission.task_assignment_id,
            user_id=submission.task_assignment_id,  # Would get actual user_id
            submission_text=content,
            char_count=len(content),
            word_count=len(content.split()),
            typing_events_count=len(metrics.typing_events),
            paste_events=metrics.paste_events,
            largest_paste_size=metrics.largest_paste_size,
            time_to_submit_seconds=actual_time,
            similarity_hash=similarity_hash,
            suspicion_level=SuspicionLevel(level.value),
            suspicion_types=[ind.type.value for ind in indicators],
            suspicion_score=score,
            suspicion_details={
                "indicators": [
                    {
                        "type": ind.type.value,
                        "severity": ind.severity.value,
                        "confidence": ind.confidence,
                        "description": ind.description
                    }
                    for ind in indicators
                ]
            },
            requires_verification=requires_verification,
            is_flagged=level in [SuspicionLevelEnum.HIGH, SuspicionLevelEnum.CRITICAL]
        )
        
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        
        return analysis
    
    def _generate_summary(
        self,
        indicators: List[SuspicionIndicator],
        level: SuspicionLevelEnum
    ) -> str:
        """Generate human-readable summary"""
        if level == SuspicionLevelEnum.NONE:
            return "No suspicious patterns detected."
        
        if not indicators:
            return f"Suspicion level: {level.value}"
        
        descriptions = [ind.description for ind in indicators[:3]]
        return " | ".join(descriptions)


# ============================================================================
# Verification Challenge Service
# ============================================================================

class VerificationService:
    """Service for creating and evaluating verification challenges"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_challenge(
        self,
        analysis_id: UUID,
        user_id: UUID,
        verification_type: VerificationTypeEnum,
        original_content: str,
        task_context: Dict[str, Any]
    ) -> VerificationChallengeResponse:
        """Create a verification challenge based on the analysis"""
        
        # Generate challenge based on type
        if verification_type == VerificationTypeEnum.FOLLOW_UP_QUESTION:
            prompt, context = self._generate_follow_up_question(original_content, task_context)
        elif verification_type == VerificationTypeEnum.CODE_MODIFICATION:
            prompt, context = self._generate_code_modification(original_content, task_context)
        elif verification_type == VerificationTypeEnum.EXPLAIN_IN_OWN_WORDS:
            prompt, context = self._generate_explain_prompt(original_content, task_context)
        elif verification_type == VerificationTypeEnum.CONCEPT_QUESTION:
            prompt, context = self._generate_concept_question(original_content, task_context)
        else:
            prompt, context = self._generate_follow_up_question(original_content, task_context)
        
        # Calculate expiry
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=DetectionConfig.VERIFICATION_EXPIRY_HOURS
        )
        
        # Create challenge record
        challenge = VerificationChallenge(
            submission_analysis_id=analysis_id,
            user_id=user_id,
            verification_type=VerificationType(verification_type.value),
            challenge_prompt=prompt,
            challenge_context=context,
            original_code=original_content if verification_type == VerificationTypeEnum.CODE_MODIFICATION else None,
            expected_keywords=context.get("expected_keywords", []),
            min_response_length=context.get("min_length", 50),
            expires_at=expires_at,
            max_attempts=DetectionConfig.MAX_VERIFICATION_ATTEMPTS
        )
        
        self.db.add(challenge)
        await self.db.commit()
        await self.db.refresh(challenge)
        
        return VerificationChallengeResponse(
            id=challenge.id,
            verification_type=verification_type,
            prompt=prompt,
            context=context,
            original_code=challenge.original_code,
            min_response_length=challenge.min_response_length,
            expires_at=expires_at,
            attempt_number=1,
            max_attempts=DetectionConfig.MAX_VERIFICATION_ATTEMPTS
        )
    
    def _generate_follow_up_question(
        self,
        content: str,
        task_context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate a follow-up question about the submission"""
        task_title = task_context.get("title", "this task")
        
        prompts = [
            f"You mentioned a key concept in your solution. Can you explain why this approach works for {task_title}?",
            "What would happen if we changed one of the key conditions in your solution? How would the output differ?",
            "Can you walk through your thought process for the most challenging part of this solution?",
            "What alternative approach did you consider before arriving at this solution?"
        ]
        
        import random
        prompt = random.choice(prompts)
        
        return prompt, {
            "min_length": 75,
            "expected_keywords": task_context.get("key_concepts", []),
            "type": "follow_up"
        }
    
    def _generate_code_modification(
        self,
        code: str,
        task_context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate a code modification challenge"""
        modifications = [
            ("Add input validation", "Add validation to check for edge cases like empty input or invalid values."),
            ("Add error handling", "Wrap the main logic in proper error handling."),
            ("Optimize performance", "Can you identify and improve any inefficient parts of the code?"),
            ("Add a feature", "Modify the code to also return the count/length of the result."),
            ("Refactor", "Break down the solution into smaller, reusable functions.")
        ]
        
        import random
        mod_type, prompt = random.choice(modifications)
        
        return prompt, {
            "modification_type": mod_type,
            "original_code": code,
            "min_length": 50,
            "type": "code_modification"
        }
    
    def _generate_explain_prompt(
        self,
        content: str,
        task_context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate an explain-in-own-words challenge"""
        topic = task_context.get("topic", "the concept used")
        
        prompt = (
            f"Please explain {topic} in your own words, as if you were teaching "
            "it to someone who has never heard of it before. Use simple language "
            "and your own examples."
        )
        
        return prompt, {
            "min_length": 100,
            "forbidden_phrases": task_context.get("common_phrases", []),
            "expected_keywords": task_context.get("key_concepts", []),
            "type": "explain"
        }
    
    def _generate_concept_question(
        self,
        content: str,
        task_context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate a conceptual understanding question"""
        topic = task_context.get("topic", "this topic")
        
        prompts = [
            f"What is the main purpose of the approach you used? Why is it suitable for this type of problem?",
            f"How does your solution handle edge cases? Give an example.",
            f"If you had to explain the core concept behind your solution to a beginner, what would you say?",
            f"What would be the disadvantages of your approach? Are there any limitations?"
        ]
        
        import random
        prompt = random.choice(prompts)
        
        return prompt, {
            "min_length": 75,
            "expected_keywords": task_context.get("key_concepts", []),
            "type": "concept"
        }
    
    async def evaluate_response(
        self,
        challenge_id: UUID,
        response: str,
        typing_metrics: Optional[SubmissionMetrics] = None
    ) -> VerificationResultResponse:
        """Evaluate user's response to verification challenge"""
        
        # Get challenge
        challenge = await self.db.get(VerificationChallenge, challenge_id)
        if not challenge:
            raise ValueError("Challenge not found")
        
        # Check expiry
        if datetime.now(timezone.utc) > challenge.expires_at:
            challenge.status = VerificationStatus.EXPIRED
            await self.db.commit()
            
            return VerificationResultResponse(
                challenge_id=challenge_id,
                status=VerificationStatusEnum.EXPIRED,
                passed=False,
                score=0.0,
                feedback="This verification challenge has expired.",
                can_retry=False,
                remaining_attempts=0,
                message=REMINDER_MESSAGES["failed_verification"].message
            )
        
        # Update challenge status
        challenge.status = VerificationStatus.IN_PROGRESS
        challenge.started_at = challenge.started_at or datetime.now(timezone.utc)
        challenge.user_response = response
        
        # Evaluate response
        score, analysis = await self._evaluate_response_quality(
            response,
            challenge,
            typing_metrics
        )
        
        # Determine pass/fail
        passed = score >= DetectionConfig.PASSING_SCORE
        
        # Update challenge
        challenge.score = score
        challenge.passed = passed
        challenge.response_analysis = analysis
        challenge.completed_at = datetime.now(timezone.utc)
        challenge.status = VerificationStatus.PASSED if passed else VerificationStatus.FAILED
        
        # Generate feedback
        feedback, areas = self._generate_feedback(score, analysis, passed)
        challenge.feedback_message = feedback
        
        await self.db.commit()
        
        # Update user integrity profile
        await self._update_integrity_profile(challenge.user_id, passed)
        
        # Check if retry is allowed
        can_retry = not passed and challenge.attempt_number < challenge.max_attempts
        remaining_attempts = max(0, challenge.max_attempts - challenge.attempt_number)
        
        # Get appropriate message
        if passed:
            message = (
                "Great job! Your response demonstrates a good understanding of the concept. "
                "Keep up the excellent work! 🌟"
            )
        else:
            message = REMINDER_MESSAGES["failed_verification"].message
        
        return VerificationResultResponse(
            challenge_id=challenge_id,
            status=VerificationStatusEnum(challenge.status.value),
            passed=passed,
            score=score,
            feedback=feedback,
            areas_for_improvement=areas,
            can_retry=can_retry,
            remaining_attempts=remaining_attempts,
            message=message
        )
    
    async def _evaluate_response_quality(
        self,
        response: str,
        challenge: VerificationChallenge,
        typing_metrics: Optional[SubmissionMetrics]
    ) -> Tuple[float, Dict[str, Any]]:
        """Evaluate the quality of a verification response"""
        analysis = {}
        score_components = []
        
        # 1. Length check
        word_count = len(response.split())
        char_count = len(response)
        
        if char_count < challenge.min_response_length:
            analysis["length_issue"] = True
            score_components.append(0.3)
        else:
            analysis["length_issue"] = False
            score_components.append(0.8)
        
        # 2. Keyword presence
        if challenge.expected_keywords:
            response_lower = response.lower()
            found_keywords = sum(
                1 for kw in challenge.expected_keywords 
                if kw.lower() in response_lower
            )
            keyword_ratio = found_keywords / len(challenge.expected_keywords)
            analysis["keyword_ratio"] = keyword_ratio
            score_components.append(0.4 + (keyword_ratio * 0.6))
        else:
            score_components.append(0.7)  # Neutral if no keywords expected
        
        # 3. Response uniqueness (not copy of original)
        if challenge.verification_type == VerificationType.EXPLAIN_IN_OWN_WORDS:
            # Check against forbidden phrases from challenge context
            context = challenge.challenge_context or {}
            forbidden = context.get("forbidden_phrases", [])
            
            found_forbidden = sum(
                1 for phrase in forbidden 
                if phrase.lower() in response.lower()
            )
            
            if forbidden:
                uniqueness = 1.0 - (found_forbidden / len(forbidden))
            else:
                uniqueness = 0.8
            
            analysis["uniqueness_score"] = uniqueness
            score_components.append(uniqueness)
        
        # 4. Response coherence (basic check)
        sentences = re.split(r'[.!?]+', response)
        valid_sentences = sum(1 for s in sentences if len(s.strip().split()) >= 3)
        
        if len(sentences) > 0:
            coherence = min(1.0, valid_sentences / max(len(sentences), 1))
        else:
            coherence = 0.3
        
        analysis["coherence_score"] = coherence
        score_components.append(0.5 + (coherence * 0.5))
        
        # 5. Typing metrics check (if available)
        if typing_metrics and typing_metrics.paste_events > 0:
            paste_ratio = typing_metrics.largest_paste_size / max(char_count, 1)
            if paste_ratio > 0.5:
                analysis["paste_detected"] = True
                score_components.append(0.3)  # Penalty for pasting in verification
            else:
                score_components.append(0.9)
        
        # Calculate final score
        final_score = sum(score_components) / len(score_components)
        analysis["component_scores"] = score_components
        
        return min(1.0, final_score), analysis
    
    def _generate_feedback(
        self,
        score: float,
        analysis: Dict[str, Any],
        passed: bool
    ) -> Tuple[str, List[str]]:
        """Generate feedback based on evaluation"""
        areas = []
        
        if analysis.get("length_issue"):
            areas.append("Provide more detailed explanations")
        
        if analysis.get("keyword_ratio", 1.0) < 0.5:
            areas.append("Include key concepts and terminology")
        
        if analysis.get("uniqueness_score", 1.0) < 0.6:
            areas.append("Use your own words to explain the concept")
        
        if analysis.get("coherence_score", 1.0) < 0.6:
            areas.append("Structure your response with clear, complete sentences")
        
        if analysis.get("paste_detected"):
            areas.append("Type your response instead of copying from other sources")
        
        if passed:
            feedback = (
                "Your response shows good understanding! "
                f"Score: {round(score * 100)}%. "
                "You've demonstrated that you can explain this concept effectively."
            )
        else:
            feedback = (
                "Your response needs some improvement. "
                f"Score: {round(score * 100)}%. "
                "Don't worry - this is a chance to strengthen your understanding. "
                "Try to explain the concept in more depth using your own words."
            )
        
        return feedback, areas
    
    async def _update_integrity_profile(self, user_id: UUID, passed: bool):
        """Update user's integrity profile after verification"""
        result = await self.db.execute(
            select(UserIntegrityProfile).where(
                UserIntegrityProfile.user_id == user_id
            )
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            # Create new profile
            profile = UserIntegrityProfile(
                user_id=user_id,
                verifications_issued=1
            )
            self.db.add(profile)
        else:
            profile.verifications_issued += 1
        
        if passed:
            profile.verifications_passed += 1
            profile.trust_score = min(
                1.0,
                profile.trust_score + DetectionConfig.TRUST_INCREASE_ON_PASSED_VERIFICATION
            )
        else:
            profile.verifications_failed += 1
            profile.trust_score = max(
                0.0,
                profile.trust_score - DetectionConfig.TRUST_DECREASE_ON_FAILED_VERIFICATION
            )
            profile.warnings_issued += 1
            profile.last_warning_at = datetime.now(timezone.utc)
        
        # Update integrity level
        if profile.trust_score >= 0.8:
            profile.integrity_level = "trusted"
        elif profile.trust_score >= 0.5:
            profile.integrity_level = "monitored"
        else:
            profile.integrity_level = "restricted"
            profile.requires_verification_always = True
        
        await self.db.commit()


# ============================================================================
# Integrity Profile Service
# ============================================================================

class IntegrityService:
    """Service for managing user integrity profiles"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_profile(self, user_id: UUID) -> UserIntegrityProfile:
        """Get or create user integrity profile"""
        result = await self.db.execute(
            select(UserIntegrityProfile).where(
                UserIntegrityProfile.user_id == user_id
            )
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = UserIntegrityProfile(user_id=user_id)
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
        
        return profile
    
    async def update_on_submission(
        self,
        user_id: UUID,
        was_flagged: bool,
        suspicion_score: float
    ):
        """Update profile after a submission"""
        profile = await self.get_or_create_profile(user_id)
        
        profile.total_submissions += 1
        
        if was_flagged:
            profile.flagged_submissions += 1
            profile.trust_score = max(
                0.0,
                profile.trust_score - DetectionConfig.TRUST_DECREASE_ON_FLAG
            )
        else:
            # Small trust recovery for clean submissions
            profile.trust_score = min(
                1.0,
                profile.trust_score + DetectionConfig.TRUST_RECOVERY_PER_CLEAN_SUBMISSION
            )
        
        await self.db.commit()
    
    async def get_reminder_message(
        self,
        user_id: UUID,
        suspicion_type: Optional[SuspicionTypeEnum] = None
    ) -> GenuineLearnerReminder:
        """Get appropriate reminder message for user"""
        if suspicion_type == SuspicionTypeEnum.LARGE_PASTE:
            return REMINDER_MESSAGES["large_paste"]
        elif suspicion_type == SuspicionTypeEnum.IDENTICAL_ANSWER:
            return REMINDER_MESSAGES["identical_answer"]
        elif suspicion_type:
            return REMINDER_MESSAGES["verification_request"]
        else:
            return REMINDER_MESSAGES["general_integrity"]
    
    async def log_suspicious_activity(
        self,
        user_id: UUID,
        analysis_id: UUID,
        suspicion_type: SuspicionTypeEnum,
        severity: SuspicionLevelEnum,
        description: str,
        evidence: Dict[str, Any]
    ):
        """Log suspicious activity for review"""
        log = SuspiciousActivityLog(
            user_id=user_id,
            submission_analysis_id=analysis_id,
            suspicion_type=SuspicionType(suspicion_type.value),
            severity=SuspicionLevel(severity.value),
            description=description,
            evidence=evidence
        )
        
        self.db.add(log)
        await self.db.commit()
