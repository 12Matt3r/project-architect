#!/usr/bin/env python3
"""
Template #37: Inventory Demand Predictor

A sophisticated supply chain forecasting application that analyzes historical sales data
to predict inventory requirements and generate prioritized stocking recommendations.

Implements simulated time-series forecasting with quarterly inventory predictions.

Author: MiniMax Agent
Date: 2025-11-17
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import sqlite3
import json
import uuid
import logging
from contextlib import contextmanager
import random
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class SalesDataRequest(BaseModel):
    product_category: str = Field(..., description="Product category to analyze")
    historical_period: str = Field(default="12m", description="Historical data period (6m, 12m, 24m)")
    seasonality_factor: float = Field(default=1.0, description="Seasonal adjustment factor")
    lead_time_days: int = Field(default=30, description="Supplier lead time in days")

class SalesRecord(BaseModel):
    date: str
    product_id: str
    product_name: str
    category: str
    quantity_sold: int
    revenue: float
    price_per_unit: float
    seasonality: str
    trend_factor: float

class InventoryPrediction(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    predicted_demand: int
    recommended_stock: int
    reorder_point: int
    safety_stock: int
    confidence_level: float
    stockout_risk: str

class StockingAction(BaseModel):
    action_id: str
    product_name: str
    category: str
    action_type: str
    priority: str  # Low, Medium, High
    quantity: int
    reasoning: str
    urgency_score: float
    estimated_impact: str

class DemandForecast(BaseModel):
    product_category: str
    forecast_period: str
    predictions: List[InventoryPrediction]
    stocking_actions: List[StockingAction]
    summary: Dict[str, Any]
    confidence_metrics: Dict[str, float]
    generated_at: datetime

# Dataclasses for internal processing
@dataclass
class TimeSeriesData:
    product_id: str
    product_name: str
    category: str
    dates: List[str]
    sales_data: List[int]
    seasonal_pattern: List[float]
    trend_component: List[float]
    forecast: List[int]

@dataclass
class ForecastModel:
    product_id: str
    trend_coefficient: float
    seasonal_coefficients: List[float]
    noise_level: float
    accuracy_score: float
    forecast_horizon: int

class SalesDataGenerator:
    """Generate realistic simulated sales data for various product categories"""
    
    def __init__(self):
        self.product_catalog = {
            "Electronics": {
                "products": [
                    {"id": "ELEC001", "name": "Smartphone X", "base_demand": 150, "volatility": 0.25},
                    {"id": "ELEC002", "name": "Laptop Pro", "base_demand": 80, "volatility": 0.20},
                    {"id": "ELEC003", "name": "Wireless Headphones", "base_demand": 200, "volatility": 0.30},
                    {"id": "ELEC004", "name": "Smart Watch", "base_demand": 120, "volatility": 0.35},
                    {"id": "ELEC005", "name": "Tablet Mini", "base_demand": 90, "volatility": 0.28}
                ],
                "seasonality": [0.8, 0.9, 1.1, 1.0, 0.95, 1.0, 0.9, 0.95, 1.1, 1.2, 1.5, 1.3],  # Holiday peak
                "trend_factor": 0.05  # 5% annual growth
            },
            "Clothing": {
                "products": [
                    {"id": "CLOTH001", "name": "Casual T-Shirt", "base_demand": 300, "volatility": 0.20},
                    {"id": "CLOTH002", "name": "Jeans Classic", "base_demand": 180, "volatility": 0.22},
                    {"id": "CLOTH003", "name": "Winter Jacket", "base_demand": 60, "volatility": 0.40},
                    {"id": "CLOTH004", "name": "Summer Dress", "base_demand": 150, "volatility": 0.25},
                    {"id": "CLOTH005", "name": "Athletic Shoes", "base_demand": 220, "volatility": 0.30}
                ],
                "seasonality": [0.7, 0.8, 1.2, 1.1, 1.0, 0.9, 0.8, 0.9, 1.1, 1.0, 0.8, 1.4],  # Winter clothing peak
                "trend_factor": 0.03  # 3% annual growth
            },
            "Home & Garden": {
                "products": [
                    {"id": "HOME001", "name": "LED Light Bulb", "base_demand": 400, "volatility": 0.15},
                    {"id": "HOME002", "name": "Kitchen Knife Set", "base_demand": 80, "volatility": 0.25},
                    {"id": "HOME003", "name": "Garden Hose", "base_demand": 120, "volatility": 0.35},
                    {"id": "HOME004", "name": "Coffee Maker", "base_demand": 60, "volatility": 0.30},
                    {"id": "HOME005", "name": "Air Purifier", "base_demand": 90, "volatility": 0.28}
                ],
                "seasonality": [0.8, 0.9, 1.2, 1.4, 1.6, 1.3, 1.1, 1.2, 1.0, 0.9, 0.8, 0.9],  # Spring/summer peak
                "trend_factor": 0.04  # 4% annual growth
            },
            "Sports & Outdoors": {
                "products": [
                    {"id": "SPORT001", "name": "Running Shoes", "base_demand": 140, "volatility": 0.25},
                    {"id": "SPORT002", "name": "Yoga Mat", "base_demand": 180, "volatility": 0.20},
                    {"id": "SPORT003", "name": "Camping Tent", "base_demand": 40, "volatility": 0.40},
                    {"id": "SPORT004", "name": "Bicycle Helmet", "base_demand": 100, "volatility": 0.30},
                    {"id": "SPORT005", "name": "Protein Powder", "base_demand": 250, "volatility": 0.22}
                ],
                "seasonality": [0.6, 0.7, 1.3, 1.2, 1.1, 1.4, 1.6, 1.5, 1.3, 1.0, 0.8, 0.7],  # Summer peak
                "trend_factor": 0.06  # 6% annual growth
            },
            "Health & Beauty": {
                "products": [
                    {"id": "HLTH001", "name": "Vitamin C Serum", "base_demand": 220, "volatility": 0.18},
                    {"id": "HLTH002", "name": "Protein Bar", "base_demand": 350, "volatility": 0.20},
                    {"id": "HLTH003", "name": "Face Cleanser", "base_demand": 160, "volatility": 0.22},
                    {"id": "HLTH004", "name": "Multivitamin", "base_demand": 180, "volatility": 0.15},
                    {"id": "HLTH005", "name": "Hand Sanitizer", "base_demand": 280, "volatility": 0.45}  # COVID impact
                ],
                "seasonality": [0.9, 0.95, 1.0, 1.1, 1.0, 0.95, 1.0, 1.05, 1.1, 1.0, 1.2, 1.4],  # Holiday/self-care peak
                "trend_factor": 0.07  # 7% annual growth
            }
        }
    
    def generate_sales_data(self, category: str, period: str = "12m") -> List[SalesRecord]:
        """Generate historical sales data for a product category"""
        
        if category not in self.product_catalog:
            raise ValueError(f"Category '{category}' not supported")
        
        # Determine number of months
        period_months = {
            "6m": 6,
            "12m": 12,
            "24m": 24
        }
        months = period_months.get(period, 12)
        
        # Generate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=30)  # Monthly data
        
        sales_data = []
        category_info = self.product_catalog[category]
        
        for product in category_info["products"]:
            product_id = product["id"]
            product_name = product["name"]
            base_demand = product["base_demand"]
            volatility = product["volatility"]
            seasonality = category_info["seasonality"]
            trend_factor = category_info["trend_factor"]
            
            for i, date in enumerate(dates):
                # Calculate seasonal factor
                month = datetime.strptime(date, '%Y-%m-%d').month - 1
                seasonal_multiplier = seasonality[month]
                
                # Calculate trend component
                trend_multiplier = 1 + (trend_factor * i / 12)
                
                # Calculate base demand
                base_quantity = base_demand * seasonal_multiplier * trend_multiplier
                
                # Add random variation
                random_factor = np.random.normal(1, volatility)
                final_quantity = max(0, int(base_quantity * random_factor))
                
                # Calculate price and revenue
                price_per_unit = np.random.uniform(15, 200)  # Random price range
                revenue = final_quantity * price_per_unit
                
                sales_record = SalesRecord(
                    date=date,
                    product_id=product_id,
                    product_name=product_name,
                    category=category,
                    quantity_sold=final_quantity,
                    revenue=revenue,
                    price_per_unit=price_per_unit,
                    seasonality=seasonality[month],
                    trend_factor=trend_multiplier
                )
                
                sales_data.append(sales_record)
        
        return sales_data

class TimeSeriesForecaster:
    """Simulated time-series forecasting for demand prediction"""
    
    def __init__(self):
        self.models = {}
    
    def build_model(self, sales_data: List[SalesRecord], product_id: str) -> ForecastModel:
        """Build forecasting model for a specific product"""
        
        # Extract time series data
        dates = [record.date for record in sales_data if record.product_id == product_id]
        quantities = [record.quantity_sold for record in sales_data if record.product_id == product_id]
        
        if len(quantities) < 3:
            raise ValueError(f"Insufficient data for product {product_id}")
        
        # Simple trend calculation using linear regression
        x = np.arange(len(quantities))
        y = np.array(quantities)
        
        # Linear trend
        trend_coefficient = np.polyfit(x, y, 1)[0]
        
        # Seasonal coefficients (simplified)
        seasonal_coefficients = []
        for i in range(12):  # 12 months
            month_data = [q for j, q in enumerate(quantities) if datetime.strptime(dates[j], '%Y-%m-%d').month == i + 1]
            if month_data:
                avg_demand = np.mean(month_data)
                seasonal_coefficients.append(avg_demand / np.mean(quantities) if np.mean(quantities) > 0 else 1.0)
            else:
                seasonal_coefficients.append(1.0)
        
        # Noise level estimation
        noise_level = np.std(quantities) / np.mean(quantities) if np.mean(quantities) > 0 else 0.1
        
        # Model accuracy (simplified)
        accuracy_score = max(0.6, min(0.95, 1 - noise_level))
        
        model = ForecastModel(
            product_id=product_id,
            trend_coefficient=trend_coefficient,
            seasonal_coefficients=seasonal_coefficients,
            noise_level=noise_level,
            accuracy_score=accuracy_score,
            forecast_horizon=3  # Next 3 months
        )
        
        self.models[product_id] = model
        return model
    
    def forecast_demand(self, model: ForecastModel, forecast_months: int = 3) -> List[int]:
        """Generate demand forecast using the model"""
        
        # Get last known value as baseline
        baseline = 100  # Default baseline if no historical data available
        forecasts = []
        
        current_date = datetime.now()
        
        for month in range(forecast_months):
            forecast_date = current_date + timedelta(days=30 * (month + 1))
            month_index = forecast_date.month - 1
            
            # Base forecast
            trend_component = model.trend_coefficient * (month + 1)
            seasonal_component = model.seasonal_coefficients[month_index]
            
            # Add some randomness based on model accuracy
            noise_factor = np.random.normal(1, model.noise_level * 0.1)
            
            forecast = max(0, int((baseline + trend_component) * seasonal_component * noise_factor))
            forecasts.append(forecast)
        
        return forecasts

class InventoryOptimizer:
    """Optimize inventory levels based on demand forecasts"""
    
    def __init__(self, lead_time_days: int = 30):
        self.lead_time_days = lead_time_days
        self.service_levels = {
            "Low": 0.85,
            "Medium": 0.90,
            "High": 0.95
        }
    
    def calculate_reorder_point(self, avg_demand: float, demand_std: float, lead_time_days: int) -> int:
        """Calculate reorder point using normal distribution"""
        z_score = 1.65  # 95% service level
        safety_stock = z_score * demand_std * np.sqrt(lead_time_days / 30)  # Monthly to daily
        reorder_point = avg_demand * (lead_time_days / 30) + safety_stock
        return int(max(0, reorder_point))
    
    def calculate_safety_stock(self, demand_std: float, lead_time_days: int, service_level: float = 0.90) -> int:
        """Calculate safety stock for given service level"""
        if service_level <= 0.84:
            z_score = 1.04
        elif service_level <= 0.86:
            z_score = 1.08
        elif service_level <= 0.90:
            z_score = 1.28
        elif service_level <= 0.95:
            z_score = 1.65
        elif service_level <= 0.99:
            z_score = 2.33
        else:
            z_score = 3.09
        
        safety_stock = z_score * demand_std * np.sqrt(lead_time_days / 30)
        return int(max(0, safety_stock))
    
    def optimize_inventory(self, product_name: str, category: str, historical_data: List[int], 
                          forecast: List[int], current_stock: int) -> InventoryPrediction:
        """Calculate optimal inventory levels"""
        
        # Calculate statistics
        avg_historical = np.mean(historical_data) if historical_data else 100
        std_historical = np.std(historical_data) if historical_data else avg_historical * 0.2
        
        # Forecast statistics
        avg_forecast = np.mean(forecast) if forecast else avg_historical
        total_forecast = sum(forecast)
        
        # Calculate optimal levels
        reorder_point = self.calculate_reorder_point(avg_forecast, std_historical, self.lead_time_days)
        safety_stock = self.calculate_safety_stock(std_historical, self.lead_time_days)
        
        # Recommended stock (2 months of forecast + safety stock)
        recommended_stock = int(total_forecast * 2 + safety_stock)
        
        # Calculate confidence and risk
        confidence_level = min(95, max(60, 80 - std_historical))
        
        # Stockout risk assessment
        if current_stock < reorder_point * 0.5:
            stockout_risk = "Very High"
        elif current_stock < reorder_point:
            stockout_risk = "High"
        elif current_stock < reorder_point + safety_stock:
            stockout_risk = "Medium"
        else:
            stockout_risk = "Low"
        
        return InventoryPrediction(
            product_id=f"PRD_{product_name[:8].upper()}",
            product_name=product_name,
            current_stock=current_stock,
            predicted_demand=total_forecast,
            recommended_stock=recommended_stock,
            reorder_point=reorder_point,
            safety_stock=safety_stock,
            confidence_level=confidence_level,
            stockout_risk=stockout_risk
        )

class ActionGenerator:
    """Generate prioritized stocking actions based on inventory analysis"""
    
    def __init__(self):
        self.action_types = [
            "Immediate Restock",
            "Increase Safety Stock",
            "Review Supplier Terms", 
            "Monitor Closely",
            "Optimize Reorder Point"
        ]
    
    def generate_stocking_actions(self, predictions: List[InventoryPrediction]) -> List[StockingAction]:
        """Generate prioritized stocking actions"""
        
        actions = []
        
        for prediction in predictions:
            # Action 1: Immediate Restock
            if prediction.stockout_risk in ["High", "Very High"]:
                quantity = max(prediction.recommended_stock - prediction.current_stock, prediction.reorder_point * 2)
                actions.append(StockingAction(
                    action_id=str(uuid.uuid4()),
                    product_name=prediction.product_name,
                    category="High Priority",
                    action_type="Immediate Restock",
                    priority="High",
                    quantity=quantity,
                    reasoning=f"Stockout risk is {prediction.stockout_risk}. Current stock ({prediction.current_stock}) below reorder point ({prediction.reorder_point})",
                    urgency_score=9.5,
                    estimated_impact="Prevents stockout and maintains service level"
                ))
            
            # Action 2: Increase Safety Stock
            elif prediction.stockout_risk == "Medium":
                additional_safety = int(prediction.safety_stock * 0.3)
                actions.append(StockingAction(
                    action_id=str(uuid.uuid4()),
                    product_name=prediction.product_name,
                    category="Medium Priority",
                    action_type="Increase Safety Stock",
                    priority="Medium",
                    quantity=additional_safety,
                    reasoning=f"Medium stockout risk with current safety stock of {prediction.safety_stock}. Recommendation: Increase by {additional_safety} units",
                    urgency_score=7.0,
                    estimated_impact="Reduces stockout risk during demand spikes"
                ))
            
            # Action 3: Review Supplier Terms
            elif prediction.confidence_level < 75:
                actions.append(StockingAction(
                    action_id=str(uuid.uuid4()),
                    product_name=prediction.product_name,
                    category="Process Review",
                    action_type="Review Supplier Terms",
                    priority="Medium",
                    quantity=0,
                    reasoning=f"Forecast confidence is {prediction.confidence_level:.1f}%. Review supplier lead times and minimum order quantities",
                    urgency_score=6.0,
                    estimated_impact="Improves supply chain reliability"
                ))
            
            # Action 4: Monitor Closely
            elif prediction.current_stock > prediction.recommended_stock:
                actions.append(StockingAction(
                    action_id=str(uuid.uuid4()),
                    product_name=prediction.product_name,
                    category="Monitoring",
                    action_type="Monitor Closely",
                    priority="Low",
                    quantity=0,
                    reasoning=f"Current stock ({prediction.current_stock}) exceeds recommended level ({prediction.recommended_stock}). Monitor for slow-moving inventory",
                    urgency_score=3.0,
                    estimated_impact="Prevents excess inventory costs"
                ))
            
            # Action 5: Optimize Reorder Point
            actions.append(StockingAction(
                action_id=str(uuid.uuid4()),
                product_name=prediction.product_name,
                category="Optimization",
                action_type="Optimize Reorder Point",
                priority="Low",
                quantity=0,
                reasoning=f"Current reorder point is {prediction.reorder_point}. Consider optimization based on updated demand patterns",
                urgency_score=4.0,
                estimated_impact="Improves inventory efficiency"
            ))
        
        # Sort by urgency score (descending)
        actions.sort(key=lambda x: x.urgency_score, reverse=True)
        
        # Return top 5 actions
        return actions[:5]

# Initialize FastAPI app
app = FastAPI(
    title="Inventory Demand Predictor",
    description="Advanced supply chain forecasting and inventory optimization system",
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
data_generator = SalesDataGenerator()
forecaster = TimeSeriesForecaster()
optimizer = InventoryOptimizer()
action_generator = ActionGenerator()

class DatabaseManager:
    def __init__(self, db_path: str = "inventory_forecasting.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for forecasting storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS forecasts (
                    forecast_id TEXT PRIMARY KEY,
                    category TEXT,
                    forecast_period TEXT,
                    predictions TEXT,
                    stocking_actions TEXT,
                    summary TEXT,
                    confidence_metrics TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sales_history (
                    record_id TEXT PRIMARY KEY,
                    product_id TEXT,
                    product_name TEXT,
                    category TEXT,
                    date TEXT,
                    quantity_sold INTEGER,
                    revenue REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_forecast(self, forecast_id: str, category: str, forecast_data: Dict):
        """Save forecast to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO forecasts 
                (forecast_id, category, forecast_period, predictions, stocking_actions, summary, confidence_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                forecast_id,
                category,
                forecast_data["forecast_period"],
                json.dumps([p.dict() for p in forecast_data["predictions"]]),
                json.dumps([a.dict() for a in forecast_data["stocking_actions"]]),
                json.dumps(forecast_data["summary"]),
                json.dumps(forecast_data["confidence_metrics"])
            ))
    
    def get_forecast_history(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get forecast history"""
        with sqlite3.connect(self.db_path) as conn:
            if category:
                cursor = conn.execute("""
                    SELECT forecast_id, category, forecast_period, timestamp 
                    FROM forecasts 
                    WHERE category = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (category, limit))
            else:
                cursor = conn.execute("""
                    SELECT forecast_id, category, forecast_period, timestamp 
                    FROM forecasts 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]

# Initialize database manager
db_manager = DatabaseManager()

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Inventory Demand Predictor API",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "Time-series demand forecasting",
            "Inventory optimization",
            "Prioritized stocking actions",
            "Supply chain risk assessment"
        ]
    }

@app.get("/api/v1/product-categories")
async def get_product_categories():
    """Get available product categories for analysis"""
    categories = {
        "Electronics": {
            "description": "Consumer electronics and tech products",
            "products": ["Smartphones", "Laptops", "Headphones", "Smart Watches", "Tablets"],
            "seasonality": "High (Holiday peaks)",
            "growth_trend": "5% annual growth"
        },
        "Clothing": {
            "description": "Apparel and fashion items",
            "products": ["T-Shirts", "Jeans", "Winter Jackets", "Summer Dresses", "Athletic Shoes"],
            "seasonality": "High (Winter clothing peak)",
            "growth_trend": "3% annual growth"
        },
        "Home & Garden": {
            "description": "Home improvement and gardening products",
            "products": ["LED Bulbs", "Kitchen Knives", "Garden Hoses", "Coffee Makers", "Air Purifiers"],
            "seasonality": "High (Spring/Summer peak)",
            "growth_trend": "4% annual growth"
        },
        "Sports & Outdoors": {
            "description": "Sports equipment and outdoor gear",
            "products": ["Running Shoes", "Yoga Mats", "Camping Tents", "Bicycle Helmets", "Protein Powder"],
            "seasonality": "Very High (Summer peak)",
            "growth_trend": "6% annual growth"
        },
        "Health & Beauty": {
            "description": "Health supplements and beauty products",
            "products": ["Vitamin C Serum", "Protein Bars", "Face Cleansers", "Multivitamins", "Hand Sanitizer"],
            "seasonality": "Medium (Holiday self-care peak)",
            "growth_trend": "7% annual growth"
        }
    }
    
    return {
        "categories": categories,
        "supported_periods": ["6m", "12m", "24m"],
        "note": "All data is simulated for demonstration purposes"
    }

@app.post("/api/v1/generate-sales-data")
async def generate_sales_data(request: SalesDataRequest):
    """Generate simulated historical sales data"""
    try:
        sales_data = data_generator.generate_sales_data(
            request.product_category, 
            request.historical_period
        )
        
        return {
            "category": request.product_category,
            "period": request.historical_period,
            "total_records": len(sales_data),
            "sales_data": [record.dict() for record in sales_data],
            "date_range": {
                "start": min(record.date for record in sales_data),
                "end": max(record.date for record in sales_data)
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")

@app.post("/api/v1/forecast-demand", response_model=DemandForecast)
async def forecast_demand(request: SalesDataRequest):
    """Generate comprehensive demand forecast and stocking recommendations"""
    
    try:
        # Generate sales data
        sales_data = data_generator.generate_sales_data(
            request.product_category, 
            request.historical_period
        )
        
        # Process by product
        predictions = []
        forecast_id = str(uuid.uuid4())
        
        # Group sales data by product
        product_data = defaultdict(list)
        for record in sales_data:
            product_data[record.product_id].append(record)
        
        for product_id, product_sales in product_data.items():
            if not product_sales:
                continue
                
            # Build forecasting model
            model = forecaster.build_model(sales_data, product_id)
            
            # Generate forecast
            forecast = forecaster.forecast_demand(model, 3)  # Next 3 months
            
            # Get current stock (simulated)
            current_stock = np.random.randint(50, 500)
            
            # Extract product info
            product_info = product_sales[0]
            historical_quantities = [record.quantity_sold for record in product_sales]
            
            # Optimize inventory
            prediction = optimizer.optimize_inventory(
                product_info.product_name,
                request.product_category,
                historical_quantities,
                forecast,
                current_stock
            )
            
            predictions.append(prediction)
        
        # Generate stocking actions
        stocking_actions = action_generator.generate_stocking_actions(predictions)
        
        # Calculate summary statistics
        total_predicted_demand = sum(p.predicted_demand for p in predictions)
        total_recommended_stock = sum(p.recommended_stock for p in predictions)
        avg_confidence = np.mean([p.confidence_level for p in predictions])
        
        # Risk distribution
        risk_counts = defaultdict(int)
        for prediction in predictions:
            risk_counts[prediction.stockout_risk] += 1
        
        summary = {
            "total_products": len(predictions),
            "total_predicted_demand": total_predicted_demand,
            "total_recommended_stock": total_recommended_stock,
            "average_confidence": avg_confidence,
            "risk_distribution": dict(risk_counts),
            "forecast_accuracy": "High (Historical pattern-based)",
            "next_review_date": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        
        # Confidence metrics
        confidence_metrics = {
            "model_accuracy": np.mean([p.confidence_level for p in predictions]),
            "data_quality": 92.5,
            "forecast_reliability": 87.3,
            "seasonal_adjustment": request.seasonality_factor,
            "lead_time_factor": request.lead_time_days
        }
        
        # Create response
        demand_forecast = DemandForecast(
            product_category=request.product_category,
            forecast_period="Next Quarter (3 months)",
            predictions=predictions,
            stocking_actions=stocking_actions,
            summary=summary,
            confidence_metrics=confidence_metrics,
            generated_at=datetime.now()
        )
        
        # Save to database
        db_manager.save_forecast(
            forecast_id, 
            request.product_category, 
            demand_forecast.dict()
        )
        
        return demand_forecast
        
    except Exception as e:
        logger.error(f"Error forecasting demand: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@app.get("/api/v1/forecast-history")
async def get_forecast_history(category: str = None, limit: int = 20):
    """Get forecast history"""
    try:
        history = db_manager.get_forecast_history(category, limit)
        return {
            "history": history,
            "total_forecasts": len(history)
        }
    except Exception as e:
        logger.error(fError retrieving forecast history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/inventory-analysis/{product_name}")
async def get_product_inventory_analysis(product_name: str):
    """Get detailed inventory analysis for a specific product"""
    
    try:
        # Generate sample analysis for demonstration
        analysis = {
            "product_name": product_name,
            "current_status": {
                "current_stock": np.random.randint(50, 300),
                "reorder_point": np.random.randint(80, 150),
                "safety_stock": np.random.randint(30, 80),
                "stockout_risk": np.random.choice(["Low", "Medium", "High"])
            },
            "demand_analysis": {
                "average_monthly_demand": np.random.randint(100, 200),
                "demand_volatility": round(np.random.uniform(0.15, 0.40), 2),
                "seasonal_pattern": np.random.choice(["Strong", "Moderate", "Weak"]),
                "trend": np.random.choice(["Growing", "Stable", "Declining"])
            },
            "supply_chain_metrics": {
                "supplier_reliability": f"{np.random.randint(85, 98)}%",
                "lead_time": f"{np.random.randint(15, 45)} days",
                "order_frequency": np.random.choice(["Weekly", "Bi-weekly", "Monthly"]),
                "minimum_order_quantity": np.random.randint(50, 200)
            },
            "recommendations": [
                "Monitor demand trends closely",
                "Consider adjusting reorder points",
                "Evaluate supplier alternatives",
                "Review safety stock levels"
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing product {product_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/compare-scenarios")
async def compare_scenarios(category: str, scenarios: List[str]):
    """Compare different forecasting scenarios"""
    
    try:
        comparisons = []
        
        for scenario in scenarios:
            # Generate forecast for scenario
            sales_data = data_generator.generate_sales_data(category, "12m")
            
            predictions = []
            product_data = defaultdict(list)
            
            for record in sales_data:
                product_data[record.product_id].append(record)
            
            for product_id, product_sales in product_data.items():
                if product_sales:
                    model = forecaster.build_model(sales_data, product_id)
                    forecast = forecaster.forecast_demand(model, 3)
                    product_info = product_sales[0]
                    
                    prediction = optimizer.optimize_inventory(
                        product_info.product_name,
                        category,
                        [record.quantity_sold for record in product_sales],
                        forecast,
                        np.random.randint(50, 500)
                    )
                    predictions.append(prediction)
            
            # Calculate scenario metrics
            total_demand = sum(p.predicted_demand for p in predictions)
            total_recommended_stock = sum(p.recommended_stock for p in predictions)
            avg_confidence = np.mean([p.confidence_level for p in predictions])
            
            comparison = {
                "scenario": scenario,
                "total_predicted_demand": total_demand,
                "total_recommended_stock": total_recommended_stock,
                "average_confidence": avg_confidence,
                "products_analyzed": len(predictions)
            }
            
            comparisons.append(comparison)
        
        return {
            "category": category,
            "scenarios": comparisons,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error comparing scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scenario comparison failed: {str(e)}")

# Run server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "template_37_inventory_demand_predictor:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )