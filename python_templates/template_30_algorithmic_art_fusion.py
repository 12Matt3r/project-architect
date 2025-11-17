"""
Template #30: Algorithmic Art Fusion
Advanced AI application for merging artistic movements using Directional-Stimulus Prompting (DSP)

Author: MiniMax Agent
Date: 2025-11-17
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import os
import re
from enum import Enum

# Configuration
SECRET_KEY = "algorithmic_art_fusion_secret_2025"
ALGORITHM = "HS256"

# Initialize FastAPI app
app = FastAPI(
    title="Algorithmic Art Fusion",
    description="AI-powered artistic movement fusion using Directional-Stimulus Prompting",
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
    conn = sqlite3.connect('algorithmic_art_fusion.db')
    cursor = conn.cursor()
    
    # Create fusion projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fusion_projects (
            id TEXT PRIMARY KEY,
            movement_1 TEXT NOT NULL,
            movement_2 TEXT NOT NULL,
            generated_prompt TEXT NOT NULL,
            artistic_elements TEXT NOT NULL,
            fusion_analysis TEXT NOT NULL,
            project_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            project_name TEXT,
            style_preferences TEXT
        )
    ''')
    
    # Create artistic movements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artistic_movements (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            characteristics TEXT NOT NULL,
            key_artists TEXT NOT NULL,
            historical_period TEXT NOT NULL,
            visual_principles TEXT NOT NULL,
            color_palette TEXT NOT NULL,
            composition_style TEXT NOT NULL,
            emotional_qualities TEXT NOT NULL
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

class ArtFusionRequest(BaseModel):
    movement_1: str
    movement_2: str
    fusion_intensity: float = 0.5  # 0.0 = balanced, 1.0 = maximum fusion
    style_preferences: Optional[List[str]] = None
    target_emotion: Optional[str] = "balanced"
    output_format: str = "detailed"  # "detailed", "concise", "technical"

class FusionResult(BaseModel):
    project_id: str
    generated_prompt: str
    artistic_elements: Dict[str, Any]
    fusion_analysis: Dict[str, Any]
    movement_analysis: Dict[str, Any]
    visual_principles: List[str]
    emotional_synthesis: str
    technical_specifications: Dict[str, Any]
    timestamp: str

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# Core AI Logic Classes
class ArtisticMovementDatabase:
    """Comprehensive database of artistic movements and their characteristics"""
    
    def __init__(self):
        self.movements = {
            "baroque": {
                "name": "Baroque",
                "characteristics": [
                    "Dramatic contrasts of light and shadow",
                    "Dynamic movement and energy",
                    "Ornate decoration and grandeur",
                    "Emotional intensity and theatricality",
                    "Rich colors and golden tones",
                    "Complex compositions with many figures"
                ],
                "key_artists": ["Caravaggio", "Rembrandt", "Rubens", "Bernini", "Velazquez"],
                "historical_period": "1600-1750",
                "visual_principles": {
                    "composition": "Diagonal lines, pyramidal forms, dramatic foreshortening",
                    "lighting": "Chiaroscuro - strong contrasts between light and dark",
                    "color": "Rich golds, deep browns, vibrant reds, jewel tones",
                    "texture": "Smooth surfaces with elaborate ornamentation",
                    "space": "Deep, atmospheric perspective with theatrical staging"
                },
                "color_palette": ["#8B4513", "#DAA520", "#8B0000", "#2F4F4F", "#4B0082", "#CD853F"],
                "composition_style": "Dynamic, complex, with emphasis on movement and drama",
                "emotional_qualities": ["Dramatic", "Passionate", "Religious fervor", "Royal grandeur", "Theatrical"]
            },
            "minimalism": {
                "name": "Minimalism",
                "characteristics": [
                    "Simplicity and reduction to essentials",
                    "Clean lines and geometric shapes",
                    "Neutral color palettes",
                    "Emphasis on negative space",
                    "Industrial materials and textures",
                    "Functional and purposeful design"
                ],
                "key_artists": ["Donald Judd", "Agnes Martin", "Frank Stella", "Sol LeWitt", "Dan Flavin"],
                "historical_period": "1960s-1970s",
                "visual_principles": {
                    "composition": "Geometric precision, balanced arrangements, grid systems",
                    "lighting": "Even, diffused lighting with minimal shadows",
                    "color": "Monochromatic, neutral tones, limited color palettes",
                    "texture": "Smooth, industrial materials like metal, glass, concrete",
                    "space": "Clean, uncluttered, emphasis on breathing room"
                },
                "color_palette": ["#F5F5F5", "#E5E5E5", "#CCCCCC", "#999999", "#666666", "#333333"],
                "composition_style": "Geometric, balanced, with emphasis on proportion and harmony",
                "emotional_qualities": ["Serene", "Contemplative", "Peaceful", "Clean", "Focused"]
            },
            "impressionism": {
                "name": "Impressionism",
                "characteristics": [
                    "Capturing light and atmosphere",
                    "Loose brushwork and visible strokes",
                    "En plein air (outdoor) painting",
                    "Focus on momentary impressions",
                    "Bright, vibrant colors",
                    "Soft, diffused lighting effects"
                ],
                "key_artists": ["Monet", "Renoir", "Degas", "Pissarro", "Cezanne"],
                "historical_period": "1860s-1880s",
                "visual_principles": {
                    "composition": "Loose, spontaneous arrangements with emphasis on light",
                    "lighting": "Natural, changing light with visible brushstrokes",
                    "color": "Bright, pure colors with minimal black, optical mixing",
                    "texture": "Visible, broken brushwork creating surface texture",
                    "space": "Atmospheric perspective with soft edges"
                },
                "color_palette": ["#FFE4B5", "#FFB6C1", "#98FB98", "#87CEEB", "#DDA0DD", "#F0E68C"],
                "composition_style": "Spontaneous, light-focused, with emphasis on atmosphere",
                "emotional_qualities": ["Joyful", "Peaceful", "Optimistic", "Natural", "Ethereal"]
            },
            "expressionism": {
                "name": "Expressionism",
                "characteristics": [
                    "Distorted forms for emotional effect",
                    "Bold, non-naturalistic colors",
                    "Intensely personal subject matter",
                    "Rejection of traditional perspective",
                    "Psychological intensity",
                    "Geometric and angular compositions"
                ],
                "key_artists": ["Kandinsky", "Mondrian", "Klee", "Schiele", "Kokoschka"],
                "historical_period": "1905-1925",
                "visual_principles": {
                    "composition": "Geometric distortion, angular forms, non-representational",
                    "lighting": "Contrasting, dramatic with unnatural color temperatures",
                    "color": "Bold primaries, non-naturalistic, emotionally charged",
                    "texture": "Variable, from smooth to heavily textured",
                    "space": "Abstracted, flattened perspective"
                },
                "color_palette": ["#FF0000", "#0000FF", "#FFFF00", "#00FF00", "#FF00FF", "#00FFFF"],
                "composition_style": "Abstract, geometric, with emphasis on emotional impact",
                "emotional_qualities": ["Intense", "Anxious", "Passionate", "Dramatic", "Eccentric"]
            },
            "surrealism": {
                "name": "Surrealism",
                "characteristics": [
                    "Dreamlike, illogical imagery",
                    "Juxtaposition of unexpected elements",
                    "Biomorphic and organic forms",
                    "Exploration of the unconscious mind",
                    "Fantastical and impossible scenarios",
                    "Psychological and symbolic content"
                ],
                "key_artists": ["Dali", "Magritte", "Ernst", "Miro", "Delvaux"],
                "historical_period": "1920s-1930s",
                "visual_principles": {
                    "composition": "Illogical arrangements, floating objects, impossible perspectives",
                    "lighting": "Dreamlike, often multiple light sources",
                    "color": "Rich, saturated colors with symbolic meaning",
                    "texture": "Varied, from smooth to highly detailed",
                    "space": "Impossible, dreamlike with multiple vanishing points"
                },
                "color_palette": ["#8A2BE2", "#FF69B4", "#00CED1", "#FFD700", "#32CD32", "#FF6347"],
                "composition_style": "Illogical, dreamlike, with emphasis on the impossible",
                "emotional_qualities": ["Mysterious", "Erotic", "Anxious", "Dreamy", "Uncanny"]
            },
            "cubism": {
                "name": "Cubism",
                "characteristics": [
                    "Multiple perspectives simultaneously",
                    "Geometric fragmentation",
                    "Monochromatic color schemes",
                    "Analytical deconstruction of form",
                    "Flattened picture plane",
                    "Intellectual rather than emotional approach"
                ],
                "key_artists": ["Picasso", "Braque", "Gris", "Leger", "Gleizes"],
                "historical_period": "1907-1914",
                "visual_principles": {
                    "composition": "Geometric fragmentation with multiple viewpoints",
                    "lighting": "Even, neutral lighting without strong shadows",
                    "color": "Limited, monochromatic with earth tones",
                    "texture": "Flattened, geometric with minimal surface variation",
                    "space": "Flattened, with multiple overlapping planes"
                },
                "color_palette": ["#8B4513", "#A0522D", "#CD853F", "#DEB887", "#F5DEB3", "#D2B48C"],
                "composition_style": "Geometric, analytical, with emphasis on form and structure",
                "emotional_qualities": ["Intellectual", "Analytical", "Serene", "Geometric", "Constructive"]
            },
            "pop_art": {
                "name": "Pop Art",
                "characteristics": [
                    "Popular culture imagery",
                    "Bold, flat colors",
                    "Commercial art techniques",
                    "Repetition and mechanical reproduction",
                    "Celebration of mass media",
                    "Irony and social commentary"
                ],
                "key_artists": ["Warhol", "Lichtenstein", "Hamilton", "Rauschenberg", "Oldenburg"],
                "historical_period": "1950s-1960s",
                "visual_principles": {
                    "composition": "Repetitive patterns, grid systems, commercial layouts",
                    "lighting": "Even, commercial lighting with sharp contrasts",
                    "color": "Bold primaries, commercial colors, high saturation",
                    "texture": "Print-like, mechanical reproduction quality",
                    "space": "Flat, commercial poster space with clear hierarchy"
                },
                "color_palette": ["#FF0000", "#0000FF", "#FFFF00", "#00FF00", "#FFA500", "#FF1493"],
                "composition_style": "Commercial, repetitive, with emphasis on mass media aesthetics",
                "emotional_qualities": ["Playful", "Ironic", "Commercial", "Bold", "Accessible"]
            },
            "romanticism": {
                "name": "Romanticism",
                "characteristics": [
                    "Emphasis on emotion and individualism",
                    "Nature and the sublime",
                    "Medieval and exotic subjects",
                    "Dramatic lighting and composition",
                    "Personal expression over reason",
                    "Revolt against industrialization"
                ],
                "key_artists": ["Delacroix", "Goya", "Turner", "Friedrich", "Blake"],
                "historical_period": "1800-1850",
                "visual_principles": {
                    "composition": "Dramatic diagonals, powerful contrasts, emotional staging",
                    "lighting": "Dramatic chiaroscuro with strong atmospheric effects",
                    "color": "Deep, saturated colors with emotional symbolism",
                    "texture": "Varied, from smooth to heavily painterly",
                    "space": "Deep, atmospheric with emphasis on scale and drama"
                },
                "color_palette": ["#2F4F4F", "#8B4513", "#800080", "#DC143C", "#006400", "#4682B4"],
                "composition_style": "Dramatic, emotional, with emphasis on nature and the sublime",
                "emotional_qualities": ["Passionate", "Mysterious", "Sublime", "Individual", "Rebellious"]
            },
            "renaissance": {
                "name": "Renaissance",
                "characteristics": [
                    "Return to classical antiquity",
                    "Mathematical proportions and perspective",
                    "Humanism and anatomical accuracy",
                    "Balanced and harmonious compositions",
                    "Oil painting techniques",
                    "Scientific approach to art"
                ],
                "key_artists": ["Leonardo", "Michelangelo", "Raphael", "Titian", "Botticelli"],
                "historical_period": "1400-1600",
                "visual_principles": {
                    "composition": "Pyramidal arrangements, mathematical proportions, linear perspective",
                    "lighting": "Soft, natural lighting with subtle modeling",
                    "color": "Harmonious, naturalistic with rich earth tones",
                    "texture": "Smooth, refined surfaces with subtle detail",
                    "space": "Linear perspective with clear depth and hierarchy"
                },
                "color_palette": ["#8B4513", "#CD853F", "#A0522D", "#D2691E", "#F4A460", "#DEB887"],
                "composition_style": "Balanced, harmonious, with emphasis on proportion and perspective",
                "emotional_qualities": ["Noble", "Harmonious", "Balanced", "Refined", "Classical"]
            },
            "art_nouveau": {
                "name": "Art Nouveau",
                "characteristics": [
                    "Organic, flowing lines",
                    "Nature-inspired motifs",
                    "Integration of art and design",
                    "Curved, asymmetrical forms",
                    "Decorative and functional unity",
                    "Rejection of historical styles"
                ],
                "key_artists": ["Mucha", "Hector Guimard", "Charles Rennie Mackintosh", "Antoni Gaudi", "Alphonse Mucha"],
                "historical_period": "1890-1910",
                "visual_principles": {
                    "composition": "Flowing, organic arrangements with asymmetrical balance",
                    "lighting": "Soft, diffused with organic light sources",
                    "color": "Elegant pastels, jewel tones, natural color harmonies",
                    "texture": "Decorative surfaces with fine detail and ornament",
                    "space": "Integrated, flowing with organic boundaries"
                },
                "color_palette": ["#DDA0DD", "#98FB98", "#F0E68C", "#FFB6C1", "#87CEEB", "#F5DEB3"],
                "composition_style": "Organic, flowing, with emphasis on natural forms and decoration",
                "emotional_qualities": ["Elegant", "Organic", "Decorative", "Natural", "Refined"]
            }
        }
    
    def get_movement(self, name: str) -> Optional[Dict[str, Any]]:
        """Get artistic movement by name (case-insensitive)"""
        name = name.lower().strip()
        return self.movements.get(name)
    
    def get_all_movements(self) -> List[str]:
        """Get list of all available artistic movements"""
        return list(self.movements.keys())
    
    def analyze_movement_characteristics(self, movement_name: str) -> Dict[str, Any]:
        """Analyze and extract key characteristics of a movement"""
        movement = self.get_movement(movement_name)
        if not movement:
            return {}
        
        return {
            "core_principles": movement["visual_principles"],
            "color_approach": movement["color_palette"],
            "composition_style": movement["composition_style"],
            "emotional_qualities": movement["emotional_qualities"],
            "historical_context": movement["historical_period"],
            "key_characteristics": movement["characteristics"]
        }

class DirectionalStimulusPrompter:
    """Advanced DSP (Directional-Stimulus Prompting) for artistic fusion"""
    
    def __init__(self):
        self.fusion_strategies = {
            "balanced": self._balanced_fusion,
            "dominant": self._dominant_fusion,
            "harmonic": self._harmonic_fusion,
            "contrast": self._contrast_fusion,
            "symbiotic": self._symbiotic_fusion
        }
    
    def generate_fusion_prompt(self, movement_1: str, movement_2: str, 
                             intensity: float = 0.5, target_emotion: str = "balanced") -> Dict[str, Any]:
        """Generate a comprehensive fusion prompt using DSP methodology"""
        
        # Get movement characteristics
        db = ArtisticMovementDatabase()
        m1_data = db.get_movement(movement_1)
        m2_data = db.get_movement(movement_2)
        
        if not m1_data or not m2_data:
            raise HTTPException(status_code=400, detail="One or both artistic movements not recognized")
        
        # Apply DSP fusion algorithm
        fusion_result = self._apply_dsp_fusion(m1_data, m2_data, intensity, target_emotion)
        
        return fusion_result
    
    def _apply_dsp_fusion(self, m1_data: Dict, m2_data: Dict, intensity: float, target_emotion: str) -> Dict[str, Any]:
        """Apply Directional-Stimulus Prompting algorithm"""
        
        # Extract core elements from both movements
        fusion_elements = {
            "visual_synthesis": self._synthesize_visual_elements(m1_data, m2_data, intensity),
            "color_harmonization": self._harmonize_colors(m1_data, m2_data, intensity),
            "composition_fusion": self._fuse_compositions(m1_data, m2_data, intensity),
            "emotional_synthesis": self._synthesize_emotions(m1_data, m2_data, target_emotion),
            "technical_fusion": self._fuse_technical_aspects(m1_data, m2_data, intensity)
        }
        
        # Generate the final prompt
        final_prompt = self._generate_final_prompt(fusion_elements, intensity)
        
        return {
            "fusion_elements": fusion_elements,
            "final_prompt": final_prompt,
            "fusion_analysis": self._analyze_fusion_quality(fusion_elements),
            "technical_specifications": self._generate_technical_specs(fusion_elements)
        }
    
    def _synthesize_visual_elements(self, m1: Dict, m2: Dict, intensity: float) -> Dict[str, Any]:
        """Synthesize visual elements from both movements"""
        
        # Extract visual principles
        m1_principles = m1["visual_principles"]
        m2_principles = m2["visual_principles"]
        
        synthesis = {}
        
        # Composition fusion
        m1_comp = m1_principles.get("composition", "")
        m2_comp = m2_principles.get("composition", "")
        
        if intensity > 0.7:
            # High fusion - prioritize second movement
            synthesis["composition"] = f"{m2_comp} with influences from {m1_comp}"
        elif intensity < 0.3:
            # Low fusion - prioritize first movement
            synthesis["composition"] = f"{m1_comp} with influences from {m2_comp}"
        else:
            # Balanced fusion
            synthesis["composition"] = f"Fusion of {m1_comp} and {m2_comp}"
        
        # Lighting synthesis
        m1_light = m1_principles.get("lighting", "")
        m2_light = m2_principles.get("lighting", "")
        
        synthesis["lighting"] = self._merge_lighting_approaches(m1_light, m2_light, intensity)
        
        # Texture synthesis
        m1_texture = m1_principles.get("texture", "")
        m2_texture = m2_principles.get("texture", "")
        
        synthesis["texture"] = self._merge_texture_approaches(m1_texture, m2_texture, intensity)
        
        return synthesis
    
    def _harmonize_colors(self, m1: Dict, m2: Dict, intensity: float) -> Dict[str, Any]:
        """Create harmonized color palette from both movements"""
        
        m1_colors = m1["color_palette"]
        m2_colors = m2["color_palette"]
        
        # Create fusion palette
        if intensity > 0.7:
            # Second movement dominant
            dominant_colors = m2_colors
            accent_colors = m1_colors[:3]
        elif intensity < 0.3:
            # First movement dominant
            dominant_colors = m1_colors
            accent_colors = m2_colors[:3]
        else:
            # Balanced fusion
            dominant_colors = m1_colors[:4] + m2_colors[:4]
            accent_colors = m1_colors[4:] + m2_colors[4:]
        
        return {
            "primary_palette": dominant_colors,
            "accent_palette": accent_colors,
            "fusion_strategy": self._determine_color_strategy(m1, m2, intensity),
            "harmonization_notes": self._generate_color_harmonization_notes(m1, m2)
        }
    
    def _fuse_compositions(self, m1: Dict, m2: Dict, intensity: float) -> Dict[str, Any]:
        """Merge composition approaches"""
        
        m1_style = m1["composition_style"]
        m2_style = m2["composition_style"]
        
        if "geometric" in m1_style and "organic" in m2_style:
            fusion_style = f"Geometric forms with organic flowing elements (balance: {intensity:.1f})"
        elif "dynamic" in m1_style and "static" in m2_style:
            fusion_style = f"Dynamic movement balanced with static stability (balance: {intensity:.1f})"
        elif "complex" in m1_style and "simple" in m2_style:
            fusion_style = f"Complex layered composition with simplified focal points (balance: {intensity:.1f})"
        else:
            fusion_style = f"Seamless blend of {m1_style} and {m2_style} (balance: {intensity:.1f})"
        
        return {
            "fusion_style": fusion_style,
            "dominant_approach": "movement_2" if intensity > 0.6 else "movement_1" if intensity < 0.4 else "balanced",
            "composition_principles": self._extract_composition_principles(m1, m2)
        }
    
    def _synthesize_emotions(self, m1: Dict, m2: Dict, target_emotion: str) -> Dict[str, Any]:
        """Synthesize emotional qualities from both movements"""
        
        m1_emotions = m1["emotional_qualities"]
        m2_emotions = m2["emotional_qualities"]
        
        # Create emotional synthesis based on target
        if target_emotion == "harmonious":
            overlapping = set(m1_emotions) & set(m2_emotions)
            synthesis_emotions = list(overlapping) + m1_emotions[:2] + m2_emotions[:2]
        elif target_emotion == "dramatic":
            synthesis_emotions = [em for em in (m1_emotions + m2_emotions) if em in ["dramatic", "intense", "passionate"]]
            if not synthesis_emotions:
                synthesis_emotions = m1_emotions[:3] + m2_emotions[:3]
        elif target_emotion == "serene":
            synthesis_emotions = [em for em in (m1_emotions + m2_emotions) if em in ["serene", "peaceful", "contemplative"]]
            if not synthesis_emotions:
                synthesis_emotions = m1_emotions[:2] + m2_emotions[:2]
        else:  # balanced
            synthesis_emotions = m1_emotions[:2] + m2_emotions[:2]
        
        return {
            "synthesized_emotions": synthesis_emotions[:6],
            "emotional_balance": self._analyze_emotional_balance(m1_emotions, m2_emotions),
            "target_alignment": target_emotion,
            "emotional_journey": self._map_emotional_journey(synthesis_emotions)
        }
    
    def _fuse_technical_aspects(self, m1: Dict, m2: Dict, intensity: float) -> Dict[str, Any]:
        """Merge technical and stylistic approaches"""
        
        # Extract technical characteristics
        m1_tech = {
            "brushwork": m1["characteristics"],
            "materials": self._infer_materials(m1),
            "techniques": self._infer_techniques(m1)
        }
        
        m2_tech = {
            "brushwork": m2["characteristics"],
            "materials": self._infer_materials(m2),
            "techniques": self._infer_techniques(m2)
        }
        
        fusion_tech = {
            "technique_fusion": self._merge_techniques(m1_tech, m2_tech, intensity),
            "material_harmonization": self._harmonize_materials(m1_tech, m2_tech),
            "stylistic_synthesis": self._synthesize_style(m1_tech, m2_tech)
        }
        
        return fusion_tech
    
    def _generate_final_prompt(self, fusion_elements: Dict, intensity: float) -> str:
        """Generate the final structured prompt for diffusion models"""
        
        visual = fusion_elements["visual_synthesis"]
        color = fusion_elements["color_harmonization"]
        composition = fusion_elements["composition_fusion"]
        emotion = fusion_elements["emotional_synthesis"]
        
        prompt = f"""Create an artwork that synthesizes two distinct artistic movements:
        
**VISUAL COMPOSITION**: {visual['composition']}
**LIGHTING APPROACH**: {visual['lighting']}
**TEXTURAL TREATMENT**: {visual['texture']}
**COLOR PALETTE**: {', '.join(color['primary_palette'])} with accents of {', '.join(color['accent_palette'])}
**COMPOSITIONAL STYLE**: {composition['fusion_style']}
**EMOTIONAL ATMOSPHERE**: Evoke {', '.join(emotion['synthesized_emotions'])}
**TECHNICAL APPROACH**: Use techniques that honor both movements while creating something new and innovative

**FUSION BALANCE**: {intensity:.1f} (0.0 = pure first movement, 1.0 = pure second movement)
**ARTISTIC VISION**: Create a piece that feels both familiar and revolutionary, drawing from the strengths of both movements while establishing its own unique identity."""
        
        return prompt
    
    def _analyze_fusion_quality(self, fusion_elements: Dict) -> Dict[str, Any]:
        """Analyze the quality and coherence of the fusion"""
        
        return {
            "coherence_score": 0.85,  # Simulated analysis score
            "innovation_level": "High",
            "aesthetic_balance": "Well-balanced fusion with clear artistic vision",
            "historical_accuracy": "Fuses movements in historically informed way",
            "technical_feasibility": "Technically achievable with appropriate skill level",
            "recommendations": [
                "Consider the interplay between dominant and subordinate elements",
                "Maintain clear visual hierarchy despite fusion complexity",
                "Ensure color harmony supports the emotional intent"
            ]
        }
    
    def _generate_technical_specs(self, fusion_elements: Dict) -> Dict[str, Any]:
        """Generate technical specifications for implementation"""
        
        return {
            "recommended_medium": "Digital painting or mixed media",
            "canvas_size": "Medium to large format for full impact",
            "color_temperature": "Warm with cool accents",
            "value_structure": "Full value range with emphasis on contrast",
            "edge_quality": "Mix of hard and soft edges for visual interest",
            "composition_focus": "Multiple focal points with clear hierarchy",
            "lighting_scheme": "Dramatic with atmospheric depth",
            "detail_level": "High detail in focal areas, simplified in supporting areas"
        }
    
    # Helper methods for specific fusion operations
    def _merge_lighting_approaches(self, light1: str, light2: str, intensity: float) -> str:
        """Merge lighting approaches from two movements"""
        if "chiaroscuro" in light1 and "even" in light2:
            return f"Chiaroscuro lighting ({intensity:.1f}) balanced with even illumination"
        elif "natural" in light1 and "dramatic" in light2:
            return f"Natural lighting with dramatic atmospheric effects"
        else:
            return f"Fusion of {light1} and {light2} approaches"
    
    def _merge_texture_approaches(self, tex1: str, tex2: str, intensity: float) -> str:
        """Merge texture approaches from two movements"""
        if "smooth" in tex1 and "textured" in tex2:
            return f"Smooth surfaces with textured accent areas"
        elif "industrial" in tex1 and "organic" in tex2:
            return f"Industrial materials with organic textural elements"
        else:
            return f"Blended textural approach combining {tex1} and {tex2}"
    
    def _determine_color_strategy(self, m1: Dict, m2: Dict, intensity: float) -> str:
        """Determine the best color harmonization strategy"""
        if intensity > 0.7:
            return "Secondary movement dominant with primary movement accents"
        elif intensity < 0.3:
            return "Primary movement dominant with secondary movement accents"
        else:
            return "Balanced fusion with equal weight to both movements"
    
    def _generate_color_harmonization_notes(self, m1: Dict, m2: Dict) -> str:
        """Generate notes for color harmonization"""
        return f"Create harmony between {m1['name']} color traditions and {m2['name']} palette preferences"
    
    def _extract_composition_principles(self, m1: Dict, m2: Dict) -> List[str]:
        """Extract key composition principles from both movements"""
        principles = []
        
        m1_style = m1["composition_style"]
        m2_style = m2["composition_style"]
        
        if "geometric" in m1_style or "geometric" in m2_style:
            principles.append("Use geometric structural elements")
        if "dynamic" in m1_style or "dynamic" in m2_style:
            principles.append("Incorporate dynamic movement and energy")
        if "balanced" in m1_style or "balanced" in m2_style:
            principles.append("Maintain visual balance and harmony")
        
        return principles
    
    def _analyze_emotional_balance(self, emotions1: List[str], emotions2: List[str]) -> str:
        """Analyze the emotional balance between movements"""
        common = set(emotions1) & set(emotions2)
        if len(common) > 2:
            return "Strong emotional compatibility"
        elif len(common) > 0:
            return "Moderate emotional compatibility with complementary differences"
        else:
            return "Contrasting emotional qualities that create dynamic tension"
    
    def _map_emotional_journey(self, emotions: List[str]) -> str:
        """Map the emotional journey through the artwork"""
        if len(emotions) >= 3:
            return f"Emotional progression from {emotions[0]} through {emotions[1]} to {emotions[2]}"
        else:
            return f"Predominant emotional tone: {', '.join(emotions)}"
    
    def _infer_materials(self, movement: Dict) -> List[str]:
        """Infer typical materials used in a movement"""
        characteristics = movement["characteristics"]
        materials = []
        
        if "industrial" in str(characteristics):
            materials.extend(["metal", "glass", "concrete"])
        if "oil" in str(characteristics):
            materials.extend(["oil paint", "canvas"])
        if "digital" in str(characteristics):
            materials.extend(["digital medium", "屏幕"])
        
        return materials or ["traditional art materials"]
    
    def _infer_techniques(self, movement: Dict) -> List[str]:
        """Infer typical techniques used in a movement"""
        characteristics = movement["characteristics"]
        techniques = []
        
        if "loose brushwork" in str(characteristics):
            techniques.append("loose brushwork")
        if "geometric" in str(characteristics):
            techniques.append("geometric construction")
        if "texture" in str(characteristics):
            techniques.append("surface texture")
        
        return techniques or ["traditional painting techniques"]
    
    def _merge_techniques(self, tech1: Dict, tech2: Dict, intensity: float) -> str:
        """Merge techniques from two movements"""
        techniques = tech1["techniques"] + tech2["techniques"]
        return f"Integrated techniques: {', '.join(techniques[:5])}"
    
    def _harmonize_materials(self, tech1: Dict, tech2: Dict) -> str:
        """Harmonize materials from two movements"""
        materials = list(set(tech1["materials"] + tech2["materials"]))
        return f"Harmonized materials: {', '.join(materials[:6])}"
    
    def _synthesize_style(self, tech1: Dict, tech2: Dict) -> str:
        """Synthesize style approaches"""
        return "Unified stylistic approach that respects both traditions while innovating"

class DatabaseManager:
    """Database operations for storing fusion projects"""
    
    def __init__(self):
        self.db_path = "algorithmic_art_fusion.db"
    
    def save_project(self, movement_1: str, movement_2: str, result: FusionResult, 
                    project_name: str = "", style_preferences: List[str] = None) -> str:
        """Save fusion project to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO fusion_projects 
                (id, movement_1, movement_2, generated_prompt, artistic_elements, fusion_analysis, project_name, style_preferences)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.project_id,
                movement_1,
                movement_2,
                result.generated_prompt,
                json.dumps(result.artistic_elements),
                json.dumps(result.fusion_analysis),
                project_name,
                json.dumps(style_preferences or [])
            ))
            
            conn.commit()
            return result.project_id
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve fusion project from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, movement_1, movement_2, generated_prompt, artistic_elements, fusion_analysis, 
                       project_timestamp, project_name, style_preferences
                FROM fusion_projects
                WHERE id = ?
            ''', (project_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                "project_id": row[0],
                "movement_1": row[1],
                "movement_2": row[2],
                "generated_prompt": row[3],
                "artistic_elements": json.loads(row[4]),
                "fusion_analysis": json.loads(row[5]),
                "timestamp": row[6],
                "project_name": row[7],
                "style_preferences": json.loads(row[8]) if row[8] else []
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()

# Initialize components
movement_database = ArtisticMovementDatabase()
dsp_generator = DirectionalStimulusPrompter()
db_manager = DatabaseManager()

# API Endpoints
@app.post("/api/v1/process", response_model=FusionResult)
async def process_art_fusion(request: AnalysisRequest, user: dict = Depends(verify_token)):
    """
    Main endpoint for artistic movement fusion
    
    Args:
        request: Contains user_input (movement names and parameters)
        user: Authenticated user object
    
    Returns:
        FusionResult with generated prompt and analysis
    """
    try:
        # Generate project ID
        project_id = str(uuid.uuid4())
        
        # For this template, we expect movement names in user_input
        # Format: "movement1,movement2,intensity,target_emotion"
        parts = request.user_input.split(',')
        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="Please specify at least two artistic movements")
        
        movement_1 = parts[0].strip()
        movement_2 = parts[1].strip()
        intensity = float(parts[2]) if len(parts) > 2 and parts[2].strip() else 0.5
        target_emotion = parts[3].strip() if len(parts) > 3 else "balanced"
        
        # Generate fusion using DSP
        fusion_result = dsp_generator.generate_fusion_prompt(movement_1, movement_2, intensity, target_emotion)
        
        # Create final result
        result = FusionResult(
            project_id=project_id,
            generated_prompt=fusion_result["final_prompt"],
            artistic_elements=fusion_result["fusion_elements"],
            fusion_analysis=fusion_result["fusion_analysis"],
            movement_analysis={
                "movement_1": movement_database.analyze_movement_characteristics(movement_1),
                "movement_2": movement_database.analyze_movement_characteristics(movement_2)
            },
            visual_principles=fusion_result["fusion_elements"]["visual_synthesis"],
            emotional_synthesis=fusion_result["fusion_elements"]["emotional_synthesis"]["synthesized_emotions"],
            technical_specifications=fusion_result["technical_specifications"],
            timestamp=datetime.now().isoformat()
        )
        
        # Save to database
        db_manager.save_project(movement_1, movement_2, result, request.context_file)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fusion generation failed: {str(e)}")

@app.post("/api/v1/fusion", response_model=FusionResult)
async def create_artistic_fusion(request: ArtFusionRequest, user: dict = Depends(verify_token)):
    """
    Create artistic movement fusion with detailed parameters
    
    Args:
        request: Contains movement names, fusion intensity, and preferences
        user: Authenticated user object
    
    Returns:
        FusionResult with comprehensive fusion analysis
    """
    try:
        # Generate project ID
        project_id = str(uuid.uuid4())
        
        # Validate movements
        m1_data = movement_database.get_movement(request.movement_1)
        m2_data = movement_database.get_movement(request.movement_2)
        
        if not m1_data or not m2_data:
            available = ", ".join(movement_database.get_all_movements())
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown movement(s). Available movements: {available}"
            )
        
        # Generate fusion using DSP
        fusion_result = dsp_generator.generate_fusion_prompt(
            request.movement_1, 
            request.movement_2, 
            request.fusion_intensity, 
            request.target_emotion
        )
        
        # Create final result
        result = FusionResult(
            project_id=project_id,
            generated_prompt=fusion_result["final_prompt"],
            artistic_elements=fusion_result["fusion_elements"],
            fusion_analysis=fusion_result["fusion_analysis"],
            movement_analysis={
                "movement_1": movement_database.analyze_movement_characteristics(request.movement_1),
                "movement_2": movement_database.analyze_movement_characteristics(request.movement_2)
            },
            visual_principles=fusion_result["fusion_elements"]["visual_synthesis"],
            emotional_synthesis=fusion_result["fusion_elements"]["emotional_synthesis"]["synthesized_emotions"],
            technical_specifications=fusion_result["technical_specifications"],
            timestamp=datetime.now().isoformat()
        )
        
        # Save to database
        db_manager.save_project(
            request.movement_1, 
            request.movement_2, 
            result, 
            style_preferences=request.style_preferences
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fusion creation failed: {str(e)}")

@app.get("/api/v1/movements")
async def get_available_movements(user: dict = Depends(verify_token)):
    """
    Get list of available artistic movements
    
    Args:
        user: Authenticated user object
    
    Returns:
        List of artistic movements with basic information
    """
    movements = []
    for name, data in movement_database.movements.items():
        movements.append({
            "name": data["name"],
            "period": data["historical_period"],
            "key_artists": data["key_artists"][:3],  # First 3 artists
            "primary_emotions": data["emotional_qualities"][:3],
            "color_characteristics": len(data["color_palette"]),
            "description": f"{data['name']} art movement from {data['historical_period']}"
        })
    
    return {
        "available_movements": movements,
        "total_count": len(movements),
        "categories": {
            "classical": ["renaissance", "baroque", "romanticism"],
            "modern": ["impressionism", "expressionism", "cubism"],
            "contemporary": ["minimalism", "pop_art", "surrealism"],
            "decorative": ["art_nouveau"]
        }
    }

@app.get("/api/v1/movement/{movement_name}")
async def get_movement_details(movement_name: str, user: dict = Depends(verify_token)):
    """
    Get detailed information about a specific artistic movement
    
    Args:
        movement_name: Name of the artistic movement
        user: Authenticated user object
    
    Returns:
        Detailed movement analysis
    """
    movement = movement_database.get_movement(movement_name)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    return movement_database.analyze_movement_characteristics(movement_name)

@app.get("/api/v1/project/{project_id}", response_model=FusionResult)
async def get_fusion_project(project_id: str, user: dict = Depends(verify_token)):
    """
    Retrieve stored fusion project
    
    Args:
        project_id: Unique project identifier
        user: Authenticated user object
    
    Returns:
        FusionResult
    """
    result = db_manager.get_project(project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Convert to FusionResult format
    return FusionResult(
        project_id=result["project_id"],
        generated_prompt=result["generated_prompt"],
        artistic_elements=result["artistic_elements"],
        fusion_analysis=result["fusion_analysis"],
        movement_analysis={
            "movement_1": movement_database.analyze_movement_characteristics(result["movement_1"]),
            "movement_2": movement_database.analyze_movement_characteristics(result["movement_2"])
        },
        visual_principles={},  # This would be reconstructed from stored data
        emotional_synthesis="",
        technical_specifications={},
        timestamp=result["timestamp"]
    )

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Algorithmic Art Fusion", "version": "1.0.0"}

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
