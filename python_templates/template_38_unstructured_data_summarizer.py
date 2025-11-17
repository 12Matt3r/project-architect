#!/usr/bin/env python3
"""
Template #38: Unstructured Data Summarizer

An intelligent text analysis system that processes customer support tickets to identify
hidden root causes and recurring problems not explicitly stated in the tickets.

Implements advanced NLP techniques for pattern recognition and root cause analysis.

Author: MiniMax Agent
Date: 2025-11-17
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import json
import uuid
import sqlite3
import logging
from contextlib import contextmanager
from collections import Counter, defaultdict
import math
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class TicketData(BaseModel):
    ticket_id: str
    content: str
    timestamp: Optional[str] = None
    customer_id: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None

class RootCauseAnalysis(BaseModel):
    analysis_id: str
    total_tickets: int
    root_cause_statement: str
    confidence_score: float
    supporting_evidence: List[str]
    pattern_analysis: Dict[str, Any]
    topic_frequency: Dict[str, int]
    sentiment_analysis: Dict[str, Any]
    keywords_identified: List[str]
    processing_metadata: Dict[str, Any]
    created_at: datetime

class TicketUploadRequest(BaseModel):
    batch_id: Optional[str] = Field(None, description="Optional batch identifier for grouping")
    analysis_notes: Optional[str] = Field(None, description="Additional notes for the analysis")

class AnalysisResponse(BaseModel):
    success: bool
    root_cause: RootCauseAnalysis
    summary: Dict[str, Any]
    recommendations: List[str]
    processing_time: float

# Dataclasses for internal processing
@dataclass
class ProcessedTicket:
    original_ticket: TicketData
    cleaned_text: str
    tokens: List[str]
    topics: List[str]
    sentiment_score: float
    keywords: List[str]
    entities: List[str]
    urgency_indicators: List[str]

@dataclass
class PatternAnalysis:
    topic_frequencies: Dict[str, int]
    keyword_cooccurrence: Dict[str, Dict[str, int]]
    sentiment_trends: List[float]
    entity_mentions: Dict[str, List[str]]
    urgency_patterns: List[str]
    temporal_patterns: Dict[str, int]

@dataclass
class RootCauseCandidate:
    cause: str
    confidence: float
    evidence_count: int
    supporting_quotes: List[str]
    frequency_score: float
    coherence_score: float

class TextPreprocessor:
    """Advanced text preprocessing for customer support tickets"""
    
    def __init__(self):
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 
            'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 
            'will', 'with', 'the', 'this', 'but', 'they', 'have', 'had', 'what', 'said',
            'each', 'which', 'she', 'do', 'how', 'their', 'if', 'up', 'out', 'many',
            'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like',
            'into', 'him', 'time', 'two', 'more', 'go', 'no', 'way', 'could', 'my',
            'than', 'first', 'been', 'call', 'who', 'oil', 'its', 'now', 'find',
            'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'
        }
        
        # Customer service specific patterns
        self.urgency_patterns = {
            'critical': ['urgent', 'emergency', 'immediately', 'critical', 'crisis', 'asap'],
            'high': ['important', 'priority', 'serious', 'major', 'significant'],
            'medium': ['issue', 'problem', 'concern', 'question', 'help'],
            'low': ['suggestion', 'feedback', 'minor', 'small']
        }
        
        self.problem_indicators = [
            'broken', 'error', 'fail', 'issue', 'problem', 'bug', 'crash', 'not working',
            'slow', 'freeze', 'hang', 'stuck', 'cant', 'cannot', 'unable', 'refuse',
            'denied', 'declined', 'rejected', 'wrong', 'incorrect', 'missing', 'lost',
            'delayed', 'late', 'overdue', 'expired', 'invalid', 'corrupt', 'damaged'
        ]
        
        self.feature_mentions = [
            'login', 'payment', 'checkout', 'delivery', 'shipping', 'account', 'password',
            'email', 'notification', 'mobile', 'app', 'website', 'interface', 'dashboard',
            'report', 'analytics', 'data', 'integration', 'api', 'security', 'privacy'
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Convert to lowercase
        text = text.lower().strip()
        
        return text
    
    def extract_tokens(self, text: str) -> List[str]:
        """Extract meaningful tokens from text"""
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stopwords and very short words
        tokens = [token for token in tokens if token not in self.stopwords and len(token) > 2]
        
        return tokens
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract domain-specific keywords"""
        tokens = self.extract_tokens(text)
        
        # Combine problem indicators and feature mentions
        relevant_patterns = self.problem_indicators + self.feature_mentions
        
        keywords = []
        for token in tokens:
            # Direct matches
            if token in relevant_patterns:
                keywords.append(token)
            
            # Partial matches for problem indicators
            for pattern in self.problem_indicators:
                if pattern in token or token in pattern:
                    keywords.append(pattern)
                    break
        
        return list(set(keywords))
    
    def identify_urgency(self, text: str) -> List[str]:
        """Identify urgency indicators in text"""
        text_lower = text.lower()
        urgency_indicators = []
        
        for urgency_level, patterns in self.urgency_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    urgency_indicators.append(f"{urgency_level}:{pattern}")
        
        return urgency_indicators
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract potential entities (product names, error codes, etc.)"""
        entities = []
        
        # Extract potential error codes
        error_codes = re.findall(r'\b[A-Z]{2,3}-\d{3,4}\b', text)
        entities.extend(error_codes)
        
        # Extract potential product names (capitalized words)
        product_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend(product_names[:5])  # Limit to first 5
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        entities.extend(emails)
        
        return entities
    
    def preprocess_ticket(self, ticket: TicketData) -> ProcessedTicket:
        """Complete preprocessing of a customer support ticket"""
        cleaned_text = self.clean_text(ticket.content)
        tokens = self.extract_tokens(cleaned_text)
        keywords = self.extract_keywords(cleaned_text)
        urgency_indicators = self.identify_urgency(cleaned_text)
        entities = self.extract_entities(cleaned_text)
        
        # Simple sentiment analysis (can be enhanced)
        sentiment_score = self._calculate_sentiment(cleaned_text)
        
        # Topic identification (simplified)
        topics = self._identify_topics(cleaned_text, keywords)
        
        return ProcessedTicket(
            original_ticket=ticket,
            cleaned_text=cleaned_text,
            tokens=tokens,
            topics=topics,
            sentiment_score=sentiment_score,
            keywords=keywords,
            entities=entities,
            urgency_indicators=urgency_indicators
        )
    
    def _calculate_sentiment(self, text: str) -> float:
        """Simple sentiment analysis using keyword counting"""
        positive_words = {'good', 'great', 'excellent', 'satisfied', 'happy', 'love', 'perfect', 'amazing'}
        negative_words = {'bad', 'terrible', 'awful', 'angry', 'hate', 'worst', 'horrible', 'frustrated', 'annoyed'}
        
        tokens = set(self.extract_tokens(text))
        
        positive_count = len(tokens.intersection(positive_words))
        negative_count = len(tokens.intersection(negative_words))
        
        if positive_count + negative_count == 0:
            return 0.0  # Neutral
        
        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return max(-1.0, min(1.0, sentiment))
    
    def _identify_topics(self, text: str, keywords: List[str]) -> List[str]:
        """Identify main topics in the text"""
        topics = []
        
        # Map keywords to topics
        topic_mapping = {
            'login': ['authentication', 'login', 'password'],
            'payment': ['payment', 'billing', 'checkout', 'transaction'],
            'delivery': ['shipping', 'delivery', 'order', 'tracking'],
            'technical': ['error', 'bug', 'crash', 'performance', 'slow'],
            'account': ['account', 'profile', 'settings', 'personal'],
            'data': ['data', 'report', 'analytics', 'export', 'import']
        }
        
        text_lower = text.lower()
        for topic, topic_keywords in topic_mapping.items():
            if any(keyword in text_lower for keyword in topic_keywords):
                topics.append(topic)
        
        return topics

class PatternAnalyzer:
    """Analyze patterns in customer support tickets to identify root causes"""
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        
        # Common root cause patterns in customer support
        self.root_cause_patterns = {
            'system_issues': {
                'keywords': ['server', 'system', 'database', 'backend', 'infrastructure', 'downtime'],
                'patterns': ['server error', 'database error', 'system crash', 'maintenance', 'outage']
            },
            'user_interface': {
                'keywords': ['interface', 'ui', 'ux', 'design', 'layout', 'navigation', 'button', 'menu'],
                'patterns': ['hard to find', 'confusing', 'not intuitive', 'missing button', 'broken link']
            },
            'process_workflow': {
                'keywords': ['process', 'workflow', 'step', 'procedure', 'instruction', 'guide'],
                'patterns': ['unclear process', 'missing step', 'complicated', 'too many steps', 'confusing flow']
            },
            'integration_problems': {
                'keywords': ['integration', 'api', 'third-party', 'external', 'sync', 'connection'],
                'patterns': ['integration error', 'api failure', 'connection timeout', 'sync failed']
            },
            'data_issues': {
                'keywords': ['data', 'information', 'record', 'file', 'document', 'report'],
                'patterns': ['missing data', 'incorrect data', 'data not showing', 'report error']
            },
            'communication': {
                'keywords': ['notification', 'alert', 'email', 'message', 'communication', 'alert'],
                'patterns': ['no notification', 'late alert', 'wrong message', 'missing email']
            },
            'performance': {
                'keywords': ['slow', 'performance', 'loading', 'timeout', 'delay', 'speed'],
                'patterns': ['loading slowly', 'timeout error', 'performance issue', 'takes too long']
            },
            'feature_functionality': {
                'keywords': ['feature', 'function', 'capability', 'option', 'tool', 'functionality'],
                'patterns': ['feature not working', 'missing feature', 'function broken', 'cant find option']
            }
        }
    
    def analyze_patterns(self, processed_tickets: List[ProcessedTicket]) -> PatternAnalysis:
        """Analyze patterns across all processed tickets"""
        
        # Topic frequency analysis
        topic_frequencies = defaultdict(int)
        for ticket in processed_tickets:
            for topic in ticket.topics:
                topic_frequencies[topic] += 1
        
        # Keyword co-occurrence analysis
        keyword_cooccurrence = self._analyze_keyword_cooccurrence(processed_tickets)
        
        # Sentiment trends
        sentiment_trends = [ticket.sentiment_score for ticket in processed_tickets]
        
        # Entity mentions across all tickets
        entity_mentions = defaultdict(list)
        for ticket in processed_tickets:
            for entity in ticket.entities:
                entity_mentions[entity].append(ticket.original_ticket.ticket_id)
        
        # Urgency patterns
        urgency_patterns = []
        for ticket in processed_tickets:
            urgency_patterns.extend(ticket.urgency_indicators)
        
        # Temporal patterns (simplified)
        temporal_patterns = defaultdict(int)
        for ticket in processed_tickets:
            if ticket.original_ticket.timestamp:
                try:
                    date = datetime.fromisoformat(ticket.original_ticket.timestamp)
                    hour = date.hour
                    temporal_patterns[f"hour_{hour}"] += 1
                except:
                    pass
        
        return PatternAnalysis(
            topic_frequencies=dict(topic_frequencies),
            keyword_cooccurrence=keyword_cooccurrence,
            sentiment_trends=sentiment_trends,
            entity_mentions=dict(entity_mentions),
            urgency_patterns=urgency_patterns,
            temporal_patterns=dict(temporal_patterns)
        )
    
    def _analyze_keyword_cooccurrence(self, processed_tickets: List[ProcessedTicket]) -> Dict[str, Dict[str, int]]:
        """Analyze which keywords appear together frequently"""
        cooccurrence = defaultdict(lambda: defaultdict(int))
        
        for ticket in processed_tickets:
            keywords = ticket.keywords
            # Check all pairs of keywords
            for i, kw1 in enumerate(keywords):
                for j, kw2 in enumerate(keywords):
                    if i != j:  # Don't count self-cooccurrence
                        cooccurrence[kw1][kw2] += 1
        
        return dict(cooccurrence)
    
    def identify_root_causes(self, processed_tickets: List[ProcessedTicket]) -> List[RootCauseCandidate]:
        """Identify potential root causes from ticket patterns"""
        
        root_cause_candidates = []
        pattern_analysis = self.analyze_patterns(processed_tickets)
        
        # Analyze each pattern category
        for cause_category, pattern_info in self.root_cause_patterns.items():
            candidate = self._evaluate_root_cause_category(
                cause_category, 
                pattern_info, 
                processed_tickets, 
                pattern_analysis
            )
            
            if candidate.confidence > 0.3:  # Minimum confidence threshold
                root_cause_candidates.append(candidate)
        
        # Sort by confidence score
        root_cause_candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        return root_cause_candidates
    
    def _evaluate_root_cause_category(self, category: str, pattern_info: Dict[str, List[str]], 
                                    processed_tickets: List[ProcessedTicket], 
                                    pattern_analysis: PatternAnalysis) -> RootCauseCandidate:
        """Evaluate a specific root cause category"""
        
        # Calculate frequency score
        matching_tickets = []
        evidence_quotes = []
        
        for ticket in processed_tickets:
            text_lower = ticket.cleaned_text
            
            # Check for keyword matches
            keyword_matches = sum(1 for keyword in pattern_info['keywords'] 
                                if keyword in text_lower)
            
            # Check for pattern matches
            pattern_matches = sum(1 for pattern in pattern_info['patterns'] 
                                if pattern in text_lower)
            
            if keyword_matches > 0 or pattern_matches > 0:
                matching_tickets.append(ticket)
                
                # Extract evidence quote (first 200 characters)
                quote = ticket.cleaned_text[:200] + "..." if len(ticket.cleaned_text) > 200 else ticket.cleaned_text
                evidence_quotes.append(quote)
        
        # Calculate confidence score
        frequency_score = len(matching_tickets) / len(processed_tickets) if processed_tickets else 0
        
        # Calculate coherence score (how well the evidence supports the cause)
        coherence_score = self._calculate_coherence_score(matching_tickets, pattern_info)
        
        # Combine scores
        confidence = (frequency_score * 0.6 + coherence_score * 0.4)
        
        # Generate root cause statement
        cause_statement = self._generate_cause_statement(category, len(matching_tickets), len(processed_tickets))
        
        return RootCauseCandidate(
            cause=cause_statement,
            confidence=confidence,
            evidence_count=len(matching_tickets),
            supporting_quotes=evidence_quotes[:3],  # Top 3 quotes
            frequency_score=frequency_score,
            coherence_score=coherence_score
        )
    
    def _calculate_coherence_score(self, matching_tickets: List[ProcessedTicket], 
                                 pattern_info: Dict[str, List[str]]) -> float:
        """Calculate how coherent the evidence is for a root cause"""
        if not matching_tickets:
            return 0.0
        
        # Check consistency of issues mentioned
        common_keywords = set()
        for ticket in matching_tickets:
            ticket_keywords = set(ticket.keywords)
            if not common_keywords:
                common_keywords = ticket_keywords
            else:
                common_keywords = common_keywords.intersection(ticket_keywords)
        
        # Higher coherence if more tickets share common keywords
        coherence = len(common_keywords) / max(1, len(matching_tickets))
        
        return min(1.0, coherence * 2)  # Scale to 0-1
    
    def _generate_cause_statement(self, category: str, matched_count: int, total_count: int) -> str:
        """Generate a natural language statement of the root cause"""
        
        percentage = (matched_count / total_count * 100) if total_count > 0 else 0
        
        cause_statements = {
            'system_issues': f"Technical infrastructure problems affecting {percentage:.1f}% of reported issues",
            'user_interface': f"User interface design issues causing confusion for {percentage:.1f}% of users",
            'process_workflow': f"Unclear or complicated business processes affecting {percentage:.1f}% of operations",
            'integration_problems': f"Third-party integration failures impacting {percentage:.1f}% of transactions",
            'data_issues': f"Data quality and management problems affecting {percentage:.1f}% of reports",
            'communication': f"Notification and communication system gaps affecting {percentage:.1f}% of users",
            'performance': f"System performance and speed issues impacting {percentage:.1f}% of user experience",
            'feature_functionality': f"Missing or broken feature functionality affecting {percentage:.1f}% of intended use cases"
        }
        
        return cause_statements.get(category, f"System-wide issues affecting {percentage:.1f}% of user reported problems")

class EvidenceAnalyzer:
    """Analyze supporting evidence and quotes for root cause analysis"""
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
    
    def extract_supporting_quotes(self, processed_tickets: List[ProcessedTicket], 
                                cause_keywords: List[str]) -> List[str]:
        """Extract most relevant quotes supporting the identified cause"""
        
        scored_quotes = []
        
        for ticket in processed_tickets:
            score = 0
            text_lower = ticket.cleaned_text.lower()
            
            # Score based on keyword matches
            for keyword in cause_keywords:
                score += text_lower.count(keyword)
            
            # Score based on problem indicators
            for indicator in self.preprocessor.problem_indicators:
                if indicator in text_lower:
                    score += 1
            
            # Extract relevant portion of text
            if score > 0:
                # Find most relevant sentence
                sentences = re.split(r'[.!?]+', ticket.cleaned_text)
                best_sentence = ""
                best_sentence_score = 0
                
                for sentence in sentences:
                    sentence_score = sum(1 for keyword in cause_keywords if keyword in sentence.lower())
                    if sentence_score > best_sentence_score:
                        best_sentence_score = sentence_score
                        best_sentence = sentence.strip()
                
                if best_sentence:
                    quote = best_sentence[:250] + "..." if len(best_sentence) > 250 else best_sentence
                    scored_quotes.append((quote, score))
        
        # Sort by score and return top quotes
        scored_quotes.sort(key=lambda x: x[1], reverse=True)
        return [quote for quote, score in scored_quotes[:3]]
    
    def analyze_keyword_frequency(self, processed_tickets: List[ProcessedTicket]) -> Dict[str, int]:
        """Analyze frequency of keywords across all tickets"""
        
        all_keywords = []
        for ticket in processed_tickets:
            all_keywords.extend(ticket.keywords)
        
        keyword_freq = Counter(all_keywords)
        
        # Filter out very common words that don't add insight
        common_non_insight = {'issue', 'problem', 'help', 'support', 'please', 'thank', 'sorry'}
        filtered_freq = {k: v for k, v in keyword_freq.items() if k not in common_non_insight}
        
        return dict(sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True)[:20])
    
    def perform_sentiment_analysis(self, processed_tickets: List[ProcessedTicket]) -> Dict[str, Any]:
        """Perform overall sentiment analysis across all tickets"""
        
        sentiments = [ticket.sentiment_score for ticket in processed_tickets]
        
        if not sentiments:
            return {"overall_sentiment": 0, "distribution": {}}
        
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Categorize sentiments
        distribution = {
            "very_negative": sum(1 for s in sentiments if s < -0.5),
            "negative": sum(1 for s in sentiments if -0.5 <= s < -0.1),
            "neutral": sum(1 for s in sentiments if -0.1 <= s < 0.1),
            "positive": sum(1 for s in sentiments if 0.1 <= s < 0.5),
            "very_positive": sum(1 for s in sentiments if s >= 0.5)
        }
        
        return {
            "overall_sentiment": avg_sentiment,
            "sentiment_distribution": distribution,
            "sentiment_trend": "improving" if avg_sentiment > 0 else "concerning"
        }

# Initialize FastAPI app
app = FastAPI(
    title="Unstructured Data Summarizer",
    description="Intelligent text analysis system for customer support ticket root cause analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pattern_analyzer = PatternAnalyzer()
evidence_analyzer = EvidenceAnalyzer()

class DatabaseManager:
    def __init__(self, db_path: str = "ticket_analysis.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for analysis storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    analysis_id TEXT PRIMARY KEY,
                    total_tickets INTEGER,
                    root_cause_statement TEXT,
                    confidence_score REAL,
                    analysis_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    batch_id TEXT,
                    content TEXT,
                    processed_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_analysis(self, analysis_id: str, root_cause: RootCauseAnalysis):
        """Save analysis to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO analyses 
                (analysis_id, total_tickets, root_cause_statement, confidence_score, analysis_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                analysis_id,
                root_cause.total_tickets,
                root_cause.root_cause_statement,
                root_cause.confidence_score,
                json.dumps(root_cause.dict())
            ))
    
    def get_analysis_history(self, limit: int = 20) -> List[Dict]:
        """Get analysis history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT analysis_id, total_tickets, root_cause_statement, confidence_score, created_at
                FROM analyses 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

# Initialize database manager
db_manager = DatabaseManager()

# Sample tickets for testing
SAMPLE_TICKETS = [
    {
        "id": "T001",
        "content": "I can't log into my account. The login page keeps showing an error message when I enter my password. This is very frustrating as I need to access my dashboard urgently.",
        "timestamp": "2025-11-15T10:30:00Z"
    },
    {
        "id": "T002", 
        "content": "The checkout process is broken. When I try to complete my purchase, the page freezes and I get a timeout error. I've tried multiple times but it doesn't work.",
        "timestamp": "2025-11-15T11:15:00Z"
    },
    {
        "id": "T003",
        "content": "My payment was declined but the funds were still charged to my account. I need this resolved immediately as this is causing serious financial issues for me.",
        "timestamp": "2025-11-15T12:00:00Z"
    },
    {
        "id": "T004",
        "content": "The mobile app crashes every time I try to view my transaction history. This is extremely inconvenient as I need to check my payments on the go.",
        "timestamp": "2025-11-15T13:45:00Z"
    },
    {
        "id": "T005",
        "content": "I received a notification about a payment but when I check my account, the transaction isn't there. This is confusing and I'm worried about my money.",
        "timestamp": "2025-11-15T14:20:00Z"
    },
    {
        "id": "T006",
        "content": "The website loading speed is incredibly slow. It takes over 30 seconds to load my dashboard and sometimes it times out completely.",
        "timestamp": "2025-11-15T15:00:00Z"
    },
    {
        "id": "T007",
        "content": "I can't find the export button for my reports. The interface is confusing and I've looked everywhere but can't figure out how to download my data.",
        "timestamp": "2025-11-15T16:30:00Z"
    },
    {
        "id": "T008",
        "content": "My account settings page shows an error 404. I need to update my contact information but I can't access the page at all.",
        "timestamp": "2025-11-15T17:15:00Z"
    },
    {
        "id": "T009",
        "content": "The integration with our accounting software is not working. Data sync has been failing for the past week and this is affecting our monthly reporting.",
        "timestamp": "2025-11-15T18:00:00Z"
    },
    {
        "id": "T010",
        "content": "I'm getting error messages when trying to upload documents to my profile. The file upload feature appears to be completely broken.",
        "timestamp": "2025-11-15T19:30:00Z"
    }
]

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Unstructured Data Summarizer API",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "Customer support ticket analysis",
            "Root cause identification",
            "Pattern recognition",
            "Evidence-based insights"
        ]
    }

@app.get("/api/v1/sample-tickets")
async def get_sample_tickets():
    """Get sample customer support tickets for testing"""
    return {
        "sample_tickets": SAMPLE_TICKETS,
        "description": "10 sample customer support tickets demonstrating common issues"
    }

@app.post("/api/v1/upload-tickets", response_model=AnalysisResponse)
async def upload_tickets(request: TicketUploadRequest, tickets_text: str = Field(..., description="JSON array of ticket objects or plain text tickets")):
    """Process uploaded customer support tickets and identify root causes"""
    
    import time
    start_time = time.time()
    
    try:
        # Parse tickets
        try:
            # Try to parse as JSON
            tickets_data = json.loads(tickets_text)
            if not isinstance(tickets_data, list):
                raise ValueError("Tickets must be provided as a JSON array")
        except json.JSONDecodeError:
            # If not JSON, treat as plain text and split by lines
            ticket_lines = [line.strip() for line in tickets_text.split('\n') if line.strip()]
            tickets_data = [{"content": line} for line in ticket_lines]
        
        # Process tickets
        processed_tickets = []
        for i, ticket_data in enumerate(tickets_data[:10]):  # Limit to 10 tickets
            if isinstance(ticket_data, dict):
                content = ticket_data.get('content', str(ticket_data))
                ticket_id = ticket_data.get('id', f"T{i+1:03d}")
                timestamp = ticket_data.get('timestamp')
            else:
                content = str(ticket_data)
                ticket_id = f"T{i+1:03d}"
                timestamp = None
            
            ticket = TicketData(
                ticket_id=ticket_id,
                content=content,
                timestamp=timestamp
            )
            
            processed_ticket = pattern_analyzer.preprocessor.preprocess_ticket(ticket)
            processed_tickets.append(processed_ticket)
        
        if len(processed_tickets) == 0:
            raise ValueError("No valid tickets found")
        
        # Perform root cause analysis
        root_cause_candidates = pattern_analyzer.identify_root_causes(processed_tickets)
        
        if not root_cause_candidates:
            raise ValueError("No root causes could be identified from the provided tickets")
        
        # Select the most confident root cause
        best_candidate = root_cause_candidates[0]
        
        # Perform detailed analysis
        pattern_analysis = pattern_analyzer.analyze_patterns(processed_tickets)
        sentiment_analysis = evidence_analyzer.perform_sentiment_analysis(processed_tickets)
        keywords_identified = list(evidence_analyzer.analyze_keyword_frequency(processed_tickets).keys())
        
        # Create root cause analysis
        analysis_id = str(uuid.uuid4())
        root_cause = RootCauseAnalysis(
            analysis_id=analysis_id,
            total_tickets=len(processed_tickets),
            root_cause_statement=best_candidate.cause,
            confidence_score=best_candidate.confidence,
            supporting_evidence=best_candidate.supporting_quotes,
            pattern_analysis=asdict(pattern_analysis),
            topic_frequency=pattern_analysis.topic_frequencies,
            sentiment_analysis=sentiment_analysis,
            keywords_identified=keywords_identified,
            processing_metadata={
                "processing_time": time.time() - start_time,
                "tickets_processed": len(processed_tickets),
                "candidates_identified": len(root_cause_candidates)
            },
            created_at=datetime.now()
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(root_cause, processed_tickets)
        
        # Save to database
        db_manager.save_analysis(analysis_id, root_cause)
        
        processing_time = time.time() - start_time
        
        response = AnalysisResponse(
            success=True,
            root_cause=root_cause,
            summary={
                "analysis_type": "Root Cause Analysis",
                "total_tickets": len(processed_tickets),
                "primary_root_cause": best_candidate.cause,
                "confidence_level": f"{best_candidate.confidence:.1%}",
                "supporting_evidence_count": len(best_candidate.supporting_quotes)
            },
            recommendations=recommendations,
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def _generate_recommendations(root_cause: RootCauseAnalysis, processed_tickets: List[ProcessedTicket]) -> List[str]:
    """Generate actionable recommendations based on root cause analysis"""
    
    recommendations = []
    cause_lower = root_cause.root_cause_statement.lower()
    
    # System/Technical issues
    if "technical infrastructure" in cause_lower or "system" in cause_lower:
        recommendations.extend([
            "Conduct immediate system health check and identify bottlenecks",
            "Implement enhanced monitoring and alerting for system performance",
            "Review and update infrastructure scaling policies"
        ])
    
    # User Interface issues
    if "user interface" in cause_lower or "interface" in cause_lower:
        recommendations.extend([
            "Conduct user experience audit to identify confusing interface elements",
            "Implement user testing sessions to validate interface improvements",
            "Review and simplify navigation workflows and information architecture"
        ])
    
    # Process/Workflow issues
    if "business process" in cause_lower or "workflow" in cause_lower:
        recommendations.extend([
            "Map current customer journey and identify process pain points",
            "Develop simplified, step-by-step user guides and documentation",
            "Implement process automation where appropriate to reduce manual steps"
        ])
    
    # Integration problems
    if "integration" in cause_lower or "third-party" in cause_lower:
        recommendations.extend([
            "Review third-party API documentation and update integration code",
            "Implement robust error handling and retry mechanisms for API calls",
            "Set up monitoring for external service availability and performance"
        ])
    
    # Performance issues
    if "performance" in cause_lower or "speed" in cause_lower:
        recommendations.extend([
            "Optimize database queries and implement query caching",
            "Review and optimize front-end asset loading and compression",
            "Consider infrastructure scaling or CDN implementation for better performance"
        ])
    
    # Feature functionality
    if "feature" in cause_lower or "functionality" in cause_lower:
        recommendations.extend([
            "Conduct feature audit to identify broken or missing functionality",
            "Implement comprehensive testing for all user-facing features",
            "Review feature documentation and ensure user guidance is available"
        ])
    
    # Data issues
    if "data" in cause_lower:
        recommendations.extend([
            "Implement data validation and quality checks in data processing pipeline",
            "Set up automated data consistency monitoring and alerts",
            "Review data architecture and implement proper backup and recovery procedures"
        ])
    
    # Communication issues
    if "communication" in cause_lower or "notification" in cause_lower:
        recommendations.extend([
            "Audit notification system and ensure all critical events trigger appropriate alerts",
            "Implement user preference management for notification settings",
            "Test notification delivery across all channels (email, SMS, in-app)"
        ])
    
    # If no specific recommendations match, provide general ones
    if len(recommendations) == 0:
        recommendations = [
            "Conduct detailed incident review to understand the scope of the problem",
            "Implement comprehensive customer feedback collection system",
            "Establish regular review process for customer support patterns and trends"
        ]
    
    return recommendations[:5]  # Limit to 5 recommendations

@app.get("/api/v1/analysis-history")
async def get_analysis_history(limit: int = 20):
    """Get analysis history"""
    try:
        history = db_manager.get_analysis_history(limit)
        return {
            "history": history,
            "total_analyses": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/analyze-sample")
async def analyze_sample_tickets():
    """Analyze the sample tickets for demonstration purposes"""
    
    import time
    start_time = time.time()
    
    try:
        # Create ticket objects from sample data
        processed_tickets = []
        for ticket_data in SAMPLE_TICKETS:
            ticket = TicketData(
                ticket_id=ticket_data["id"],
                content=ticket_data["content"],
                timestamp=ticket_data["timestamp"]
            )
            
            processed_ticket = pattern_analyzer.preprocessor.preprocess_ticket(ticket)
            processed_tickets.append(processed_ticket)
        
        # Perform root cause analysis
        root_cause_candidates = pattern_analyzer.identify_root_causes(processed_tickets)
        best_candidate = root_cause_candidates[0]
        
        # Perform detailed analysis
        pattern_analysis = pattern_analyzer.analyze_patterns(processed_tickets)
        sentiment_analysis = evidence_analyzer.perform_sentiment_analysis(processed_tickets)
        keywords_identified = list(evidence_analyzer.analyze_keyword_frequency(processed_tickets).keys())
        
        # Create root cause analysis
        analysis_id = str(uuid.uuid4())
        root_cause = RootCauseAnalysis(
            analysis_id=analysis_id,
            total_tickets=len(processed_tickets),
            root_cause_statement=best_candidate.cause,
            confidence_score=best_candidate.confidence,
            supporting_evidence=best_candidate.supporting_quotes,
            pattern_analysis=asdict(pattern_analysis),
            topic_frequency=pattern_analysis.topic_frequencies,
            sentiment_analysis=sentiment_analysis,
            keywords_identified=keywords_identified,
            processing_metadata={
                "processing_time": time.time() - start_time,
                "tickets_processed": len(processed_tickets),
                "candidates_identified": len(root_cause_candidates),
                "data_source": "sample_tickets"
            },
            created_at=datetime.now()
        )
        
        # Generate recommendations
        recommendations = _generate_recommendations(root_cause, processed_tickets)
        
        processing_time = time.time() - start_time
        
        response = AnalysisResponse(
            success=True,
            root_cause=root_cause,
            summary={
                "analysis_type": "Sample Ticket Analysis",
                "total_tickets": len(processed_tickets),
                "primary_root_cause": best_candidate.cause,
                "confidence_level": f"{best_candidate.confidence:.1%}",
                "supporting_evidence_count": len(best_candidate.supporting_quotes)
            },
            recommendations=recommendations,
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing sample tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sample analysis failed: {str(e)}")

# Run server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "template_38_unstructured_data_summarizer:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )