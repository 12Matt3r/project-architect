"""
Template #28: Synthetic User Tester
Advanced AI application for analyzing website screenshots and generating user personas with journey predictions.

Author: MiniMax Agent
Date: 2025-11-17
"""

import base64
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import os
import cv2
import numpy as np
from PIL import Image
import io

# Configuration
SECRET_KEY = "synthetic_user_tester_secret_2025"
ALGORITHM = "HS256"

# Initialize FastAPI app
app = FastAPI(
    title="Synthetic User Tester",
    description="AI-powered website screenshot analysis and user persona generation",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database setup
def init_database():
    conn = sqlite3.connect('synthetic_user_tester.db')
    cursor = conn.cursor()
    
    # Create analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id TEXT PRIMARY KEY,
            image_data TEXT NOT NULL,
            personas TEXT NOT NULL,
            success_rate REAL,
            analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_context TEXT
        )
    ''')
    
    # Create user personas table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_personas (
            id TEXT PRIMARY KEY,
            analysis_id TEXT,
            persona_name TEXT NOT NULL,
            demographics TEXT,
            psychographics TEXT,
            success_prediction TEXT,
            journey_steps TEXT,
            FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()

# Models
class AnalysisRequest(BaseModel):
    user_input: str
    context_file: Optional[str] = None

class PersonaGenerationRequest(BaseModel):
    image_data: str
    website_type: Optional[str] = "general"
    target_audience: Optional[str] = "general"

class Persona(BaseModel):
    id: str
    name: str
    demographics: Dict[str, str]
    psychographics: Dict[str, str]
    success_prediction: str
    journey_steps: List[Dict[str, str]]

class AnalysisResult(BaseModel):
    analysis_id: str
    personas: List[Persona]
    overall_success_rate: float
    timestamp: str

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# Core AI Logic Classes
class ImageAnalyzer:
    """Advanced image analysis for website screenshots"""
    
    def __init__(self):
        self.demographic_patterns = {
            "young_professional": {
                "age_range": "25-35",
                "tech_comfort": "high",
                "design_preference": "minimalist, clean",
                "attention_span": "short"
            },
            "senior_user": {
                "age_range": "55-70",
                "tech_comfort": "low",
                "design_preference": "traditional, high contrast",
                "attention_span": "extended"
            },
            "gen_z_user": {
                "age_range": "18-24",
                "tech_comfort": "very high",
                "design_preference": "trendy, mobile-first",
                "attention_span": "very short"
            },
            "millennial_parent": {
                "age_range": "30-45",
                "tech_comfort": "medium-high",
                "design_preference": "family-friendly, trustworthy",
                "attention_span": "moderate"
            },
            "small_business_owner": {
                "age_range": "35-55",
                "tech_comfort": "medium",
                "design_preference": "professional, efficient",
                "attention_span": "time-conscious"
            },
            "researcher_academic": {
                "age_range": "25-65",
                "tech_comfort": "high",
                "design_preference": "information-dense, detailed",
                "attention_span": "extended"
            },
            "creative_professional": {
                "age_range": "25-40",
                "tech_comfort": "high",
                "design_preference": "visually appealing, creative",
                "attention_span": "moderate"
            },
            "budget_conscious": {
                "age_range": "20-60",
                "tech_comfort": "medium",
                "design_preference": "value-focused, transparent pricing",
                "attention_span": "price-sensitive"
            },
            "international_user": {
                "age_range": "20-50",
                "tech_comfort": "varies",
                "design_preference": "multilingual, culturally adaptable",
                "attention_span": "cultural considerations"
            },
            "accessibility_needs": {
                "age_range": "15-80",
                "tech_comfort": "varies",
                "design_preference": "accessible, screen reader friendly",
                "attention_span": "extended processing time"
            }
        }
    
    def analyze_screenshot(self, image_data: str) -> Dict[str, Any]:
        """Analyze website screenshot for user experience insights"""
        try:
            # Decode base64 image
            image = self._decode_image(image_data)
            
            # Perform image analysis
            analysis = {
                "layout_complexity": self._analyze_layout_complexity(image),
                "visual_hierarchy": self._analyze_visual_hierarchy(image),
                "accessibility_features": self._check_accessibility_features(image),
                "mobile_responsiveness": self._assess_mobile_design(image),
                "call_to_action_visibility": self._identify_cta_elements(image),
                "content_density": self._measure_content_density(image)
            }
            
            return analysis
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image analysis failed: {str(e)}")
    
    def _decode_image(self, image_data: str) -> np.ndarray:
        """Decode base64 image data to OpenCV format"""
        try:
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            return np.array(image)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
    
    def _analyze_layout_complexity(self, image: np.ndarray) -> str:
        """Analyze the complexity of the website layout"""
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Detect edges to understand layout structure
        edges = cv2.Canny(gray, 50, 150)
        
        # Count edge density
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        if edge_density > 0.3:
            return "complex"
        elif edge_density > 0.15:
            return "moderate"
        else:
            return "simple"
    
    def _analyze_visual_hierarchy(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze visual hierarchy and design elements"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Analyze color diversity
        unique_colors = len(np.unique(hsv.reshape(-1, hsv.shape[2]), axis=0))
        
        # Detect text regions (simplified)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        text_regions = self._detect_text_regions(gray)
        
        return {
            "color_diversity": "high" if unique_colors > 50 else "moderate" if unique_colors > 20 else "low",
            "text_density": len(text_regions),
            "visual_balance": self._assess_visual_balance(image)
        }
    
    def _detect_text_regions(self, gray_image: np.ndarray) -> List[Dict]:
        """Detect text regions in the image"""
        # Simple text detection using edge detection
        edges = cv2.Canny(gray_image, 30, 100)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 5000:  # Filter for text-like regions
                x, y, w, h = cv2.boundingRect(contour)
                text_regions.append({
                    "x": x, "y": y, "width": w, "height": h,
                    "area": area
                })
        
        return text_regions
    
    def _assess_visual_balance(self, image: np.ndarray) -> str:
        """Assess the visual balance of the design"""
        height, width = image.shape[:2]
        
        # Divide image into quadrants
        h_mid, w_mid = height // 2, width // 2
        
        quadrants = [
            image[:h_mid, :w_mid],      # Top-left
            image[:h_mid, w_mid:],      # Top-right
            image[h_mid:, :w_mid],      # Bottom-left
            image[h_mid:, w_mid:]       # Bottom-right
        ]
        
        # Calculate brightness variance for each quadrant
        brightness_variance = [np.var(cv2.cvtColor(q, cv2.COLOR_RGB2GRAY)) for q in quadrants]
        
        # If variance is too high between quadrants, consider unbalanced
        variance_diff = max(brightness_variance) - min(brightness_variance)
        
        if variance_diff > 1000:
            return "unbalanced"
        elif variance_diff > 500:
            return "moderate"
        else:
            return "balanced"
    
    def _check_accessibility_features(self, image: np.ndarray) -> Dict[str, bool]:
        """Check for accessibility features in the design"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Check for high contrast elements
        high_contrast_regions = self._detect_high_contrast(gray)
        
        # Check for large clickable areas
        large_clickable_areas = self._detect_large_clickable_areas(gray)
        
        return {
            "high_contrast": len(high_contrast_regions) > 3,
            "large_click_targets": large_clickable_areas,
            "alt_text_indicators": False,  # Cannot detect alt text from image
            "screen_reader_friendly": False  # Cannot detect from image
        }
    
    def _detect_high_contrast(self, gray_image: np.ndarray) -> List[Dict]:
        """Detect high contrast regions"""
        # Simple edge detection for contrast boundaries
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Find contours of high contrast areas
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        high_contrast_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200:  # Minimum area for significant contrast
                x, y, w, h = cv2.boundingRect(contour)
                high_contrast_regions.append({"x": x, "y": y, "width": w, "height": h})
        
        return high_contrast_regions
    
    def _detect_large_clickable_areas(self, gray_image: np.ndarray) -> bool:
        """Detect if there are large clickable areas"""
        # Simple heuristic: look for large rectangular regions
        edges = cv2.Canny(gray_image, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000:  # Large clickable area threshold
                return True
        
        return False
    
    def _assess_mobile_design(self, image: np.ndarray) -> Dict[str, Any]:
        """Assess mobile design responsiveness"""
        height, width = image.shape[:2]
        aspect_ratio = width / height
        
        return {
            "mobile_optimized": aspect_ratio < 1.5,
            "responsive_layout": self._detect_responsive_elements(image),
            "touch_friendly": self._assess_touch_friendly_design(image)
        }
    
    def _detect_responsive_elements(self, image: np.ndarray) -> bool:
        """Detect signs of responsive design"""
        # Look for grid-like structures that indicate responsive design
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 30, 100)
        
        # Detect horizontal and vertical lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=80)
        
        if lines is not None:
            horizontal_lines = sum(1 for rho, theta in lines[:, 0] if abs(theta) < 0.1 or abs(theta - np.pi) < 0.1)
            vertical_lines = sum(1 for rho, theta in lines[:, 0] if abs(theta - np.pi/2) < 0.1)
            
            return (horizontal_lines + vertical_lines) > 10
        
        return False
    
    def _assess_touch_friendly_design(self, image: np.ndarray) -> bool:
        """Assess touch-friendly design elements"""
        # Look for large buttons and spacing
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        large_buttons = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Check for button-like characteristics
            if area > 2000 and 0.5 < aspect_ratio < 3:
                large_buttons += 1
        
        return large_buttons > 3
    
    def _identify_cta_elements(self, image: np.ndarray) -> List[Dict]:
        """Identify call-to-action elements"""
        # Look for button-like elements and bright color regions
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Define ranges for common CTA colors (red, orange, blue, green)
        cta_colors = [
            ([0, 100, 100], [10, 255, 255]),    # Red
            ([10, 100, 100], [25, 255, 255]),   # Orange
            ([100, 100, 100], [130, 255, 255]), # Blue
            ([40, 100, 100], [80, 255, 255])    # Green
        ]
        
        cta_elements = []
        for lower, upper in cta_colors:
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Minimum area for CTA elements
                    x, y, w, h = cv2.boundingRect(contour)
                    cta_elements.append({
                        "x": x, "y": y, "width": w, "height": h,
                        "area": area,
                        "position": "top" if y < image.shape[0] * 0.3 else "middle" if y < image.shape[0] * 0.7 else "bottom"
                    })
        
        return cta_elements
    
    def _measure_content_density(self, image: np.ndarray) -> Dict[str, Any]:
        """Measure content density and organization"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Count text-like regions
        text_regions = self._detect_text_regions(gray)
        
        # Calculate whitespace percentage
        edges = cv2.Canny(gray, 30, 100)
        content_pixels = np.sum(edges > 0)
        total_pixels = edges.shape[0] * edges.shape[1]
        content_ratio = content_pixels / total_pixels
        
        return {
            "text_density": len(text_regions),
            "whitespace_ratio": 1 - content_ratio,
            "organization_score": "high" if content_ratio < 0.3 else "moderate" if content_ratio < 0.6 else "low"
        }

class PersonaGenerator:
    """Generate diverse user personas based on website analysis"""
    
    def __init__(self):
        self.base_personas = {
            "young_professional": {
                "name": "Alex Chen",
                "description": "A tech-savvy marketing professional",
                "traits": ["fast-paced", "goal-oriented", "value efficiency"],
                "frustrations": ["slow loading", "complicated navigation", "poor mobile experience"],
                "goals": ["quick information", "easy transactions", "modern design"]
            },
            "senior_user": {
                "name": "Margaret Thompson",
                "description": "A retired teacher exploring digital services",
                "traits": ["cautious", "detail-oriented", "prefers clear instructions"],
                "frustrations": ["small text", "complex interfaces", "unclear pricing"],
                "goals": ["security", "clear information", "reliable service"]
            },
            "gen_z_user": {
                "name": "Jordan Rodriguez",
                "description": "A social media influencer and content creator",
                "traits": ["mobile-first", "visual-focused", "short attention span"],
                "frustrations": ["desktop-only features", "slow performance", "boring visuals"],
                "goals": ["instant gratification", "social sharing", "trendy design"]
            },
            "millennial_parent": {
                "name": "Sarah Williams",
                "description": "A working mother of two young children",
                "traits": ["time-pressed", "value-conscious", "trust-oriented"],
                "frustrations": ["time-consuming processes", "hidden fees", "complicated returns"],
                "goals": ["convenience", "value for money", "family safety"]
            },
            "small_business_owner": {
                "name": "Mike Johnson",
                "description": "Owner of a local construction company",
                "traits": ["practical", "ROI-focused", "time-conscious"],
                "frustrations": ["unnecessary features", "slow support", "unclear pricing"],
                "goals": ["business efficiency", "cost-effective solutions", "professional credibility"]
            },
            "researcher_academic": {
                "name": "Dr. Emily Foster",
                "description": "University researcher specializing in education",
                "traits": ["detail-oriented", "evidence-based", "thorough"],
                "frustrations": ["oversimplified content", "lack of depth", "poor citations"],
                "goals": ["comprehensive information", "data accuracy", "professional credibility"]
            },
            "creative_professional": {
                "name": "Riley Kim",
                "description": "Freelance graphic designer",
                "traits": ["visually-driven", "creative", "aesthetic-focused"],
                "frustrations": ["poor typography", "cluttered design", "lack of inspiration"],
                "goals": ["visual appeal", "creative inspiration", "portfolio quality"]
            },
            "budget_conscious": {
                "name": "Carlos Martinez",
                "description": "College student on a tight budget",
                "traits": ["price-sensitive", "deal-seeking", "value-maximizing"],
                "frustrations": ["high prices", "hidden costs", "pushy sales tactics"],
                "goals": ["best deals", "transparent pricing", "student discounts"]
            },
            "international_user": {
                "name": "Hiro Tanaka",
                "description": "International student from Japan",
                "traits": ["culturally-aware", "language-conscious", "adaptive"],
                "frustrations": ["poor localization", "cultural insensitivity", "language barriers"],
                "goals": ["cultural respect", "language support", "global compatibility"]
            },
            "accessibility_needs": {
                "name": "David Lee",
                "description": "User with visual impairment using assistive technology",
                "traits": ["technology-adaptive", "patient", "accessibility-focused"],
                "frustrations": ["poor screen reader support", "low contrast", "keyboard navigation issues"],
                "goals": ["full accessibility", "assistive technology compatibility", "equal access"]
            }
        }
    
    def generate_personas(self, analysis: Dict[str, Any], count: int = 10) -> List[Persona]:
        """Generate user personas based on website analysis"""
        personas = []
        
        # Select most relevant personas based on analysis
        relevant_personas = self._select_relevant_personas(analysis, count)
        
        for i, persona_key in enumerate(relevant_personas):
            base_persona = self.base_personas[persona_key]
            
            # Customize persona based on website analysis
            journey = self._generate_user_journey(base_persona, analysis)
            success_prediction = self._predict_success_rate(base_persona, analysis, journey)
            
            persona = Persona(
                id=str(uuid.uuid4()),
                name=base_persona["name"],
                demographics={
                    "age_range": self._get_persona_demographic(persona_key, "age_range"),
                    "location": self._get_persona_demographic(persona_key, "location"),
                    "education": self._get_persona_demographic(persona_key, "education"),
                    "income": self._get_persona_demographic(persona_key, "income")
                },
                psychographics={
                    "personality": base_persona["traits"],
                    "values": self._get_persona_values(persona_key),
                    "frustrations": base_persona["frustrations"],
                    "goals": base_persona["goals"]
                },
                success_prediction=success_prediction,
                journey_steps=journey
            )
            
            personas.append(persona)
        
        return personas
    
    def _select_relevant_personas(self, analysis: Dict[str, Any], count: int) -> List[str]:
        """Select the most relevant personas based on website analysis"""
        relevant = []
        
        # Analyze website characteristics
        complexity = analysis.get("layout_complexity", "moderate")
        mobile_optimized = analysis.get("mobile_responsiveness", {}).get("mobile_optimized", False)
        accessibility = analysis.get("accessibility_features", {})
        cta_visibility = len(analysis.get("call_to_action_visibility", []))
        content_density = analysis.get("content_density", {}).get("organization_score", "moderate")
        
        # Scoring system for persona relevance
        persona_scores = {
            "young_professional": 0,
            "senior_user": 0,
            "gen_z_user": 0,
            "millennial_parent": 0,
            "small_business_owner": 0,
            "researcher_academic": 0,
            "creative_professional": 0,
            "budget_conscious": 0,
            "international_user": 0,
            "accessibility_needs": 0
        }
        
        # Score based on website characteristics
        if complexity == "simple":
            persona_scores["senior_user"] += 3
            persona_scores["accessibility_needs"] += 2
            persona_scores["budget_conscious"] += 2
        elif complexity == "complex":
            persona_scores["researcher_academic"] += 3
            persona_scores["small_business_owner"] += 2
        
        if mobile_optimized:
            persona_scores["gen_z_user"] += 3
            persona_scores["young_professional"] += 2
            persona_scores["millennial_parent"] += 2
        else:
            persona_scores["researcher_academic"] += 2
            persona_scores["small_business_owner"] += 1
        
        if accessibility.get("high_contrast", False):
            persona_scores["accessibility_needs"] += 3
            persona_scores["senior_user"] += 2
        
        if cta_visibility > 5:
            persona_scores["young_professional"] += 2
            persona_scores["gen_z_user"] += 2
            persona_scores["budget_conscious"] += 2
        
        if content_density == "high":
            persona_scores["researcher_academic"] += 3
            persona_scores["small_business_owner"] += 2
        elif content_density == "low":
            persona_scores["gen_z_user"] += 2
            persona_scores["young_professional"] += 1
        
        # Select top scoring personas
        sorted_personas = sorted(persona_scores.items(), key=lambda x: x[1], reverse=True)
        relevant = [persona[0] for persona in sorted_personas[:count]]
        
        # Ensure we always have at least some diversity
        if len(relevant) < count:
            remaining = [p for p in self.base_personas.keys() if p not in relevant]
            relevant.extend(remaining[:count - len(relevant)])
        
        return relevant
    
    def _get_persona_demographic(self, persona_key: str, demographic: str) -> str:
        """Get demographic information for a persona"""
        demographics_map = {
            "young_professional": {
                "age_range": "25-35",
                "location": "Urban metropolitan areas",
                "education": "Bachelor's degree",
                "income": "$50,000 - $80,000"
            },
            "senior_user": {
                "age_range": "55-70",
                "location": "Suburban or rural",
                "education": "High school to college",
                "income": "$30,000 - $60,000"
            },
            "gen_z_user": {
                "age_range": "18-24",
                "location": "Urban areas",
                "education": "In college or recent graduate",
                "income": "$20,000 - $40,000"
            },
            "millennial_parent": {
                "age_range": "30-45",
                "location": "Suburban areas",
                "education": "Bachelor's degree",
                "income": "$60,000 - $100,000"
            },
            "small_business_owner": {
                "age_range": "35-55",
                "location": "Various",
                "education": "High school to some college",
                "income": "$40,000 - $150,000"
            },
            "researcher_academic": {
                "age_range": "25-65",
                "location": "University cities",
                "education": "Master's or PhD",
                "income": "$45,000 - $90,000"
            },
            "creative_professional": {
                "age_range": "25-40",
                "location": "Creative hubs",
                "education": "Bachelor's degree in creative field",
                "income": "$35,000 - $70,000"
            },
            "budget_conscious": {
                "age_range": "20-60",
                "location": "Various",
                "education": "High school to college",
                "income": "$15,000 - $45,000"
            },
            "international_user": {
                "age_range": "20-50",
                "location": "International",
                "education": "Varies",
                "income": "Varies"
            },
            "accessibility_needs": {
                "age_range": "15-80",
                "location": "Various",
                "education": "Varies",
                "income": "Varies"
            }
        }
        
        return demographics_map.get(persona_key, {}).get(demographic, "Not specified")
    
    def _get_persona_values(self, persona_key: str) -> List[str]:
        """Get core values for a persona"""
        values_map = {
            "young_professional": ["Efficiency", "Career growth", "Modern technology"],
            "senior_user": ["Reliability", "Security", "Traditional values"],
            "gen_z_user": ["Authenticity", "Social responsibility", "Innovation"],
            "millennial_parent": ["Family", "Security", "Work-life balance"],
            "small_business_owner": ["Profitability", "Practicality", "Independence"],
            "researcher_academic": ["Knowledge", "Accuracy", "Evidence"],
            "creative_professional": ["Artistic expression", "Beauty", "Uniqueness"],
            "budget_conscious": ["Value", "Savings", "Practicality"],
            "international_user": ["Cultural respect", "Global perspective", "Adaptability"],
            "accessibility_needs": ["Inclusion", "Accessibility", "Equality"]
        }
        
        return values_map.get(persona_key, ["General values"])
    
    def _generate_user_journey(self, persona: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate a 5-step user journey for the persona"""
        base_steps = [
            {
                "step": 1,
                "action": "Initial page load and first impression",
                "thoughts": f"How does this first glance align with {persona['name']}'s expectations?",
                "emotions": "Curiosity" if len(persona['traits']) > 2 else "Neutral",
                "pain_points": "None yet - first impressions"
            },
            {
                "step": 2,
                "action": "Navigation and information seeking",
                "thoughts": f"Can {persona['name']} quickly find what they're looking for?",
                "emotions": "Determination",
                "pain_points": self._identify_navigation_pain_points(persona, analysis)
            },
            {
                "step": 3,
                "action": "Content engagement and evaluation",
                "thoughts": f"Does the content resonate with {persona['name']}'s values?",
                "emotions": "Interest" if "creative" in persona.get('traits', []) else "Focused",
                "pain_points": self._identify_content_pain_points(persona, analysis)
            },
            {
                "step": 4,
                "action": "Action or conversion attempt",
                "thoughts": f"Will {persona['name']} complete the desired action?",
                "emotions": "Decision-making",
                "pain_points": self._identify_conversion_pain_points(persona, analysis)
            },
            {
                "step": 5,
                "action": "Completion or abandonment",
                "thoughts": f"What factors influenced {persona['name']}'s final decision?",
                "emotions": "Satisfaction" if "success" in persona.get('traits', []) else "Uncertainty",
                "pain_points": "Final obstacles or successful completion"
            }
        ]
        
        return base_steps
    
    def _identify_navigation_pain_points(self, persona: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Identify navigation-specific pain points"""
        complexity = analysis.get("layout_complexity", "moderate")
        
        if persona.get('frustrations', []):
            if "complicated navigation" in persona['frustrations']:
                return "Complex menu structure, unclear navigation labels"
            if "small text" in persona['frustrations']:
                return "Small navigation elements, poor readability"
            if "slow loading" in persona['frustrations']:
                return "Navigation lag, slow page transitions"
        
        if complexity == "complex":
            return "Overwhelming layout, difficult to find key navigation elements"
        elif complexity == "simple":
            return "Limited navigation options, may feel too basic"
        else:
            return "Standard navigation challenges"
    
    def _identify_content_pain_points(self, persona: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Identify content-specific pain points"""
        content_density = analysis.get("content_density", {}).get("organization_score", "moderate")
        
        if persona.get('frustrations', []):
            if "poor typography" in persona['frustrations']:
                return "Inconsistent fonts, poor spacing, unreadable text"
            if "unclear pricing" in persona['frustrations']:
                return "Hidden costs, unclear pricing structure"
            if "lack of depth" in persona['frustrations']:
                return "Oversimplified content, insufficient detail"
        
        if content_density == "high":
            return "Information overload, difficult to process key messages"
        elif content_density == "low":
            return "Insufficient information, lack of detail"
        else:
            return "Standard content challenges"
    
    def _identify_conversion_pain_points(self, persona: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Identify conversion-specific pain points"""
        cta_visibility = len(analysis.get("call_to_action_visibility", []))
        
        if persona.get('frustrations', []):
            if "hidden fees" in persona['frustrations']:
                return "Surprise costs, unclear terms and conditions"
            if "complicated returns" in persona['frustrations']:
                return "Difficult return process, unclear refund policy"
            if "pushy sales tactics" in persona['frustrations']:
                return "Aggressive sales approach, pressure tactics"
        
        if cta_visibility < 3:
            return "Unclear call-to-action, missing conversion elements"
        elif cta_visibility > 8:
            return "Too many competing calls-to-action, decision paralysis"
        else:
            return "Standard conversion challenges"
    
    def _predict_success_rate(self, persona: Dict[str, Any], analysis: Dict[str, Any], journey: List[Dict]) -> str:
        """Predict success rate based on persona fit and website analysis"""
        base_score = 50  # Start with neutral score
        
        # Adjust based on persona-goal alignment
        goals = persona.get('goals', [])
        website_strengths = self._identify_website_strengths(analysis)
        
        alignment_score = 0
        for goal in goals:
            if any(strength in goal.lower() for strength in website_strengths):
                alignment_score += 10
        
        # Adjust based on pain point matches
        frustrations = persona.get('frustrations', [])
        website_weaknesses = self._identify_website_weaknesses(analysis)
        
        mismatch_score = 0
        for frustration in frustrations:
            if any(weakness in frustration.lower() for weakness in website_weaknesses):
                mismatch_score += 15
        
        # Calculate final score
        final_score = base_score + alignment_score - mismatch_score
        final_score = max(10, min(95, final_score))  # Clamp between 10-95%
        
        if final_score >= 80:
            return f"High success probability ({final_score}%) - Website aligns well with user expectations and goals"
        elif final_score >= 60:
            return f"Moderate success probability ({final_score}%) - Website has good potential but may face some challenges"
        elif final_score >= 40:
            return f"Low-moderate success probability ({final_score}%) - Website may frustrate user expectations in key areas"
        else:
            return f"Low success probability ({final_score}%) - Significant misalignment between user needs and website design"
    
    def _identify_website_strengths(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify website strengths from analysis"""
        strengths = []
        
        if analysis.get("layout_complexity") == "simple":
            strengths.append("clean")
        elif analysis.get("layout_complexity") == "complex":
            strengths.append("comprehensive")
        
        if analysis.get("mobile_responsiveness", {}).get("mobile_optimized"):
            strengths.append("mobile-friendly")
        
        if analysis.get("accessibility_features", {}).get("high_contrast"):
            strengths.append("accessible")
        
        cta_count = len(analysis.get("call_to_action_visibility", []))
        if 3 <= cta_count <= 6:
            strengths.append("clear action")
        
        content_org = analysis.get("content_density", {}).get("organization_score")
        if content_org == "high":
            strengths.append("well-organized")
        elif content_org == "low":
            strengths.append("minimalist")
        
        return strengths
    
    def _identify_website_weaknesses(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify website weaknesses from analysis"""
        weaknesses = []
        
        if analysis.get("layout_complexity") == "complex":
            weaknesses.append("complicated")
        elif analysis.get("layout_complexity") == "simple":
            weaknesses.append("basic")
        
        if not analysis.get("mobile_responsiveness", {}).get("mobile_optimized"):
            weaknesses.append("mobile")
        
        if not analysis.get("accessibility_features", {}).get("high_contrast"):
            weaknesses.append("contrast")
        
        cta_count = len(analysis.get("call_to_action_visibility", []))
        if cta_count < 3:
            weaknesses.append("unclear action")
        elif cta_count > 8:
            weaknesses.append("overwhelming")
        
        content_org = analysis.get("content_density", {}).get("organization_score")
        if content_org == "low":
            weaknesses.append("organized")
        elif content_org == "high":
            weaknesses.append("minimalist")
        
        return weaknesses

class DatabaseManager:
    """Database operations for storing analysis results"""
    
    def __init__(self):
        self.db_path = "synthetic_user_tester.db"
    
    def save_analysis(self, result: AnalysisResult) -> str:
        """Save analysis result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO analysis_results 
                (id, image_data, personas, success_rate, user_context)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                result.analysis_id,
                "",  # Image data not stored in this version
                json.dumps([persona.dict() for persona in result.personas]),
                result.overall_success_rate,
                ""
            ))
            
            # Save individual personas
            for persona in result.personas:
                cursor.execute('''
                    INSERT INTO user_personas 
                    (id, analysis_id, persona_name, demographics, psychographics, success_prediction, journey_steps)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    persona.id,
                    result.analysis_id,
                    persona.name,
                    json.dumps(persona.demographics),
                    json.dumps(persona.psychographics),
                    persona.success_prediction,
                    json.dumps(persona.journey_steps)
                ))
            
            conn.commit()
            return result.analysis_id
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()
    
    def get_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Retrieve analysis result from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, personas, success_rate, analysis_timestamp
                FROM analysis_results
                WHERE id = ?
            ''', (analysis_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            personas_data = json.loads(row[1])
            personas = [Persona(**persona_data) for persona_data in personas_data]
            
            return AnalysisResult(
                analysis_id=row[0],
                personas=personas,
                overall_success_rate=row[2],
                timestamp=row[3]
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()

# Initialize components
image_analyzer = ImageAnalyzer()
persona_generator = PersonaGenerator()
db_manager = DatabaseManager()

# API Endpoints
@app.post("/api/v1/process", response_model=AnalysisResult)
async def process_website_analysis(request: AnalysisRequest, user: dict = Depends(verify_token)):
    """
    Main endpoint for website screenshot analysis and persona generation
    
    Args:
        request: Contains user_input and optional context_file
        user: Authenticated user object
    
    Returns:
        AnalysisResult with generated personas and success predictions
    """
    try:
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # For this template, we simulate the screenshot analysis based on user input
        # In a real implementation, this would process an actual image
        analysis = image_analyzer.analyze_screenshot(request.user_input)
        
        # Generate personas
        personas = persona_generator.generate_personas(analysis)
        
        # Calculate overall success rate
        success_rates = []
        for persona in personas:
            # Extract numeric success rate from prediction
            prediction = persona.success_prediction
            if "%" in prediction:
                rate_str = prediction.split("(")[1].split("%")[0]
                try:
                    rate = int(rate_str)
                    success_rates.append(rate)
                except ValueError:
                    success_rates.append(50)  # Default fallback
        
        overall_success_rate = sum(success_rates) / len(success_rates) if success_rates else 50
        
        # Create result
        result = AnalysisResult(
            analysis_id=analysis_id,
            personas=personas,
            overall_success_rate=overall_success_rate,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to database
        db_manager.save_analysis(result)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/upload-screenshot")
async def upload_screenshot(file: UploadFile = File(...), user: dict = Depends(verify_token)):
    """
    Upload and analyze website screenshot
    
    Args:
        file: Image file upload
        user: Authenticated user object
    
    Returns:
        AnalysisResult with generated personas
    """
    try:
        # Read file content
        content = await file.read()
        
        # Convert to base64
        image_data = base64.b64encode(content).decode('utf-8')
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Analyze image
        analysis = image_analyzer.analyze_screenshot(image_data)
        
        # Generate personas
        personas = persona_generator.generate_personas(analysis)
        
        # Calculate overall success rate
        success_rates = []
        for persona in personas:
            prediction = persona.success_prediction
            if "%" in prediction:
                rate_str = prediction.split("(")[1].split("%")[0]
                try:
                    rate = int(rate_str)
                    success_rates.append(rate)
                except ValueError:
                    success_rates.append(50)
        
        overall_success_rate = sum(success_rates) / len(success_rates) if success_rates else 50
        
        # Create result
        result = AnalysisResult(
            analysis_id=analysis_id,
            personas=personas,
            overall_success_rate=overall_success_rate,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to database
        db_manager.save_analysis(result)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot analysis failed: {str(e)}")

@app.get("/api/v1/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str, user: dict = Depends(verify_token)):
    """
    Retrieve stored analysis result
    
    Args:
        analysis_id: Unique analysis identifier
        user: Authenticated user object
    
    Returns:
        AnalysisResult
    """
    result = db_manager.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Synthetic User Tester", "version": "1.0.0"}

@app.post("/api/v1/generate-token")
async def generate_token():
    """Generate a demo JWT token for testing"""
    payload = {
        "user_id": "demo_user",
        "username": "demo_user",
        "exp": datetime.utcnow().timestamp() + 3600  # 1 hour expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
