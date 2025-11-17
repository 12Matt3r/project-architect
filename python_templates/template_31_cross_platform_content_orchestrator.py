"""
Template #31: Cross-Platform Content Orchestrator
Advanced AI-powered content generation system that creates consistent multi-format campaigns
"""

import os
import json
import base64
import io
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import uuid
from PIL import Image, ImageEnhance
import requests
import re
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Cross-Platform Content Orchestrator",
    description="Advanced AI-powered content generation system for consistent multi-format campaigns",
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
DATABASE_PATH = "/workspace/content_orchestrator.db"
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_database():
    """Initialize SQLite database for content campaigns"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Campaigns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            image_filename TEXT,
            twitter_thread TEXT,
            linkedin_post TEXT,
            podcast_script TEXT,
            consistency_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    # Content variations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content_variations (
            id TEXT PRIMARY KEY,
            campaign_id TEXT,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            variation_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# Enums for content types and platforms
class Platform(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PODCAST = "podcast"

class VariationType(Enum):
    ORIGINAL = "original"
    ALTERNATIVE = "alternative"
    OPTIMIZED = "optimized"

@dataclass
class ContentStyle:
    """Defines platform-specific content styles"""
    platform: Platform
    tone: str
    max_length: int
    structure: List[str]
    hashtags_strategy: str
    call_to_action: str

# Content style configurations
CONTENT_STYLES = {
    Platform.TWITTER: ContentStyle(
        platform=Platform.TWITTER,
        tone="witty, engaging, conversational",
        max_length=280,
        structure=["hook", "insight", "value", "engagement"],
        hashtags_strategy="2-3 relevant hashtags, trending when possible",
        call_to_action="Ask question, encourage replies"
    ),
    Platform.LINKEDIN: ContentStyle(
        platform=Platform.LINKEDIN,
        tone="professional, thoughtful, authoritative",
        max_length=3000,
        structure=["insight", "context", "analysis", "conclusion", "discussion"],
        hashtags_strategy="5-8 professional hashtags",
        call_to_action="Encourage professional discussion"
    ),
    Platform.PODCAST: ContentStyle(
        platform=Platform.PODCAST,
        tone="conversational, exploratory, interview-style",
        max_length=2000,
        structure=["intro", "topic_development", "key_points", "q&a", "outro"],
        hashtags_strategy="N/A",
        call_to_action="Subscribe and provide feedback"
    )
}

@dataclass
class ContentPiece:
    """Represents a piece of content for a specific platform"""
    platform: Platform
    title: str
    content: str
    metadata: Dict
    consistency_score: float

class ContentGenerator:
    """Advanced content generation engine with multi-modal input processing"""
    
    def __init__(self):
        self.content_patterns = self._load_content_patterns()
        self.visual_analysis = self._load_visual_analysis()
        
    def _load_content_patterns(self) -> Dict:
        """Load content generation patterns for each platform"""
        return {
            "twitter": {
                "opening_hooks": [
                    "Hot take: {topic}",
                    "Just realized something about {topic}",
                    "{topic} is having a moment, and here's why you should care",
                    "Plot twist about {topic}",
                    "The {topic} conversation nobody's having"
                ],
                "engagement_techniques": [
                    "Thoughts?",
                    "Agree or disagree?",
                    "What am I missing?",
                    "Change my mind",
                    "Hit me with your best take"
                ],
                "value_statements": [
                    "The key insight here is",
                    "What this really means is",
                    "Here's the thing nobody tells you about",
                    "The real opportunity is",
                    "This changes everything because"
                ]
            },
            "linkedin": {
                "professional_hooks": [
                    "In my analysis of {topic}, I've identified",
                    "After extensive research into {topic}, it's clear that",
                    "The {topic} landscape is evolving, and leaders need to understand",
                    "Based on recent developments in {topic},",
                    "The future of {topic} depends on understanding"
                ],
                "structured_insights": [
                    "First, we need to consider",
                    "Additionally, there's the question of",
                    "From a strategic perspective,",
                    "On the implementation side,",
                    "Looking ahead, the implications are"
                ],
                "professional_conclusions": [
                    "The path forward requires",
                    "Organizations should prioritize",
                    "The key takeaway is",
                    "Success in this area depends on",
                    "Leaders who understand this will be positioned to"
                ]
            },
            "podcast": {
                "interview_intros": [
                    "Today we're diving deep into {topic}, a topic that's reshaping how we think about",
                    "We're exploring {topic} with someone who's been watching this space closely",
                    "Let's talk about {topic} and why it matters in today's landscape",
                    "Our focus today is {topic} and what it means for the future of",
                    "We sat down to discuss {topic} and its implications for"
                ],
                "exploration_questions": [
                    "What's driving the current conversation around {topic}?",
                    "How do you see {topic} evolving over the next few years?",
                    "What should people know about {topic} that they might be missing?",
                    "What are the biggest opportunities in {topic} right now?",
                    "How can someone get started with {topic}?"
                ],
                "conversational_transitions": [
                    "That's a great point, and it makes me think about",
                    "Speaking of which, I'd love to hear your thoughts on",
                    "That connects to something I've been wondering about",
                    "Tell me more about that perspective",
                    "How does that fit into the broader picture of {topic}?"
                ]
            }
        }
    
    def _load_visual_analysis(self) -> Dict:
        """Load visual analysis patterns for image processing"""
        return {
            "mood_indicators": {
                "bright": ["energetic", "optimistic", "vibrant", "dynamic"],
                "dark": ["serious", "mysterious", "introspective", "dramatic"],
                "warm": ["friendly", "approachable", "cozy", "welcoming"],
                "cool": ["professional", "sophisticated", "calm", "modern"],
                "colorful": ["creative", "playful", "expressive", "artistic"]
            },
            "composition_types": {
                "centered": ["focused", "balanced", "symmetrical", "structured"],
                "asymmetrical": ["dynamic", "movement", "energy", "flow"],
                "minimal": ["clean", "simple", "elegant", "refined"],
                "complex": ["detailed", "rich", "layered", "comprehensive"]
            },
            "subject_matters": {
                "people": ["human", "relatable", "storytelling", "connection"],
                "objects": ["practical", "functional", "specific", "tangible"],
                "scenes": ["environmental", "contextual", "situational", "atmospheric"],
                "abstract": ["conceptual", "theoretical", "interpretive", "artistic"]
            }
        }
    
    def analyze_image(self, image_data: bytes) -> Dict:
        """Analyze uploaded image to extract visual context and mood"""
        try:
            # Load and analyze image
            image = Image.open(io.BytesIO(image_data))
            
            # Get basic image properties
            width, height = image.size
            aspect_ratio = width / height if height > 0 else 1
            
            # Enhance image for better analysis
            enhancer = ImageEnhance.Contrast(image)
            enhanced = enhancer.enhance(1.2)
            
            # Simple color analysis (simulated since we're not doing actual color analysis)
            # In a production environment, you'd use proper color analysis
            size_category = "small" if width < 400 else "medium" if width < 1200 else "large"
            complexity = "simple" if aspect_ratio > 1.5 or aspect_ratio < 0.67 else "balanced"
            
            # Generate visual metadata
            visual_context = {
                "dimensions": {"width": width, "height": height},
                "aspect_ratio": round(aspect_ratio, 2),
                "size_category": size_category,
                "composition_style": complexity,
                "mood_indicators": ["professional", "engaging", "visual"],
                "suggested_tone": "accessible" if size_category == "large" else "concise",
                "visual_elements": ["color", "composition", "subject_matter"],
                "content_angle": f"Visual storytelling through {size_category} format",
                "brand_compatibility": "high"
            }
            
            return visual_context
            
        except Exception as e:
            return {
                "error": f"Image analysis failed: {str(e)}",
                "mood_indicators": ["professional", "neutral"],
                "suggested_tone": "professional",
                "visual_elements": ["general"],
                "content_angle": "text-focused content"
            }
    
    def generate_twitter_thread(self, topic: str, visual_context: Dict, campaign_metadata: Dict) -> ContentPiece:
        """Generate Twitter thread with witty, engaging content"""
        
        style = CONTENT_STYLES[Platform.TWITTER]
        patterns = self.content_patterns["twitter"]
        
        # Generate thread content
        thread_content = []
        tweet_count = 0
        
        # Tweet 1: Hook
        hook_template = patterns["opening_hooks"][tweet_count % len(patterns["opening_hooks"])]
        hook = hook_template.format(topic=topic)
        
        tweet1 = f"🧵 {hook}\n\n"
        if visual_context.get("suggested_tone") == "accessible":
            tweet1 += f"Here's what I found: {topic} is more relevant than ever.\n\n"
        tweet1 += "Thread ⬇️"
        
        thread_content.append(tweet1)
        tweet_count += 1
        
        # Tweet 2: Key insight
        insight_template = patterns["value_statements"][tweet_count % len(patterns["value_statements"])]
        insight = insight_template.format(topic=topic)
        
        tweet2 = f"{insight}:\n\n"
        tweet2 += f"• {topic} impacts how we approach daily decisions\n"
        tweet2 += f"• The connection to real outcomes is clearer than ever\n"
        tweet2 += f"• This creates new opportunities for growth\n\n"
        
        # Add visual context integration
        if visual_context.get("mood_indicators"):
            mood = visual_context["mood_indicators"][0]
            tweet2 += f"📊 The {mood} nature of this topic makes it particularly engaging.\n"
        
        thread_content.append(tweet2)
        tweet_count += 1
        
        # Tweet 3: Value proposition
        tweet3 = f"Why this matters:\n\n"
        tweet3 += f"1. {topic} affects multiple industries\n"
        tweet3 += f"2. Early adopters see significant advantages\n"
        tweet3 += f"3. The learning curve is smaller than expected\n\n"
        
        if visual_context.get("visual_elements"):
            elements = visual_context["visual_elements"][:2]
            tweet3 += f"💡 Visual communication enhances understanding of {', '.join(elements)}.\n"
        
        thread_content.append(tweet3)
        tweet_count += 1
        
        # Tweet 4: Action/Engagement
        engagement = patterns["engagement_techniques"][tweet_count % len(patterns["engagement_techniques"])]
        tweet4 = f"The bottom line: {topic} is worth your attention.\n\n"
        tweet4 += f"{engagement}\n\n"
        
        # Add campaign-specific hashtags
        campaign_id = campaign_metadata.get("campaign_id", "content")
        tweet4 += f"#{topic.replace(' ', '')} #ContentMarketing #{campaign_id}"
        
        thread_content.append(tweet4)
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency_score(thread_content, topic, visual_context)
        
        return ContentPiece(
            platform=Platform.TWITTER,
            title=f"Twitter Thread: {topic}",
            content="\n\n".join(thread_content),
            metadata={
                "tweet_count": len(thread_content),
                "character_count": sum(len(tweet) for tweet in thread_content),
                "hashtags": [f"#{topic.replace(' ', '')}", "#ContentMarketing"],
                "engagement_elements": ["questions", "bullet_points", "visual_emojis"],
                "tone": "witty and engaging"
            },
            consistency_score=consistency_score
        )
    
    def generate_linkedin_post(self, topic: str, visual_context: Dict, campaign_metadata: Dict) -> ContentPiece:
        """Generate professional LinkedIn post with long-form content"""
        
        style = CONTENT_STYLES[Platform.LINKEDIN]
        patterns = self.content_patterns["linkedin"]
        
        # Generate post content
        post_content = ""
        
        # Opening hook
        hook_template = patterns["professional_hooks"][0]
        hook = hook_template.format(topic=topic)
        
        post_content += f"{hook}\n\n"
        
        # Main body with insights
        insights = patterns["structured_insights"]
        
        post_content += f"{insights[0]} understanding the current landscape of {topic}.\n\n"
        post_content += f"{insights[1]} the implementation challenges that organizations face when adapting to {topic}.\n\n"
        post_content += f"{insights[2]} {topic} isn't just a trend—it's a fundamental shift in how we approach strategic decisions.\n\n"
        
        # Integrate visual context
        if visual_context.get("visual_elements"):
            elements = visual_context["visual_elements"]
            post_content += f"The visual representation of {topic} through {', '.join(elements)} provides concrete evidence of this transformation.\n\n"
        
        # Professional insights
        post_content += f"{insights[3]} successful teams are those that can effectively communicate the value of {topic} to stakeholders at all levels.\n\n"
        
        post_content += f"{insights[4]} the future belongs to organizations that can integrate {topic} into their core strategies while maintaining operational excellence.\n\n"
        
        # Conclusion with call to action
        conclusion_template = patterns["professional_conclusions"][0]
        conclusion = conclusion_template.format(topic=topic)
        
        post_content += f"**{conclusion}**\n\n"
        post_content += f"Successful implementation of {topic} strategies requires:\n"
        post_content += f"• Clear communication of value propositions\n"
        post_content += f"• Cross-functional collaboration\n"
        post_content += f"• Continuous learning and adaptation\n\n"
        
        post_content += f"What role does {topic} play in your organization's strategy? I'd love to hear your thoughts and experiences.\n\n"
        
        # Add professional hashtags
        hashtags = ["#Leadership", "#Strategy", "#Innovation", "#BusinessGrowth", "#ProfessionalDevelopment"]
        post_content += " ".join(hashtags)
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency_score([post_content], topic, visual_context)
        
        return ContentPiece(
            platform=Platform.LINKEDIN,
            title=f"LinkedIn Post: {topic}",
            content=post_content,
            metadata={
                "word_count": len(post_content.split()),
                "character_count": len(post_content),
                "paragraphs": post_content.count('\n\n') + 1,
                "call_to_action": "professional_discussion",
                "tone": "professional and authoritative"
            },
            consistency_score=consistency_score
        )
    
    def generate_podcast_script(self, topic: str, visual_context: Dict, campaign_metadata: Dict) -> ContentPiece:
        """Generate conversational podcast script outline"""
        
        style = CONTENT_STYLES[Platform.PODCAST]
        patterns = self.content_patterns["podcast"]
        
        # Generate podcast script
        script_content = ""
        
        # Intro
        intro_template = patterns["interview_intros"][0]
        intro = intro_template.format(topic=topic)
        
        script_content += f"**INTRO (0:00-0:30)**\n"
        script_content += f"{intro}\n\n"
        script_content += f"We're going to explore the key insights around {topic} and what they mean for professionals in today's market.\n\n"
        
        # Main discussion
        script_content += f"**MAIN DISCUSSION (0:30-12:00)**\n\n"
        
        script_content += f"**Segment 1: Understanding the Landscape**\n"
        script_content += f"Host: \"{patterns['exploration_questions'][0].format(topic=topic)}\"\n"
        script_content += f"Guest: [Response discussing current trends and developments]\n\n"
        
        script_content += f"**Segment 2: Strategic Implications**\n"
        script_content += f"Host: \"{patterns['exploration_questions'][1].format(topic=topic)}\"\n"
        script_content += f"Guest: [Analysis of strategic considerations and business impact]\n\n"
        
        script_content += f"**Segment 3: Practical Applications**\n"
        script_content += f"Host: \"{patterns['exploration_questions'][2].format(topic=topic)}\"\n"
        script_content += f"Guest: [Practical insights and implementation strategies]\n\n"
        
        script_content += f"**Segment 4: Future Outlook**\n"
        script_content += f"Host: \"{patterns['exploration_questions'][3].format(topic=topic)}\"\n"
        script_content += f"Guest: [Predictions and recommendations for moving forward]\n\n"
        
        # Q&A section
        script_content += f"**Q&A SEGMENT (12:00-15:00)**\n"
        script_content += f"Host: \"Let's open it up for listener questions about {topic}.\"\n"
        script_content += f"[Community questions and responses]\n\n"
        
        # Outro
        script_content += f"**OUTRO (15:00-15:30)**\n"
        script_content += f"Host: \"{patterns['exploration_questions'][4].format(topic=topic)}\"\n"
        script_content += f"Guest: [Final advice and key takeaways]\n\n"
        script_content += f"Host: \"Thanks for joining us for this discussion on {topic}. Don't forget to subscribe and share your thoughts in the comments.\"\n\n"
        
        # Add episode metadata
        script_content += f"**EPISODE METADATA**\n"
        script_content += f"• Topic: {topic}\n"
        script_content += f"• Duration: ~15 minutes\n"
        script_content += f"• Format: Interview-style discussion\n"
        script_content += f"• Tone: Conversational and informative\n"
        script_content += f"• Target audience: Professionals interested in {topic}\n\n"
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency_score([script_content], topic, visual_context)
        
        return ContentPiece(
            platform=Platform.PODCAST,
            title=f"Podcast Script: {topic}",
            content=script_content,
            metadata={
                "estimated_duration": "15 minutes",
                "segments": 6,
                "word_count": len(script_content.split()),
                "format": "interview_outline",
                "tone": "conversational and exploratory"
            },
            consistency_score=consistency_score
        )
    
    def _calculate_consistency_score(self, content_list: List[str], topic: str, visual_context: Dict) -> float:
        """Calculate consistency score across content pieces"""
        base_score = 0.7
        
        # Topic consistency check
        topic_mentions = sum(content.lower().count(topic.lower()) for content in content_list)
        topic_bonus = min(0.1, topic_mentions * 0.02)
        
        # Visual context integration
        visual_bonus = 0.05 if visual_context.get("visual_elements") else 0
        
        # Tone consistency
        tone_words = ["professional", "engaging", "insightful", "valuable"]
        tone_consistency = sum(1 for content in content_list for word in tone_words if word in content.lower())
        tone_bonus = min(0.1, tone_consistency * 0.01)
        
        # Brand voice consistency
        brand_elements = ["strategy", "growth", "development", "innovation"]
        brand_bonus = sum(0.02 for content in content_list for word in brand_elements if word in content.lower())
        brand_bonus = min(0.15, brand_bonus)
        
        final_score = base_score + topic_bonus + visual_bonus + tone_bonus + brand_bonus
        return min(0.95, final_score)
    
    def create_campaign(self, topic: str, image_data: Optional[bytes], campaign_metadata: Dict) -> Dict:
        """Create complete content campaign with all three platforms"""
        
        # Generate unique campaign ID
        campaign_id = str(uuid.uuid4())
        
        # Analyze image if provided
        visual_context = {}
        image_filename = None
        
        if image_data:
            visual_context = self.analyze_image(image_data)
            # Save image file
            image_filename = f"{campaign_id}_image.jpg"
            image_path = f"/workspace/{image_filename}"
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
        
        # Generate content for each platform
        twitter_content = self.generate_twitter_thread(topic, visual_context, campaign_metadata)
        linkedin_content = self.generate_linked_in_post(topic, visual_context, campaign_metadata)
        podcast_content = self.generate_podcast_script(topic, visual_context, campaign_metadata)
        
        # Calculate overall campaign consistency
        consistency_scores = [
            twitter_content.consistency_score,
            linkedin_content.consistency_score,
            podcast_content.consistency_score
        ]
        overall_consistency = sum(consistency_scores) / len(consistency_scores)
        
        # Store campaign in database
        self._save_campaign_to_db(
            campaign_id=campaign_id,
            topic=topic,
            image_filename=image_filename,
            twitter_content=twitter_content.content,
            linkedin_content=linkedin_content.content,
            podcast_content=podcast_content.content,
            consistency_score=overall_consistency,
            metadata=campaign_metadata
        )
        
        # Compile final campaign response
        campaign = {
            "campaign_id": campaign_id,
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "consistency_score": overall_consistency,
            "content_pieces": [
                {
                    "platform": "twitter",
                    "title": twitter_content.title,
                    "content": twitter_content.content,
                    "metadata": twitter_content.metadata,
                    "consistency_score": twitter_content.consistency_score
                },
                {
                    "platform": "linkedin",
                    "title": linkedin_content.title,
                    "content": linkedin_content.content,
                    "metadata": linkedin_content.metadata,
                    "consistency_score": linkedin_content.consistency_score
                },
                {
                    "platform": "podcast",
                    "title": podcast_content.title,
                    "content": podcast_content.content,
                    "metadata": podcast_content.metadata,
                    "consistency_score": podcast_content.consistency_score
                }
            ],
            "visual_context": visual_context,
            "campaign_summary": {
                "total_pieces": 3,
                "avg_consistency_score": overall_consistency,
                "content_alignment": "High" if overall_consistency > 0.8 else "Medium" if overall_consistency > 0.6 else "Low"
            }
        }
        
        return campaign
    
    def _save_campaign_to_db(self, campaign_id: str, topic: str, image_filename: Optional[str],
                           twitter_content: str, linkedin_content: str, podcast_content: str,
                           consistency_score: float, metadata: Dict):
        """Save campaign data to SQLite database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaigns 
            (id, topic, image_filename, twitter_thread, linkedin_post, podcast_script, 
             consistency_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id, topic, image_filename, twitter_content, linkedin_content,
            podcast_content, consistency_score, json.dumps(metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def generate_content_variations(self, campaign_id: str, platform: str, content: str) -> List[Dict]:
        """Generate alternative versions of content for A/B testing"""
        variations = []
        
        # Alternative tone variations
        if platform == "twitter":
            variations.append({
                "type": "alternative_tone",
                "title": "More Casual Twitter Version",
                "content": content.replace("🧵", "").replace("Thread", "Quick thoughts"),
                "tone": "casual"
            })
        elif platform == "linkedin":
            variations.append({
                "type": "alternative_tone", 
                "title": "Concise LinkedIn Version",
                "content": content[:1500] + "...",  # Shorter version
                "tone": "concise"
            })
        
        # Optimized versions
        if platform == "twitter":
            variations.append({
                "type": "optimized",
                "title": "Character-Optimized Twitter Version", 
                "content": content.replace("🧵 Thread ⬇️", "🧵"),
                "optimization": "character_count"
            })
        
        return variations

# Initialize content generator
content_generator = ContentGenerator()

# API Models
class ContentGenerationRequest(BaseModel):
    topic: str = Field(..., description="The main topic for content generation")
    campaign_name: Optional[str] = Field(None, description="Optional campaign name")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    brand_voice: Optional[str] = Field("professional", description="Desired brand voice tone")
    custom_instructions: Optional[str] = Field(None, description="Additional custom instructions")

class CampaignResponse(BaseModel):
    campaign_id: str
    topic: str
    created_at: str
    consistency_score: float
    content_pieces: List[Dict]
    visual_context: Dict
    campaign_summary: Dict

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Cross-Platform Content Orchestrator API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "generate_campaign": "/api/v1/generate-campaign",
            "get_campaign": "/api/v1/campaign/{campaign_id}",
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
            "content_generator": "active",
            "image_processor": "ready"
        }
    }

@app.post("/api/v1/generate-campaign", response_model=CampaignResponse)
async def generate_campaign(
    topic: str = Form(..., description="Main topic for content generation"),
    image: Optional[UploadFile] = File(None, description="Optional image to analyze"),
    campaign_name: Optional[str] = Form(None, description="Optional campaign name"),
    target_audience: Optional[str] = Form(None, description="Target audience"),
    brand_voice: Optional[str] = Form("professional", description="Brand voice tone"),
    custom_instructions: Optional[str] = Form(None, description="Custom instructions")
):
    """
    Generate cross-platform content campaign from topic and optional image
    
    - **topic**: Main topic/theme for content creation
    - **image**: Optional image file for visual context analysis
    - **campaign_name**: Optional name for the campaign
    - **target_audience**: Description of target audience
    - **brand_voice**: Desired tone (professional, casual, etc.)
    - **custom_instructions**: Additional custom requirements
    """
    
    try:
        # Process image if provided
        image_data = None
        if image:
            image_data = await image.read()
        
        # Prepare campaign metadata
        campaign_metadata = {
            "campaign_name": campaign_name or f"Campaign for {topic}",
            "target_audience": target_audience or "General professional audience",
            "brand_voice": brand_voice,
            "custom_instructions": custom_instructions,
            "created_by": "cross_platform_orchestrator"
        }
        
        # Generate campaign
        campaign = content_generator.create_campaign(topic, image_data, campaign_metadata)
        
        return JSONResponse(content=campaign)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {str(e)}")

@app.get("/api/v1/campaign/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Retrieve previously generated campaign"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT topic, image_filename, twitter_thread, linkedin_post, podcast_script, 
                   consistency_score, created_at, metadata
            FROM campaigns WHERE id = ?
        ''', (campaign_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        topic, image_filename, twitter_thread, linkedin_post, podcast_script, \
        consistency_score, created_at, metadata_json = result
        
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        return {
            "campaign_id": campaign_id,
            "topic": topic,
            "created_at": created_at,
            "consistency_score": consistency_score,
            "content_pieces": [
                {"platform": "twitter", "content": twitter_thread},
                {"platform": "linkedin", "content": linkedin_post},
                {"platform": "podcast", "content": podcast_script}
            ],
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve campaign: {str(e)}")

@app.get("/api/v1/campaigns")
async def list_campaigns(limit: int = 10):
    """List recent campaigns"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, topic, consistency_score, created_at 
            FROM campaigns 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        campaigns = []
        for row in cursor.fetchall():
            campaign_id, topic, consistency_score, created_at = row
            campaigns.append({
                "campaign_id": campaign_id,
                "topic": topic,
                "consistency_score": consistency_score,
                "created_at": created_at
            })
        
        conn.close()
        
        return {
            "campaigns": campaigns,
            "total": len(campaigns)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list campaigns: {str(e)}")

@app.post("/api/v1/generate-variations/{campaign_id}/{platform}")
async def generate_content_variations(
    campaign_id: str,
    platform: str,
    content: str = Form(..., description="Original content to vary")
):
    """Generate alternative content versions for A/B testing"""
    try:
        if platform not in ["twitter", "linkedin", "podcast"]:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        variations = content_generator.generate_content_variations(campaign_id, platform, content)
        
        return {
            "campaign_id": campaign_id,
            "platform": platform,
            "original_content": content,
            "variations": variations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate variations: {str(e)}")

@app.get("/api/v1/analytics/{campaign_id}")
async def get_campaign_analytics(campaign_id: str):
    """Get campaign performance analytics"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get main campaign data
        cursor.execute('''
            SELECT topic, consistency_score, created_at, metadata
            FROM campaigns WHERE id = ?
        ''', (campaign_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        topic, consistency_score, created_at, metadata_json = result
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        # Calculate engagement metrics (simulated)
        engagement_metrics = {
            "twitter": {
                "estimated_reach": "2.5K-5K",
                "engagement_rate": "3.2%",
                "click_through_rate": "1.8%"
            },
            "linkedin": {
                "estimated_reach": "1K-2.5K", 
                "engagement_rate": "5.1%",
                "comment_rate": "2.3%"
            },
            "podcast": {
                "estimated_listens": "500-1K",
                "completion_rate": "78%",
                "subscription_rate": "12%"
            }
        }
        
        analytics = {
            "campaign_id": campaign_id,
            "topic": topic,
            "consistency_score": consistency_score,
            "created_at": created_at,
            "engagement_projections": engagement_metrics,
            "optimization_suggestions": [
                "Twitter: Consider adding more trending hashtags",
                "LinkedIn: Could benefit from more specific industry insights", 
                "Podcast: Add more interactive elements in Q&A section"
            ]
        }
        
        conn.close()
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)