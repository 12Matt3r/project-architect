#!/usr/bin/env python3
"""
Template #35: Virtual E-Commerce Agent

A sophisticated e-commerce platform that executes ReAct cycles for complex product queries.
Implements: Thought -> Action -> Observation -> Answer workflow for intelligent product recommendations.

Author: MiniMax Agent
Date: 2025-11-17
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import uuid
import sqlite3
from contextlib import contextmanager
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class Product(BaseModel):
    id: str
    name: str
    category: str
    brand: str
    price: float
    description: str
    features: List[str]
    specifications: Dict[str, Any]
    ratings: float
    review_count: int
    image_url: str
    in_stock: bool
    tags: List[str]

class CustomerQuery(BaseModel):
    query: str = Field(..., description="Customer's product search query")
    session_id: Optional[str] = Field(None, description="Session identifier for tracking")

class ReActStep(BaseModel):
    step_type: str  # "Thought", "Action", "Observation", "Answer"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ReActCycle(BaseModel):
    query: str
    steps: List[ReActStep]
    final_recommendation: str
    confidence_score: float
    session_id: str
    timestamp: datetime

class ProductRecommendation(BaseModel):
    product: Product
    match_score: float
    reasoning: str
    key_features: List[str]

class QueryResponse(BaseModel):
    session_id: str
    react_cycle: ReActCycle
    recommendations: List[ProductRecommendation]
    analysis_summary: str

# Dataclasses for internal processing
@dataclass
class CustomerNeeds:
    requirements: List[str]
    preferences: Dict[str, Any]
    constraints: List[str]
    priority_order: List[str]

@dataclass
class CatalogFilter:
    category_filters: List[str]
    brand_preferences: List[str]
    price_range: tuple
    feature_requirements: List[str]
    availability_filter: bool

@dataclass
class SearchObservation:
    total_products_found: int
    filtered_products: List[Product]
    filter_applied: Dict[str, Any]
    reasoning: str

# Initialize FastAPI app
app = FastAPI(
    title="Virtual E-Commerce Agent",
    description="AI-powered e-commerce platform with ReAct-based product recommendations",
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

# Initialize product database
PRODUCT_CATALOG = {
    "running_shoes": [
        {
            "id": "rs001",
            "name": "Nike ZoomX Vaporfly Next% 3",
            "category": "Running Shoes",
            "brand": "Nike",
            "price": 249.99,
            "description": "Elite racing shoe with carbon plate for marathon performance",
            "features": ["Carbon fiber plate", "ZoomX foam", "Lightweight", "High energy return"],
            "specifications": {
                "weight": "185g (US M9)",
                "stack_height": "36mm/28mm",
                "drop": "8mm",
                "plate": "Carbon fiber",
                "terrain": "Road"
            },
            "ratings": 4.8,
            "review_count": 1247,
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "in_stock": True,
            "tags": ["marathon", "racing", "lightweight", "carbon-plate"]
        },
        {
            "id": "rs002",
            "name": "ASICS Metaspeed Sky+",
            "category": "Running Shoes",
            "brand": "ASICS",
            "price": 229.99,
            "description": "Speed-focused running shoe with organic curve carbon plate",
            "features": ["Carbon plate", "FF BLAST+ ECO foam", "Organic curved design", "Responsive ride"],
            "specifications": {
                "weight": "190g (US M9)",
                "stack_height": "35mm/28mm",
                "drop": "7mm",
                "plate": "Carbon fiber",
                "terrain": "Road"
            },
            "ratings": 4.7,
            "review_count": 892,
            "image_url": "https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=400",
            "in_stock": True,
            "tags": ["marathon", "racing", "responsive", "stability"]
        },
        {
            "id": "rs003",
            "name": "Brooks Ghost 15",
            "category": "Running Shoes",
            "brand": "Brooks",
            "price": 129.99,
            "description": "Comfortable daily trainer with excellent arch support",
            "features": ["DNA Loft cushioning", "Soft landings", "Breathable upper", "Durable outsole"],
            "specifications": {
                "weight": "280g (US M9)",
                "stack_height": "32mm/24mm",
                "drop": "8mm",
                "plate": "None",
                "terrain": "Road"
            },
            "ratings": 4.6,
            "review_count": 2145,
            "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400",
            "in_stock": True,
            "tags": ["daily-training", "comfort", "arch-support", "durable"]
        },
        {
            "id": "rs004",
            "name": "New Balance Fresh Foam X 1080 v12",
            "category": "Running Shoes",
            "brand": "New Balance",
            "price": 159.99,
            "description": "Premium cushioning with excellent high-arch support",
            "features": ["Fresh Foam X midsole", "High arch support", "Flexible ride", "Premium materials"],
            "specifications": {
                "weight": "290g (US M9)",
                "stack_height": "34mm/26mm",
                "drop": "8mm",
                "plate": "None",
                "terrain": "Road"
            },
            "ratings": 4.5,
            "review_count": 1673,
            "image_url": "https://images.unsplash.com/photo-1560072810-82194044694e?w=400",
            "in_stock": True,
            "tags": ["high-arch", "cushioning", "premium", "comfortable"]
        },
        {
            "id": "rs005",
            "name": "Adidas Adizero Adios Pro 3",
            "category": "Running Shoes",
            "brand": "Adidas",
            "price": 219.99,
            "description": "Elite marathon shoe with carbon plates and Lightstrike Pro foam",
            "features": ["Dual carbon plates", "Lightstrike Pro foam", "Energy return", "Lightweight design"],
            "specifications": {
                "weight": "195g (US M9)",
                "stack_height": "39mm/31mm",
                "drop": "8mm",
                "plate": "Dual carbon",
                "terrain": "Road"
            },
            "ratings": 4.7,
            "review_count": 743,
            "image_url": "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=400",
            "in_stock": True,
            "tags": ["marathon", "elite", "energy-return", "lightweight"]
        },
        {
            "id": "rs006",
            "name": "HOKA Clifton 9",
            "category": "Running Shoes",
            "brand": "HOKA",
            "price": 139.99,
            "description": "Maximal cushioning with rockered geometry for easy running",
            "features": ["High cushioning", "Rocker geometry", "Lightweight despite stack", "Comfortable upper"],
            "specifications": {
                "weight": "275g (US M9)",
                "stack_height": "37mm/29mm",
                "drop": "8mm",
                "plate": "None",
                "terrain": "Road"
            },
            "ratings": 4.4,
            "review_count": 1821,
            "image_url": "https://images.unsplash.com/photo-1595341888016-a392ef81b7de?w=400",
            "in_stock": True,
            "tags": ["maximal-cushioning", "comfortable", "daily-training", "rocker"]
        }
    ],
    "casual_shoes": [
        {
            "id": "cs001",
            "name": "Nike Air Max 270",
            "category": "Casual Shoes",
            "brand": "Nike",
            "price": 149.99,
            "description": "Lifestyle sneaker with large Air unit for comfort",
            "features": ["Large Air Max unit", "Comfortable fit", "Stylish design", "Breathable"],
            "specifications": {
                "weight": "320g",
                "style": "Lifestyle",
                "upper": "Mesh and synthetic",
                "outsole": "Rubber"
            },
            "ratings": 4.3,
            "review_count": 567,
            "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
            "in_stock": True,
            "tags": ["lifestyle", "comfortable", "stylish"]
        }
    ],
    "basketball_shoes": [
        {
            "id": "bs001",
            "name": "Nike LeBron XXI",
            "category": "Basketball Shoes",
            "brand": "Nike",
            "price": 199.99,
            "description": "High-performance basketball shoe for explosive plays",
            "features": ["Air Zoom units", "Cushlon foam", "Traction pattern", "Supportive upper"],
            "specifications": {
                "weight": "410g",
                "sport": "Basketball",
                "ankle_support": "High",
                "traction": "Excellent"
            },
            "ratings": 4.6,
            "review_count": 432,
            "image_url": "https://images.unsplash.com/photo-1582233479366-6d38bc3a6fa7?w=400",
            "in_stock": True,
            "tags": ["basketball", "performance", "ankle-support"]
        }
    ]
}

class ReActEngine:
    """Core ReAct cycle engine for e-commerce query processing"""
    
    def __init__(self):
        self.session_data = {}
        
    async def process_customer_query(self, query: str, session_id: str) -> QueryResponse:
        """Execute full ReAct cycle for customer query"""
        
        # Step 1: Thought - Analyze customer needs
        customer_needs = await self._analyze_customer_needs(query)
        
        thought_step = ReActStep(
            step_type="Thought",
            content=f"Analyzed customer needs from query: '{query}'. Identified requirements: {customer_needs.requirements}, preferences: {customer_needs.preferences}, constraints: {customer_needs.constraints}",
            timestamp=datetime.now(),
            metadata={
                "requirements": customer_needs.requirements,
                "preferences": customer_needs.preferences,
                "constraints": customer_needs.constraints
            }
        )
        
        # Step 2: Action - Filter catalog
        catalog_filter = self._create_catalog_filter(customer_needs)
        
        action_step = ReActStep(
            step_type="Action",
            content=f"Applied catalog filters: categories={catalog_filter.category_filters}, price range={catalog_filter.price_range}, feature requirements={catalog_filter.feature_requirements}",
            timestamp=datetime.now(),
            metadata=asdict(catalog_filter)
        )
        
        # Step 3: Observation - Get filtered results
        observation_result = await self._observe_catalog_results(catalog_filter)
        
        observation_step = ReActStep(
            step_type="Observation",
            content=f"Found {observation_result.total_products_found} products matching criteria. Applied filters: {observation_result.filter_applied}. Top matches identified.",
            timestamp=datetime.now(),
            metadata=asdict(observation_result)
        )
        
        # Step 4: Answer - Provide final recommendation
        recommendations = await self._generate_recommendations(observation_result, customer_needs)
        
        final_recommendation = self._create_final_recommendation(recommendations)
        
        answer_step = ReActStep(
            step_type="Answer",
            content=final_recommendation,
            timestamp=datetime.now(),
            metadata={
                "recommendations_count": len(recommendations),
                "confidence_score": recommendations[0].match_score if recommendations else 0.0
            }
        )
        
        # Assemble complete ReAct cycle
        react_cycle = ReActCycle(
            query=query,
            steps=[thought_step, action_step, observation_step, answer_step],
            final_recommendation=final_recommendation,
            confidence_score=recommendations[0].match_score if recommendations else 0.0,
            session_id=session_id,
            timestamp=datetime.now()
        )
        
        # Generate analysis summary
        analysis_summary = self._generate_analysis_summary(customer_needs, observation_result, recommendations)
        
        response = QueryResponse(
            session_id=session_id,
            react_cycle=react_cycle,
            recommendations=recommendations,
            analysis_summary=analysis_summary
        )
        
        # Store in session
        self.session_data[session_id] = response
        
        return response
    
    async def _analyze_customer_needs(self, query: str) -> CustomerNeeds:
        """Analyze customer query to extract needs, preferences, and constraints"""
        query_lower = query.lower()
        
        # Extract requirements
        requirements = []
        if "marathon" in query_lower:
            requirements.append("marathon_running")
        if "running" in query_lower:
            requirements.append("running_shoes")
        if "high arches" in query_lower or "arch support" in query_lower:
            requirements.append("arch_support")
        if "comfortable" in query_lower:
            requirements.append("comfort")
        if "lightweight" in query_lower:
            requirements.append("lightweight")
        if "racing" in query_lower:
            requirements.append("performance")
        
        # Extract preferences
        preferences = {}
        if "best" in query_lower or "top" in query_lower:
            preferences["quality_priority"] = "high"
        if "budget" in query_lower or "affordable" in query_lower:
            preferences["price_sensitivity"] = "high"
        
        # Extract constraints
        constraints = []
        if "under" in query_lower:
            # Extract price constraints if mentioned
            import re
            price_match = re.search(r'under\s+\$(\d+)', query_lower)
            if price_match:
                constraints.append(f"max_price_{price_match.group(1)}")
        
        # Determine priority order
        priority_order = ["marathon_running", "arch_support", "comfort", "lightweight"]
        
        return CustomerNeeds(
            requirements=requirements,
            preferences=preferences,
            constraints=constraints,
            priority_order=priority_order
        )
    
    def _create_catalog_filter(self, needs: CustomerNeeds) -> CatalogFilter:
        """Create catalog filter based on customer needs"""
        
        category_filters = []
        if "running_shoes" in needs.requirements:
            category_filters.append("Running Shoes")
        
        brand_preferences = []
        # Premium brands for marathon needs
        if "marathon_running" in needs.requirements:
            brand_preferences.extend(["Nike", "ASICS", "Brooks", "Adidas", "New Balance", "HOKA"])
        
        price_range = (0, 300)  # Default range
        
        feature_requirements = []
        if "arch_support" in needs.requirements:
            feature_requirements.append("arch_support")
        if "marathon_running" in needs.requirements:
            feature_requirements.extend(["carbon-plate", "lightweight", "high-cushioning"])
        if "comfort" in needs.requirements:
            feature_requirements.append("cushioning")
        
        return CatalogFilter(
            category_filters=category_filters,
            brand_preferences=brand_preferences,
            price_range=price_range,
            feature_requirements=feature_requirements,
            availability_filter=True
        )
    
    async def _observe_catalog_results(self, catalog_filter: CatalogFilter) -> SearchObservation:
        """Observe and filter catalog results"""
        
        all_products = []
        for category_products in PRODUCT_CATALOG.values():
            all_products.extend(category_products)
        
        # Apply filters
        filtered_products = []
        for product in all_products:
            # Category filter
            if catalog_filter.category_filters and product["category"] not in catalog_filter.category_filters:
                continue
            
            # Brand preference filter
            if catalog_filter.brand_preferences and product["brand"] not in catalog_filter.brand_preferences:
                continue
            
            # Price range filter
            if not (catalog_filter.price_range[0] <= product["price"] <= catalog_filter.price_range[1]):
                continue
            
            # Availability filter
            if catalog_filter.availability_filter and not product["in_stock"]:
                continue
            
            # Feature requirements filter
            if catalog_filter.feature_requirements:
                product_features = [f.lower() for f in product["features"]]
                product_tags = [t.lower() for t in product["tags"]]
                all_product_info = product_features + product_tags
                
                requirements_met = 0
                for requirement in catalog_filter.feature_requirements:
                    if any(requirement.lower() in info for info in all_product_info):
                        requirements_met += 1
                
                # Product must meet at least 50% of feature requirements
                if requirements_met < len(catalog_filter.feature_requirements) * 0.5:
                    continue
            
            filtered_products.append(product)
        
        return SearchObservation(
            total_products_found=len(filtered_products),
            filtered_products=filtered_products,
            filter_applied={
                "categories": catalog_filter.category_filters,
                "brands": catalog_filter.brand_preferences,
                "price_range": catalog_filter.price_range,
                "feature_requirements": catalog_filter.feature_requirements
            },
            reasoning=f"Applied {len(catalog_filter.category_filters)} category filters, {len(catalog_filter.brand_preferences)} brand preferences, and {len(catalog_filter.feature_requirements)} feature requirements"
        )
    
    async def _generate_recommendations(self, observation: SearchObservation, needs: CustomerNeeds) -> List[ProductRecommendation]:
        """Generate ranked product recommendations"""
        
        recommendations = []
        
        for product_data in observation.filtered_products[:10]:  # Limit to top 10
            # Calculate match score
            match_score = self._calculate_match_score(product_data, needs)
            
            # Generate reasoning
            reasoning = self._generate_product_reasoning(product_data, needs)
            
            # Extract key features
            key_features = self._extract_key_features(product_data, needs)
            
            recommendation = ProductRecommendation(
                product=Product(**product_data),
                match_score=match_score,
                reasoning=reasoning,
                key_features=key_features
            )
            
            recommendations.append(recommendation)
        
        # Sort by match score (descending)
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        
        return recommendations[:3]  # Return top 3
    
    def _calculate_match_score(self, product: Dict[str, Any], needs: CustomerNeeds) -> float:
        """Calculate how well a product matches customer needs"""
        
        score = 0.0
        max_score = 0.0
        
        # Requirements weighting
        requirement_weight = 25.0
        max_score += requirement_weight * len(needs.requirements)
        
        for requirement in needs.requirements:
            if requirement == "marathon_running":
                # Check for marathon-specific features
                if any(tag in ["marathon", "racing", "carbon-plate", "elite"] for tag in product["tags"]):
                    score += requirement_weight
            elif requirement == "arch_support":
                # Check for arch support
                if any("arch" in feature.lower() or "support" in feature.lower() for feature in product["features"]):
                    score += requirement_weight
            elif requirement == "comfort":
                # Check for comfort features
                if any("cushion" in feature.lower() or "comfort" in feature.lower() for feature in product["features"]):
                    score += requirement_weight
            elif requirement == "lightweight":
                # Check weight
                weight_str = product["specifications"].get("weight", "300g")
                try:
                    weight_val = float(weight_str.split("g")[0].replace("(", ""))
                    if weight_val < 250:  # Lightweight threshold
                        score += requirement_weight
                except:
                    pass
        
        # Ratings weighting
        rating_score = (product["ratings"] - 3.0) * 5.0  # Normalize to 0-5 scale
        max_score += 10.0
        score += max(0, rating_score)
        
        # Review count weighting (popularity)
        review_score = min(product["review_count"] / 100, 10.0)  # Max 10 points
        max_score += 10.0
        score += review_score
        
        # Price reasonableness (not too expensive, not too cheap)
        if 100 <= product["price"] <= 250:
            price_score = 5.0
        elif 50 <= product["price"] <= 300:
            price_score = 3.0
        else:
            price_score = 1.0
        
        max_score += 5.0
        score += price_score
        
        # Calculate final score as percentage
        final_score = (score / max_score) * 100.0
        return min(final_score, 100.0)
    
    def _generate_product_reasoning(self, product: Dict[str, Any], needs: CustomerNeeds) -> str:
        """Generate reasoning for product recommendation"""
        
        reasons = []
        
        # Marathon-specific reasoning
        if "marathon_running" in needs.requirements:
            if "marathon" in product["tags"]:
                reasons.append(f"specifically designed for marathon racing")
            elif "racing" in product["tags"]:
                reasons.append(f"built for competitive racing performance")
            elif "carbon" in str(product["features"]).lower():
                reasons.append(f"features carbon plate technology for energy return")
        
        # Arch support reasoning
        if "arch_support" in needs.requirements:
            arch_features = [f for f in product["features"] if "arch" in f.lower() or "support" in f.lower()]
            if arch_features:
                reasons.append(f"provides excellent arch support with {arch_features[0]}")
        
        # General benefits
        if product["ratings"] >= 4.5:
            reasons.append(f"highly rated ({product['ratings']}/5.0) by {product['review_count']} customers")
        
        if product["price"] > 200:
            reasons.append(f"premium quality with advanced technology")
        elif product["price"] < 150:
            reasons.append(f"excellent value for money")
        
        return " | ".join(reasons) if reasons else "Suitable option matching your criteria"
    
    def _extract_key_features(self, product: Dict[str, Any], needs: CustomerNeeds) -> List[str]:
        """Extract key features relevant to customer needs"""
        
        key_features = []
        
        for feature in product["features"]:
            feature_lower = feature.lower()
            if any(req in feature_lower for req in ["cushion", "arch", "support", "carbon", "lightweight"]):
                key_features.append(feature)
        
        # Add top 3 most relevant specifications
        if "weight" in product["specifications"]:
            key_features.append(f"Weight: {product['specifications']['weight']}")
        
        if "stack_height" in product["specifications"]:
            key_features.append(f"Stack: {product['specifications']['stack_height']}")
        
        return key_features[:5]  # Limit to 5 features
    
    def _create_final_recommendation(self, recommendations: List[ProductRecommendation]) -> str:
        """Create final recommendation text"""
        
        if not recommendations:
            return "No products found matching your criteria. Please try adjusting your search or contact our support team."
        
        top_rec = recommendations[0]
        
        recommendation = f"""Based on your query, I recommend the **{top_rec.product.name}** by {top_rec.product.brand}.
        
{top_rec.reasoning}

Key benefits:
{chr(10).join(f"• {feature}" for feature in top_rec.key_features[:3])}

This shoe scored {top_rec.match_score:.1f}% match for your needs and is available for ${top_rec.product.price:.2f}."""
        
        return recommendation.strip()
    
    def _generate_analysis_summary(self, needs: CustomerNeeds, observation: SearchObservation, recommendations: List[ProductRecommendation]) -> str:
        """Generate summary of the analysis process"""
        
        summary = f"""Query Analysis Summary:

**Customer Needs Identified:**
• {len(needs.requirements)} primary requirements: {', '.join(needs.requirements)}
• {len(needs.preferences)} preferences considered
• {len(needs.constraints)} constraints applied

**Search Results:**
• {observation.total_products_found} products matched your criteria
• Filters applied: {observation.reasoning}

**Top Recommendations:**
"""
        
        for i, rec in enumerate(recommendations, 1):
            summary += f"{i}. {rec.product.name} - {rec.match_score:.1f}% match score\n"
        
        summary += f"\n**Confidence Level:** {recommendations[0].match_score:.1f}% (High)" if recommendations else "No matches found"
        
        return summary

# Initialize ReAct engine
react_engine = ReActEngine()

# Database for session management
class DatabaseManager:
    def __init__(self, db_path: str = "ecommerce_sessions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for session management"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    query TEXT,
                    response_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS product_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    product_id TEXT,
                    product_name TEXT,
                    match_score REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
    
    def save_session(self, session_id: str, query: str, response_data: Dict):
        """Save session data to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions (session_id, query, response_data) VALUES (?, ?, ?)",
                (session_id, query, json.dumps(response_data))
            )
    
    def get_session_history(self, limit: int = 10) -> List[Dict]:
        """Retrieve session history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT session_id, query, timestamp FROM sessions ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return [{"session_id": row[0], "query": row[1], "timestamp": row[2]} for row in cursor.fetchall()]

# Initialize database manager
db_manager = DatabaseManager()

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Virtual E-Commerce Agent API",
        "version": "1.0.0",
        "status": "operational",
        "react_cycle": "Thought → Action → Observation → Answer"
    }

@app.get("/api/v1/catalog")
async def get_catalog():
    """Get product catalog overview"""
    catalog_summary = {}
    for category, products in PRODUCT_CATALOG.items():
        catalog_summary[category] = {
            "count": len(products),
            "brands": list(set(p["brand"] for p in products)),
            "price_range": {
                "min": min(p["price"] for p in products),
                "max": max(p["price"] for p in products)
            }
        }
    
    return {
        "catalog": catalog_summary,
        "total_products": sum(len(products) for products in PRODUCT_CATALOG.values()),
        "categories": list(PRODUCT_CATALOG.keys())
    }

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_customer_query(query_request: CustomerQuery):
    """Process customer query through ReAct cycle"""
    
    try:
        # Generate session ID if not provided
        session_id = query_request.session_id or str(uuid.uuid4())
        
        # Process query through ReAct engine
        response = await react_engine.process_customer_query(query_request.query, session_id)
        
        # Save to database
        db_manager.save_session(session_id, query_request.query, response.dict())
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/sessions/history")
async def get_session_history(limit: int = 10):
    """Get session history"""
    try:
        history = db_manager.get_session_history(limit)
        return {
            "sessions": history,
            "total_sessions": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving session history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get specific session data"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute(
                "SELECT response_data FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            
            if row:
                response_data = json.loads(row[0])
                return response_data
            else:
                raise HTTPException(status_code=404, detail="Session not found")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/products/{product_id}")
async def get_product_details(product_id: str):
    """Get detailed product information"""
    
    try:
        # Search for product across all categories
        for category_products in PRODUCT_CATALOG.values():
            for product in category_products:
                if product["id"] == product_id:
                    return Product(**product)
        
        raise HTTPException(status_code=404, detail="Product not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/compare-products")
async def compare_products(product_ids: List[str]):
    """Compare multiple products side by side"""
    
    try:
        products = []
        for product_id in product_ids:
            # Search for product
            found = False
            for category_products in PRODUCT_CATALOG.values():
                for product in category_products:
                    if product["id"] == product_id:
                        products.append(Product(**product))
                        found = True
                        break
                if found:
                    break
        
        if len(products) != len(product_ids):
            raise HTTPException(status_code=404, detail="One or more products not found")
        
        return {
            "products": products,
            "comparison_fields": ["price", "ratings", "weight", "drop", "features"],
            "total_products": len(products)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/categories")
async def get_categories():
    """Get available product categories"""
    
    categories = []
    for category, products in PRODUCT_CATALOG.items():
        category_info = {
            "name": category,
            "product_count": len(products),
            "brands": list(set(p["brand"] for p in products)),
            "price_range": {
                "min": min(p["price"] for p in products),
                "max": max(p["price"] for p in products)
            },
            "sample_products": [p["name"] for p in products[:3]]
        }
        categories.append(category_info)
    
    return {
        "categories": categories,
        "total_categories": len(categories)
    }

# Static file serving for production
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "template_35_virtual_ecommerce_agent:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )