"""
Template #34: Live Conversation Analyst (Simulated)
Advanced conversation analysis system for meeting transcripts
"""

import os
import json
import sqlite3
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
import csv
import io
from dataclasses import dataclass, asdict
from enum import Enum
import chardet

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Live Conversation Analyst",
    description="Advanced conversation analysis system for meeting transcripts",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_PATH = "/workspace/conversation_analyst.db"
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_database():
    """Initialize SQLite database for conversation analysis"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Conversation sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_sessions (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            total_speakers INTEGER NOT NULL,
            total_segments INTEGER NOT NULL,
            duration_minutes REAL,
            analysis_status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    # Speaker analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS speaker_analysis (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            speaker_name TEXT NOT NULL,
            speaker_role TEXT,
            emotional_peaks INTEGER DEFAULT 0,
            emotional_lows INTEGER DEFAULT 0,
            total_statements INTEGER DEFAULT 0,
            dominant_emotion TEXT,
            engagement_score REAL DEFAULT 0.0,
            speaking_time_percentage REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
        )
    ''')
    
    # Decision points table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decision_points (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            decision_text TEXT NOT NULL,
            importance_score REAL NOT NULL,
            participants TEXT NOT NULL,
            consensus_level TEXT NOT NULL,
            time_stamp TEXT NOT NULL,
            context_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
        )
    ''')
    
    # Conversation segments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_segments (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            speaker TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp REAL NOT NULL,
            emotional_state TEXT,
            sentiment_score REAL,
            segment_type TEXT,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# Enums for conversation analysis
class EmotionalState(Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    ENGAGED = "engaged"
    DISENGAGED = "disengaged"

class DecisionType(Enum):
    APPROVAL = "approval"
    REJECTION = "rejection"
    DEFERRED = "deferred"
    CONSENSUS = "consensus"
    ACTION_ITEM = "action_item"
    DISCUSSION = "discussion"

class ConsensusLevel(Enum):
    UNANIMOUS = "unanimous"
    STRONG_CONSENSUS = "strong_consensus"
    MODERATE_CONSENSUS = "moderate_consensus"
    MINORITY_SUPPORT = "minority_support"
    NO_CONSENSUS = "no_consensus"

@dataclass
class SpeakerSegment:
    """Represents a segment of speech from a speaker"""
    speaker: str
    content: str
    timestamp: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None

@dataclass
class EmotionalAnalysis:
    """Emotional state analysis for a speaker"""
    speaker: str
    current_emotion: EmotionalState
    emotion_intensity: float  # 0.0 to 1.0
    sentiment_score: float    # -1.0 to 1.0
    confidence: float         # 0.0 to 1.0
    triggers: List[str]       # What caused this emotional state

@dataclass
class DecisionPoint:
    """Identified decision point in conversation"""
    id: str
    decision_text: str
    importance_score: float
    participants: List[str]
    consensus_level: ConsensusLevel
    timestamp: float
    context_summary: str
    supporting_evidence: List[str]

@dataclass
class SpeakerProfile:
    """Complete speaker analysis profile"""
    name: str
    role: str
    emotional_peaks: List[Tuple[float, EmotionalState]]  # timestamp, emotion
    emotional_lows: List[Tuple[float, EmotionalState]]
    total_statements: int
    dominant_emotion: EmotionalState
    engagement_score: float
    speaking_time_percentage: float
    conversation_contribution: float

class ConversationAnalyzer:
    """Advanced conversation analysis engine"""
    
    def __init__(self):
        self.emotion_lexicon = self._load_emotion_lexicon()
        self.decision_indicators = self._load_decision_indicators()
        self.agreement_patterns = self._load_agreement_patterns()
        
    def _load_emotion_lexicon(self) -> Dict[str, List[str]]:
        """Load emotion detection lexicon"""
        return {
            "very_positive": [
                "excellent", "fantastic", "amazing", "wonderful", "outstanding",
                "incredible", "brilliant", "perfect", "superb", "phenomenal"
            ],
            "positive": [
                "good", "great", "nice", "pleased", "happy", "satisfied",
                "optimistic", "confident", "enthusiastic", "positive"
            ],
            "excited": [
                "excited", "thrilled", "pumped", "energetic", "enthusiastic",
                "eager", "animated", "passionate", "fired up"
            ],
            "frustrated": [
                "frustrated", "annoyed", "irritated", "upset", "angry",
                "mad", "furious", "pissed", "aggravated", "vexed"
            ],
            "confused": [
                "confused", "unclear", "puzzled", "baffled", "perplexed",
                "uncertain", "unsure", "questioning", "dubious"
            ],
            "engaged": [
                "engaged", "attentive", "focused", "involved", "participating",
                "contributing", "interacting", "responsive"
            ],
            "disengaged": [
                "disengaged", "distracted", "bored", "uninterested", "absent",
                "distant", "withdrawn", "quiet"
            ]
        }
    
    def _load_decision_indicators(self) -> Dict[str, List[str]]:
        """Load decision point detection indicators"""
        return {
            "approval": [
                "approved", "agreed", "accepted", "confirmed", "greenlit",
                "authorized", "endorsed", "supported", "okay", "good to go"
            ],
            "rejection": [
                "rejected", "declined", "denied", "refused", "dismissed",
                "turned down", "not approved", "disagreed"
            ],
            "action_item": [
                "action item", "follow up", "next steps", "assign", "task",
                "responsibility", "deadline", "due date", "schedule"
            ],
            "consensus": [
                "consensus", "everyone agrees", "we're all on the same page",
                "unanimous", "all in favor", "majority agreement"
            ]
        }
    
    def _load_agreement_patterns(self) -> List[str]:
        """Load agreement and consensus patterns"""
        return [
            r"\b(yes|yeah|agree|absolutely|certainly|definitely)\b",
            r"\b(that's right|exactly|precisely|correct)\b",
            r"\b(i think so|me too|sounds good|that works)\b",
            r"\b(we (all )?agree|everyone agrees|unanimous)\b",
            r"\b(consensus|general agreement|majority)\b",
            r"\b(okay|fine|good|no problem)\b"
        ]
    
    def parse_transcript(self, content: str, filename: str) -> Tuple[List[SpeakerSegment], str]:
        """Parse meeting transcript into speaker segments"""
        
        # Try different transcript formats
        segments = []
        errors = []
        
        # Format 1: Speaker: Content
        pattern1 = r'^([^:]+):\s*(.+)$'
        matches1 = re.findall(pattern1, content, re.MULTILINE)
        
        if matches1:
            for timestamp, (speaker, content_part) in enumerate(matches1):
                segments.append(SpeakerSegment(
                    speaker=speaker.strip(),
                    content=content_part.strip(),
                    timestamp=timestamp
                ))
        else:
            # Format 2: [timestamp] Speaker: Content
            pattern2 = r'^\[([^\]]+)\]\s*([^:]+):\s*(.+)$'
            matches2 = re.findall(pattern2, content, re.MULTILINE)
            
            if matches2:
                for timestamp, (time_str, speaker, content_part) in enumerate(matches2):
                    segments.append(SpeakerSegment(
                        speaker=speaker.strip(),
                        content=content_part.strip(),
                        timestamp=timestamp,
                        start_time=time_str.strip()
                    ))
            else:
                # Format 3: Name - Content (with dashes)
                pattern3 = r'^([^-]+)-\s*(.+)$'
                matches3 = re.findall(pattern3, content, re.MULTILINE)
                
                if matches3:
                    for timestamp, (speaker, content_part) in enumerate(matches3):
                        segments.append(SpeakerSegment(
                            speaker=speaker.strip(),
                            content=content_part.strip(),
                            timestamp=timestamp
                        ))
                else:
                    # Format 4: Generic numbered format
                    pattern4 = r'^\d+\.\s*([^:]+):\s*(.+)$'
                    matches4 = re.findall(pattern4, content, re.MULTILINE)
                    
                    if matches4:
                        for timestamp, (speaker, content_part) in enumerate(matches4):
                            segments.append(SpeakerSegment(
                                speaker=speaker.strip(),
                                content=content_part.strip(),
                                timestamp=timestamp
                            ))
                    else:
                        errors.append("Could not parse transcript format. Supported formats: 'Speaker: Content', '[Time] Speaker: Content', 'Name - Content'")
        
        return segments, '; '.join(errors)
    
    def analyze_emotional_states(self, segments: List[SpeakerSegment]) -> Dict[str, List[EmotionalAnalysis]]:
        """Analyze emotional states for each speaker"""
        speaker_emotions = {}
        
        for segment in segments:
            speaker = segment.speaker
            if speaker not in speaker_emotions:
                speaker_emotions[speaker] = []
            
            emotion_analysis = self._analyze_single_segment_emotion(segment)
            speaker_emotions[speaker].append(emotion_analysis)
        
        return speaker_emotions
    
    def _analyze_single_segment_emotion(self, segment: SpeakerSegment) -> EmotionalAnalysis:
        """Analyze emotion for a single speech segment"""
        
        content_lower = segment.content.lower()
        
        # Count emotion indicators
        emotion_scores = {}
        for emotion, indicators in self.emotion_lexicon.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Determine dominant emotion
        if emotion_scores:
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            emotion_state = EmotionalState(dominant_emotion[0])
            intensity = min(1.0, dominant_emotion[1] / 3.0)  # Normalize to max 1.0
        else:
            emotion_state = EmotionalState.NEUTRAL
            intensity = 0.0
        
        # Calculate sentiment score (-1.0 to 1.0)
        sentiment_score = self._calculate_sentiment_score(content_lower, emotion_scores)
        
        # Determine confidence based on emotion clarity
        confidence = 0.5 + (intensity * 0.5) if emotion_scores else 0.3
        
        # Identify emotion triggers
        triggers = self._identify_emotion_triggers(segment.content, emotion_state)
        
        return EmotionalAnalysis(
            speaker=segment.speaker,
            current_emotion=emotion_state,
            emotion_intensity=intensity,
            sentiment_score=sentiment_score,
            confidence=confidence,
            triggers=triggers
        )
    
    def _calculate_sentiment_score(self, content: str, emotion_scores: Dict[str, int]) -> float:
        """Calculate overall sentiment score"""
        positive_emotions = {"very_positive", "positive", "excited", "engaged"}
        negative_emotions = {"very_negative", "negative", "frustrated", "disengaged"}
        
        positive_score = sum(emotion_scores.get(emotion, 0) for emotion in positive_emotions)
        negative_score = sum(emotion_scores.get(emotion, 0) for emotion in negative_emotions)
        
        total_emotion_words = positive_score + negative_score
        
        if total_emotion_words == 0:
            return 0.0  # Neutral
        
        # Calculate sentiment (-1.0 to 1.0)
        sentiment = (positive_score - negative_score) / max(total_emotion_words, 1)
        return max(-1.0, min(1.0, sentiment))
    
    def _identify_emotion_triggers(self, content: str, emotion: EmotionalState) -> List[str]:
        """Identify what triggered the emotional state"""
        triggers = []
        content_lower = content.lower()
        
        # Look for trigger phrases
        if emotion == EmotionalState.FRUSTRATED:
            trigger_phrases = ["not working", "failed", "problem", "issue", "error"]
            triggers.extend([phrase for phrase in trigger_phrases if phrase in content_lower])
        
        elif emotion == EmotionalState.EXCITED:
            trigger_phrases = ["great idea", "excellent", "love it", "fantastic"]
            triggers.extend([phrase for phrase in trigger_phrases if phrase in content_lower])
        
        elif emotion == EmotionalState.CONFUSED:
            trigger_phrases = ["don't understand", "unclear", "confusing", "what do you mean"]
            triggers.extend([phrase for phrase in trigger_phrases if phrase in content_lower])
        
        # Add question marks as confusion triggers
        if "?" in content:
            triggers.append("questioning")
        
        # Add exclamation marks as excitement triggers
        if "!" in content:
            triggers.append("emphasis")
        
        return triggers
    
    def identify_decision_points(self, segments: List[SpeakerSegment]) -> List[DecisionPoint]:
        """Identify decision points in the conversation"""
        decisions = []
        content = ' '.join(segment.content for segment in segments)
        content_lower = content.lower()
        
        # Sliding window analysis for decision detection
        window_size = 3  # Analyze in groups of 3 segments
        for i in range(len(segments) - window_size + 1):
            window_segments = segments[i:i + window_size]
            window_content = ' '.join(seg.content for seg in window_segments)
            
            decision_analysis = self._analyze_decision_window(window_segments, window_content)
            if decision_analysis:
                decision = DecisionPoint(
                    id=str(uuid.uuid4()),
                    decision_text=decision_analysis["text"],
                    importance_score=decision_analysis["importance"],
                    participants=decision_analysis["participants"],
                    consensus_level=decision_analysis["consensus"],
                    timestamp=segments[i].timestamp,
                    context_summary=decision_analysis["context"],
                    supporting_evidence=decision_analysis["evidence"]
                )
                decisions.append(decision)
        
        # Rank decisions by importance and return top 3
        decisions.sort(key=lambda x: x.importance_score, reverse=True)
        return decisions[:3]
    
    def _analyze_decision_window(self, segments: List[SpeakerSegment], content: str) -> Optional[Dict]:
        """Analyze a window of segments for decision indicators"""
        
        content_lower = content.lower()
        participants = list(set(segment.speaker for segment in segments))
        
        # Check for decision indicators
        decision_type = None
        confidence = 0.0
        evidence = []
        
        for decision_type_key, indicators in self.decision_indicators.items():
            for indicator in indicators:
                if indicator in content_lower:
                    decision_type = decision_type_key
                    confidence += 0.3
                    evidence.append(f"Found '{indicator}'")
        
        # Check for consensus patterns
        consensus_level = ConsensusLevel.NO_CONSENSUS
        for pattern in self.agreement_patterns:
            if re.search(pattern, content_lower):
                consensus_level = ConsensusLevel.STRONG_CONSENSUS
                confidence += 0.2
                evidence.append("Consensus indicators found")
                break
        
        # Calculate importance score
        importance_indicators = [
            "critical", "important", "urgent", "priority", "key decision",
            "must", "required", "essential", "major", "significant"
        ]
        
        importance_score = 0.5  # Base score
        for indicator in importance_indicators:
            if indicator in content_lower:
                importance_score += 0.1
                evidence.append(f"Importance indicator: '{indicator}'")
        
        importance_score = min(1.0, importance_score)
        
        # Only return if we have sufficient confidence
        if confidence >= 0.5 and decision_type:
            # Extract decision text (first sentence or key phrase)
            sentences = re.split(r'[.!?]+', content)
            decision_text = sentences[0].strip() if sentences else content[:100]
            
            return {
                "text": decision_text,
                "importance": importance_score,
                "participants": participants,
                "consensus": consensus_level,
                "context": f"Decision regarding: {decision_type}",
                "evidence": evidence
            }
        
        return None
    
    def generate_speaker_profiles(self, segments: List[SpeakerSegment], 
                                emotions: Dict[str, List[EmotionalAnalysis]]) -> Dict[str, SpeakerProfile]:
        """Generate comprehensive speaker profiles"""
        profiles = {}
        
        # Group segments by speaker
        speaker_segments = {}
        for segment in segments:
            if segment.speaker not in speaker_segments:
                speaker_segments[segment.speaker] = []
            speaker_segments[segment.speaker].append(segment)
        
        # Calculate total speaking time
        total_segments = len(segments)
        
        for speaker, speaker_segs in speaker_segments.items():
            speaker_emotions = emotions.get(speaker, [])
            
            # Identify emotional peaks and lows
            peaks = []
            lows = []
            
            for i, analysis in enumerate(speaker_emotions):
                if analysis.emotion_intensity > 0.7:
                    peaks.append((segments[i].timestamp, analysis.current_emotion))
                elif analysis.emotion_intensity < 0.3 and analysis.sentiment_score < -0.3:
                    lows.append((segments[i].timestamp, analysis.current_emotion))
            
            # Determine dominant emotion
            emotion_counts = {}
            for analysis in speaker_emotions:
                emotion = analysis.current_emotion.value
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            dominant_emotion = EmotionalState.NEUTRAL
            if emotion_counts:
                dominant_emotion_name = max(emotion_counts.items(), key=lambda x: x[1])[0]
                dominant_emotion = EmotionalState(dominant_emotion_name)
            
            # Calculate engagement score
            total_statements = len(speaker_segs)
            speaking_time_percentage = (total_statements / total_segments) * 100
            
            # Engagement based on emotional variability and participation
            engagement_score = self._calculate_engagement_score(speaker_emotions, total_statements)
            
            # Conversation contribution (considering both quantity and quality)
            contribution_score = self._calculate_conversation_contribution(speaker_segs, speaker_emotions)
            
            profiles[speaker] = SpeakerProfile(
                name=speaker,
                role="participant",  # Could be enhanced with role detection
                emotional_peaks=peaks,
                emotional_lows=lows,
                total_statements=total_statements,
                dominant_emotion=dominant_emotion,
                engagement_score=engagement_score,
                speaking_time_percentage=speaking_time_percentage,
                conversation_contribution=contribution_score
            )
        
        return profiles
    
    def _calculate_engagement_score(self, emotions: List[EmotionalAnalysis], total_statements: int) -> float:
        """Calculate speaker engagement score"""
        if not emotions:
            return 0.0
        
        # Factors for engagement:
        # 1. Emotional variability (more variation = more engaged)
        emotion_variability = len(set(emotion.current_emotion for emotion in emotions)) / len(emotions)
        
        # 2. Emotional intensity average
        avg_intensity = sum(emotion.emotion_intensity for emotion in emotions) / len(emotions)
        
        # 3. Statement frequency relative to conversation length
        participation_rate = min(1.0, total_statements / 10.0)  # Normalize to max 10 statements
        
        # Weighted engagement score
        engagement = (emotion_variability * 0.4 + avg_intensity * 0.4 + participation_rate * 0.2)
        return min(1.0, engagement)
    
    def _calculate_conversation_contribution(self, segments: List[SpeakerSegment], 
                                           emotions: List[EmotionalAnalysis]) -> float:
        """Calculate overall conversation contribution score"""
        if not segments or not emotions:
            return 0.0
        
        # Factors:
        # 1. Statement length (longer statements indicate more contribution)
        avg_length = sum(len(seg.content.split()) for seg in segments) / len(segments)
        length_score = min(1.0, avg_length / 20.0)  # Normalize to 20 words
        
        # 2. Emotional engagement
        emotional_engagement = sum(emotion.emotion_intensity for emotion in emotions) / len(emotions)
        
        # 3. Initiative (questions, suggestions, proposals)
        initiative_indicators = ["i suggest", "i propose", "what if", "how about", "let's"]
        content_combined = ' '.join(seg.content.lower() for seg in segments)
        initiative_score = sum(1 for indicator in initiative_indicators if indicator in content_combined)
        initiative_score = min(1.0, initiative_score / 3.0)  # Normalize to max 3 initiatives
        
        # Weighted contribution score
        contribution = (length_score * 0.3 + emotional_engagement * 0.4 + initiative_score * 0.3)
        return min(1.0, contribution)

class DecisionTreeGenerator:
    """Generate decision tree visualization data"""
    
    def generate_decision_tree(self, segments: List[SpeakerSegment], 
                             decisions: List[DecisionPoint], 
                             emotions: Dict[str, List[EmotionalAnalysis]]) -> Dict:
        """Generate decision tree structure for visualization"""
        
        # Create tree structure
        tree = {
            "type": "conversation_flow",
            "title": "Conversation Decision Tree",
            "nodes": [],
            "edges": []
        }
        
        node_id = 0
        
        # Add decision nodes
        for decision in decisions:
            decision_node = {
                "id": f"decision_{node_id}",
                "type": "decision",
                "label": f"Decision: {decision.decision_text[:50]}...",
                "participants": decision.participants,
                "importance": decision.importance_score,
                "consensus": decision.consensus_level.value,
                "timestamp": decision.timestamp,
                "position": {"x": node_id * 200, "y": 100}
            }
            
            tree["nodes"].append(decision_node)
            
            # Add emotional context for this decision
            decision_emotions = self._get_emotions_for_timestamp(emotions, decision.timestamp)
            if decision_emotions:
                emotional_node = {
                    "id": f"emotion_{node_id}",
                    "type": "emotion",
                    "label": f"Emotional context: {decision_emotions}",
                    "position": {"x": node_id * 200, "y": 200}
                }
                tree["nodes"].append(emotional_node)
                
                # Connect decision to emotion
                tree["edges"].append({
                    "from": f"decision_{node_id}",
                    "to": f"emotion_{node_id}",
                    "type": "emotional_context"
                })
            
            node_id += 1
        
        # Add speaker interaction nodes
        speakers = list(set(segment.speaker for segment in segments))
        for speaker in speakers:
            speaker_node = {
                "id": f"speaker_{speaker}",
                "type": "speaker",
                "label": speaker,
                "position": {"x": 50, "y": 50 + len(tree["nodes"]) * 150}
            }
            tree["nodes"].append(speaker_node)
        
        # Add conversation flow edges
        for i in range(len(decisions) - 1):
            tree["edges"].append({
                "from": f"decision_{i}",
                "to": f"decision_{i+1}",
                "type": "sequence"
            })
        
        return tree
    
    def _get_emotions_for_timestamp(self, emotions: Dict[str, List[EmotionalAnalysis]], 
                                  timestamp: float) -> str:
        """Get emotional context around a specific timestamp"""
        all_emotions = []
        for speaker_emotions in emotions.values():
            for analysis in speaker_emotions:
                # Find emotions within a reasonable time window
                if abs(analysis.confidence - timestamp) < 2.0:  # Within 2 units
                    all_emotions.append(f"{analysis.speaker}: {analysis.current_emotion.value}")
        
        return "; ".join(all_emotions) if all_emotions else "neutral"

class LiveConversationAnalyzer:
    """Main conversation analysis orchestrator"""
    
    def __init__(self):
        self.analyzer = ConversationAnalyzer()
        self.tree_generator = DecisionTreeGenerator()
        
    def analyze_conversation(self, file_content: bytes, filename: str) -> Dict:
        """Analyze meeting transcript for emotional states and decision points"""
        
        # Parse file encoding
        detected_encoding = chardet.detect(file_content)['encoding'] or 'utf-8'
        
        try:
            content = file_content.decode(detected_encoding)
        except UnicodeDecodeError:
            content = file_content.decode('latin-1', errors='ignore')
        
        # Parse transcript
        segments, parse_errors = self.analyzer.parse_transcript(content, filename)
        
        if not segments:
            return {
                "status": "error",
                "error": "No valid conversation segments found",
                "parse_errors": parse_errors,
                "total_segments": 0,
                "speakers": [],
                "emotional_analysis": {},
                "decision_points": [],
                "decision_tree": {}
            }
        
        # Analyze emotional states
        emotions = self.analyzer.analyze_emotional_states(segments)
        
        # Identify decision points
        decisions = self.analyzer.identify_decision_points(segments)
        
        # Generate speaker profiles
        profiles = self.analyzer.generate_speaker_profiles(segments, emotions)
        
        # Generate decision tree
        decision_tree = self.tree_generator.generate_decision_tree(segments, decisions, emotions)
        
        # Store analysis in database
        session_id = self._store_analysis_session(filename, segments, emotions, decisions)
        
        # Compile results
        results = {
            "session_id": session_id,
            "status": "completed",
            "filename": filename,
            "total_segments": len(segments),
            "speakers": list(set(segment.speaker for segment in segments)),
            "parse_errors": parse_errors,
            "emotional_analysis": self._compile_emotional_analysis(emotions, profiles),
            "decision_points": [asdict(decision) for decision in decisions],
            "decision_tree": decision_tree,
            "speaker_profiles": {name: asdict(profile) for name, profile in profiles.items()},
            "conversation_summary": self._generate_conversation_summary(segments, emotions, decisions, profiles),
            "recommendations": self._generate_recommendations(decisions, profiles)
        }
        
        return results
    
    def _compile_emotional_analysis(self, emotions: Dict[str, List[EmotionalAnalysis]], 
                                  profiles: Dict[str, SpeakerProfile]) -> Dict:
        """Compile emotional analysis results"""
        compiled = {}
        
        for speaker, emotion_list in emotions.items():
            profile = profiles.get(speaker)
            
            # Aggregate emotional data
            emotional_states = [analysis.current_emotion.value for analysis in emotion_list]
            avg_sentiment = sum(analysis.sentiment_score for analysis in emotion_list) / len(emotion_list)
            avg_intensity = sum(analysis.emotion_intensity for analysis in emotion_list) / len(emotion_list)
            
            # Identify peaks and lows
            peaks = []
            lows = []
            for i, analysis in enumerate(emotion_list):
                if analysis.emotion_intensity > 0.7:
                    peaks.append({
                        "timestamp": i,
                        "emotion": analysis.current_emotion.value,
                        "intensity": analysis.emotion_intensity
                    })
                elif analysis.emotion_intensity < 0.3 and analysis.sentiment_score < -0.3:
                    lows.append({
                        "timestamp": i,
                        "emotion": analysis.current_emotion.value,
                        "intensity": analysis.emotion_intensity
                    })
            
            compiled[speaker] = {
                "dominant_emotion": profile.dominant_emotion.value if profile else "neutral",
                "average_sentiment": avg_sentiment,
                "average_intensity": avg_intensity,
                "emotional_peaks": peaks,
                "emotional_lows": lows,
                "engagement_score": profile.engagement_score if profile else 0.0,
                "speaking_time_percentage": profile.speaking_time_percentage if profile else 0.0,
                "total_statements": len(emotion_list)
            }
        
        return compiled
    
    def _generate_conversation_summary(self, segments: List[SpeakerSegment], 
                                     emotions: Dict[str, List[EmotionalAnalysis]],
                                     decisions: List[DecisionPoint],
                                     profiles: Dict[str, SpeakerProfile]) -> Dict:
        """Generate conversation summary"""
        
        # Overall statistics
        total_speakers = len(profiles)
        total_segments = len(segments)
        
        # Speaker activity summary
        speaker_activity = {}
        for speaker, profile in profiles.items():
            speaker_activity[speaker] = {
                "statements": profile.total_statements,
                "speaking_time": profile.speaking_time_percentage,
                "engagement": profile.engagement_score,
                "contribution": profile.conversation_contribution
            }
        
        # Decision summary
        decision_summary = {
            "total_decisions": len(decisions),
            "high_importance": len([d for d in decisions if d.importance_score > 0.8]),
            "consensus_decisions": len([d for d in decisions if d.consensus_level in [ConsensusLevel.UNANIMOUS, ConsensusLevel.STRONG_CONSENSUS]]),
            "participants": list(set(participant for decision in decisions for participant in decision.participants))
        }
        
        # Emotional climate
        all_emotions = []
        for emotion_list in emotions.values():
            all_emotions.extend([analysis.current_emotion for analysis in emotion_list])
        
        emotion_counts = {}
        for emotion in all_emotions:
            emotion_counts[emotion.value] = emotion_counts.get(emotion.value, 0) + 1
        
        dominant_conversation_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "neutral"
        
        return {
            "total_speakers": total_speakers,
            "total_segments": total_segments,
            "average_statements_per_speaker": total_segments / total_speakers if total_speakers > 0 else 0,
            "speaker_activity": speaker_activity,
            "decision_summary": decision_summary,
            "emotional_climate": {
                "dominant_emotion": dominant_conversation_emotion,
                "emotion_distribution": emotion_counts
            },
            "conversation_flow": "structured" if decisions else "informal"
        }
    
    def _generate_recommendations(self, decisions: List[DecisionPoint], 
                                profiles: Dict[str, SpeakerProfile]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Participation balance recommendations
        speaking_times = [profile.speaking_time_percentage for profile in profiles.values()]
        if speaking_times:
            max_speaking_time = max(speaking_times)
            min_speaking_time = min(speaking_times)
            
            if max_speaking_time - min_speaking_time > 30:  # More than 30% difference
                recommendations.append("Consider encouraging more balanced participation among speakers")
        
        # Engagement recommendations
        low_engagement_speakers = [speaker for speaker, profile in profiles.items() 
                                 if profile.engagement_score < 0.4]
        
        if low_engagement_speakers:
            recommendations.append(f"Monitor engagement of: {', '.join(low_engagement_speakers)}")
        
        # Decision-making recommendations
        low_consensus_decisions = [d for d in decisions if d.consensus_level in [ConsensusLevel.NO_CONSENSUS, ConsensusLevel.MINORITY_SUPPORT]]
        
        if low_consensus_decisions:
            recommendations.append("Follow up on decisions with low consensus to ensure alignment")
        
        # Action items recommendations
        action_decisions = [d for d in decisions if d.consensus_level == ConsensusLevel.ACTION_ITEM]
        
        if action_decisions:
            recommendations.append("Assign clear ownership and deadlines for action items identified")
        
        return recommendations
    
    def _store_analysis_session(self, filename: str, segments: List[SpeakerSegment], 
                              emotions: Dict[str, List[EmotionalAnalysis]], 
                              decisions: List[DecisionPoint]) -> str:
        """Store analysis session in database"""
        session_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Store session
        cursor.execute('''
            INSERT INTO conversation_sessions (
                id, filename, total_speakers, total_segments, duration_minutes,
                analysis_status, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            filename,
            len(set(segment.speaker for segment in segments)),
            len(segments),
            len(segments) * 2,  # Estimated 2 minutes per segment
            "completed",
            json.dumps({
                "analysis_date": datetime.now().isoformat(),
                "emotional_analysis": True,
                "decision_detection": True,
                "speaker_profiling": True
            })
        ))
        
        # Store speaker analysis
        for speaker, emotion_list in emotions.items():
            peaks_count = len([e for e in emotion_list if e.emotion_intensity > 0.7])
            lows_count = len([e for e in emotion_list if e.emotion_intensity < 0.3 and e.sentiment_score < -0.3])
            
            cursor.execute('''
                INSERT INTO speaker_analysis (
                    id, session_id, speaker_name, emotional_peaks, emotional_lows,
                    total_statements, engagement_score, speaking_time_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                session_id,
                speaker,
                peaks_count,
                lows_count,
                len(emotion_list),
                sum(e.emotion_intensity for e in emotion_list) / len(emotion_list) if emotion_list else 0.0,
                (len(emotion_list) / len(segments)) * 100 if segments else 0.0
            ))
        
        # Store decision points
        for decision in decisions:
            cursor.execute('''
                INSERT INTO decision_points (
                    id, session_id, decision_text, importance_score, participants,
                    consensus_level, time_stamp, context_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision.id,
                session_id,
                decision.decision_text,
                decision.importance_score,
                json.dumps(decision.participants),
                decision.consensus_level.value,
                str(decision.timestamp),
                decision.context_summary
            ))
        
        conn.commit()
        conn.close()
        
        return session_id

# Initialize conversation analyzer
analyzer = LiveConversationAnalyzer()

# API Models
class AnalysisResponse(BaseModel):
    session_id: str
    status: str
    filename: str
    total_segments: int
    speakers: List[str]
    parse_errors: str
    emotional_analysis: Dict
    decision_points: List[Dict]
    decision_tree: Dict
    speaker_profiles: Dict
    conversation_summary: Dict
    recommendations: List[str]

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Live Conversation Analyst API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "analyze_conversation": "/api/v1/analyze-conversation",
            "get_session": "/api/v1/session/{session_id}",
            "speaker_analysis": "/api/v1/speaker-analysis",
            "decision_points": "/api/v1/decision-points",
            "conversation_insights": "/api/v1/conversation-insights",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "conversation_analyzer": "active",
            "emotion_detector": "ready",
            "decision_detector": "operational",
            "tree_generator": "available"
        },
        "capabilities": [
            "emotional_state_analysis",
            "decision_point_detection",
            "speaker_profiling",
            "conversation_flow_visualization",
            "multi_format_transcript_support"
        ],
        "supported_formats": [
            "Speaker: Content",
            "[Time] Speaker: Content", 
            "Name - Content",
            "Numbered segments"
        ]
    }

@app.post("/api/v1/analyze-conversation", response_model=AnalysisResponse)
async def analyze_conversation(
    transcript_file: UploadFile = File(..., description="Meeting transcript file to analyze"),
    analysis_type: Optional[str] = Form("comprehensive", description="Type of analysis to perform")
):
    """
    Analyze meeting transcript for emotional states and decision points
    
    - **transcript_file**: Meeting transcript file (.txt, .csv, .json)
    - **analysis_type**: Type of analysis (comprehensive, emotional_only, decisions_only)
    
    **Analysis Features:**
    - Emotional peak/low detection for each speaker
    - Top 3 decision points identification
    - Decision tree generation for conversational flow
    - Speaker engagement and contribution analysis
    """
    
    try:
        # Validate file
        if not transcript_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (limit to 5MB)
        content = await transcript_file.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(status_code=413, detail="File too large (max 5MB)")
        
        # Validate file type
        allowed_extensions = ['.txt', '.csv', '.json']
        if not any(transcript_file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Analyze the transcript
        results = analyzer.analyze_conversation(content, transcript_file.filename)
        
        return JSONResponse(content=results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/session/{session_id}")
async def get_analysis_session(session_id: str):
    """Get previously completed analysis session"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT filename, total_speakers, total_segments, duration_minutes,
                   analysis_status, started_at, completed_at, metadata
            FROM conversation_sessions WHERE id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Analysis session not found")
        
        (
            filename, total_speakers, total_segments, duration_minutes,
            analysis_status, started_at, completed_at, metadata_json
        ) = result
        
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        # Get speaker analysis
        cursor.execute('''
            SELECT speaker_name, speaker_role, emotional_peaks, emotional_lows,
                   total_statements, engagement_score, speaking_time_percentage
            FROM speaker_analysis WHERE session_id = ?
        ''', (session_id,))
        
        speakers = []
        for row in cursor.fetchall():
            speakers.append({
                "name": row[0],
                "role": row[1],
                "emotional_peaks": row[2],
                "emotional_lows": row[3],
                "total_statements": row[4],
                "engagement_score": row[5],
                "speaking_time_percentage": row[6]
            })
        
        # Get decision points
        cursor.execute('''
            SELECT decision_text, importance_score, participants, consensus_level,
                   time_stamp, context_summary
            FROM decision_points WHERE session_id = ?
            ORDER BY importance_score DESC
        ''', (session_id,))
        
        decisions = []
        for row in cursor.fetchall():
            decisions.append({
                "decision_text": row[0],
                "importance_score": row[1],
                "participants": json.loads(row[2]),
                "consensus_level": row[3],
                "timestamp": row[4],
                "context_summary": row[5]
            })
        
        conn.close()
        
        return {
            "session_id": session_id,
            "filename": filename,
            "total_speakers": total_speakers,
            "total_segments": total_segments,
            "duration_minutes": duration_minutes,
            "analysis_status": analysis_status,
            "started_at": started_at,
            "completed_at": completed_at,
            "speakers": speakers,
            "decision_points": decisions,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

@app.get("/api/v1/speaker-analysis")
async def list_speaker_analysis(limit: int = 50):
    """List speaker analysis results"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sa.speaker_name, sa.speaker_role, sa.emotional_peaks, sa.emotional_lows,
                   sa.total_statements, sa.engagement_score, sa.speaking_time_percentage,
                   cs.filename, cs.created_at
            FROM speaker_analysis sa
            JOIN conversation_sessions cs ON sa.session_id = cs.id
            ORDER BY sa.engagement_score DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "speaker_name": row[0],
                "speaker_role": row[1],
                "emotional_peaks": row[2],
                "emotional_lows": row[3],
                "total_statements": row[4],
                "engagement_score": row[5],
                "speaking_time_percentage": row[6],
                "source_file": row[7],
                "analyzed_at": row[8]
            })
        
        conn.close()
        
        return {
            "speaker_analysis": results,
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list speaker analysis: {str(e)}")

@app.get("/api/v1/decision-points")
async def list_decision_points(limit: int = 50, min_importance: float = 0.0):
    """List decision points across all sessions"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT dp.decision_text, dp.importance_score, dp.participants, dp.consensus_level,
                   dp.time_stamp, dp.context_summary, cs.filename, cs.created_at
            FROM decision_points dp
            JOIN conversation_sessions cs ON dp.session_id = cs.id
            WHERE dp.importance_score >= ?
            ORDER BY dp.importance_score DESC
            LIMIT ?
        ''', (min_importance, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "decision_text": row[0],
                "importance_score": row[1],
                "participants": json.loads(row[2]),
                "consensus_level": row[3],
                "timestamp": row[4],
                "context_summary": row[5],
                "source_file": row[6],
                "analyzed_at": row[7]
            })
        
        conn.close()
        
        return {
            "decision_points": results,
            "total": len(results),
            "filters_applied": {"min_importance": min_importance}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list decision points: {str(e)}")

@app.get("/api/v1/conversation-insights")
async def get_conversation_insights():
    """Get conversation analysis insights and statistics"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute('SELECT COUNT(*) FROM conversation_sessions')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM speaker_analysis')
        total_speakers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM decision_points')
        total_decisions = cursor.fetchone()[0]
        
        # Average engagement
        cursor.execute('SELECT AVG(engagement_score) FROM speaker_analysis')
        avg_engagement = cursor.fetchone()[0] or 0.0
        
        # High engagement speakers
        cursor.execute('''
            SELECT speaker_name, engagement_score, total_statements
            FROM speaker_analysis 
            WHERE engagement_score > 0.7
            ORDER BY engagement_score DESC
            LIMIT 10
        ''')
        high_engagement_speakers = [
            {"name": row[0], "engagement_score": row[1], "statements": row[2]}
            for row in cursor.fetchall()
        ]
        
        # Important decisions
        cursor.execute('''
            SELECT decision_text, importance_score, consensus_level
            FROM decision_points 
            WHERE importance_score > 0.8
            ORDER BY importance_score DESC
            LIMIT 10
        ''')
        important_decisions = [
            {"text": row[0], "importance": row[1], "consensus": row[2]}
            for row in cursor.fetchall()
        ]
        
        # Speaker activity distribution
        cursor.execute('''
            SELECT speaker_name, speaking_time_percentage
            FROM speaker_analysis
            ORDER BY speaking_time_percentage DESC
        ''')
        activity_distribution = [
            {"speaker": row[0], "speaking_percentage": row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "overview": {
                "total_sessions": total_sessions,
                "total_speakers_analyzed": total_speakers,
                "total_decisions_identified": total_decisions,
                "average_engagement_score": round(avg_engagement, 2)
            },
            "high_engagement_speakers": high_engagement_speakers,
            "important_decisions": important_decisions,
            "activity_distribution": activity_distribution,
            "insights": [
                f"Analyzed {total_sessions} conversation sessions",
                f"Identified {total_decisions} decision points across all meetings",
                f"Average speaker engagement: {round(avg_engagement * 100, 1)}%",
                "Most engaged speakers tend to drive decision-making"
            ],
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation insights: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)