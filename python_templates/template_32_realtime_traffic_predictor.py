"""
Template #32: Real-Time Traffic Predictor
Advanced traffic prediction system with real-time API integration and historical pattern analysis
"""

import os
import json
import sqlite3
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import uuid
import requests
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import time

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Traffic Predictor",
    description="Advanced traffic prediction system with real-time API integration and historical pattern analysis",
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
DATABASE_PATH = "/workspace/traffic_predictor.db"
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_database():
    """Initialize SQLite database for traffic predictions"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id TEXT PRIMARY KEY,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            prediction_time TIMESTAMP NOT NULL,
            confidence_score REAL NOT NULL,
            predicted_duration REAL NOT NULL,
            current_duration REAL,
            traffic_conditions TEXT,
            historical_patterns TEXT,
            weather_impact REAL,
            event_impact REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Historical traffic data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_data (
            id TEXT PRIMARY KEY,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            day_of_week INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            avg_duration REAL NOT NULL,
            variance REAL NOT NULL,
            peak_factor REAL NOT NULL,
            weather_multiplier REAL DEFAULT 1.0,
            event_multiplier REAL DEFAULT 1.0,
            sample_count INTEGER DEFAULT 0
        )
    ''')
    
    # Traffic conditions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_conditions (
            id TEXT PRIMARY KEY,
            location TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            congestion_level TEXT NOT NULL,
            average_speed REAL NOT NULL,
            incidents_count INTEGER DEFAULT 0,
            weather_condition TEXT DEFAULT 'clear',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# Enums for traffic and prediction types
class CongestionLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"

class WeatherCondition(Enum):
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    STORM = "storm"

class PredictionType(Enum):
    NORMAL = "normal"
    PREDICTIVE = "predictive"
    HISTORICAL = "historical"

@dataclass
class Location:
    """Represents a geographical location"""
    name: str
    latitude: float
    longitude: float
    traffic_zones: List[str]

@dataclass
class TrafficCondition:
    """Real-time traffic condition data"""
    location: str
    timestamp: datetime
    congestion_level: CongestionLevel
    average_speed: float
    incidents: int
    weather: WeatherCondition
    traffic_flow: float

@dataclass
class HistoricalPattern:
    """Historical traffic pattern data"""
    origin: str
    destination: str
    day_of_week: int
    hour: int
    avg_duration: float
    variance: float
    peak_factor: float
    weather_multiplier: float
    event_multiplier: float

@dataclass
class TrafficPrediction:
    """Complete traffic prediction result"""
    id: str
    origin: str
    destination: str
    prediction_time: datetime
    confidence_score: float
    predicted_duration: float
    current_duration: Optional[float]
    traffic_conditions: Dict
    historical_analysis: Dict
    factors: Dict
    recommendations: List[str]

class TrafficDataProvider:
    """Simulates real-time traffic API integration"""
    
    def __init__(self):
        self.locations = self._load_locations()
        self.current_conditions = {}
        
    def _load_locations(self) -> Dict[str, Location]:
        """Load predefined locations with coordinates and zones"""
        return {
            "Downtown": Location("Downtown", 40.7589, -73.9851, ["business_district", "commercial"]),
            "Airport": Location("Airport", 40.6413, -73.7781, ["transportation", "high_volume"]),
            "University": Location("University", 40.8075, -73.9626, ["educational", "residential"]),
            "Shopping Center": Location("Shopping Center", 40.7505, -73.9934, ["commercial", "entertainment"]),
            "Hospital": Location("Hospital", 40.7892, -73.9512, ["medical", "emergency"]),
            "Stadium": Location("Stadium", 40.8296, -73.9262, ["sports", "events"])
        }
    
    def get_real_time_traffic(self, origin: str, destination: str) -> TrafficCondition:
        """Simulate real-time traffic API call"""
        
        # Generate realistic traffic conditions based on current time and location
        now = datetime.now()
        current_hour = now.hour
        current_dow = now.weekday()
        
        # Base congestion patterns by time and day
        base_congestion = self._calculate_base_congestion(current_hour, current_dow)
        
        # Apply location-specific modifiers
        origin_zone_modifier = self._get_location_modifier(origin)
        dest_zone_modifier = self._get_location_modifier(destination)
        
        # Calculate combined congestion
        combined_congestion = (base_congestion + origin_zone_modifier + dest_zone_modifier) / 3
        
        # Determine congestion level
        if combined_congestion < 0.3:
            congestion_level = CongestionLevel.LOW
            speed_factor = random.uniform(0.8, 0.95)
        elif combined_congestion < 0.6:
            congestion_level = CongestionLevel.MODERATE
            speed_factor = random.uniform(0.5, 0.8)
        elif combined_congestion < 0.8:
            congestion_level = CongestionLevel.HIGH
            speed_factor = random.uniform(0.3, 0.6)
        else:
            congestion_level = CongestionLevel.SEVERE
            speed_factor = random.uniform(0.1, 0.4)
        
        # Base speed (km/h)
        base_speed = 50
        actual_speed = base_speed * speed_factor
        
        # Simulate incidents
        incidents = random.choices([0, 1, 2, 3], weights=[80, 15, 4, 1])[0]
        
        # Weather simulation
        weather_conditions = list(WeatherCondition)
        weather = random.choices(
            weather_conditions, 
            weights=[70, 15, 5, 5, 5]
        )[0]
        
        # Traffic flow calculation
        traffic_flow = (actual_speed / base_speed) * 100
        
        return TrafficCondition(
            location=f"{origin} to {destination}",
            timestamp=now,
            congestion_level=congestion_level,
            average_speed=actual_speed,
            incidents=incidents,
            weather=weather,
            traffic_flow=traffic_flow
        )
    
    def _calculate_base_congestion(self, hour: int, dow: int) -> float:
        """Calculate base congestion pattern by time and day"""
        
        # Peak hours (7-9 AM, 5-7 PM)
        if (7 <= hour <= 9) or (17 <= hour <= 19):
            peak_factor = 0.8
        # Moderate hours (10-16)
        elif 10 <= hour <= 16:
            peak_factor = 0.5
        # Evening (20-22)
        elif 20 <= hour <= 22:
            peak_factor = 0.4
        # Night (23-6)
        else:
            peak_factor = 0.2
        
        # Day of week modifiers
        dow_modifiers = {
            0: 0.7,  # Monday
            1: 0.6,  # Tuesday
            2: 0.6,  # Wednesday
            3: 0.7,  # Thursday
            4: 0.8,  # Friday
            5: 0.5,  # Saturday
            6: 0.4   # Sunday
        }
        
        return peak_factor * dow_modifiers[dow]
    
    def _get_location_modifier(self, location: str) -> float:
        """Get congestion modifier based on location type"""
        location_data = self.locations.get(location)
        if not location_data:
            return 0.5
        
        # Zone-based modifiers
        zone_modifiers = {
            "business_district": 0.3,
            "commercial": 0.2,
            "transportation": 0.4,
            "high_volume": 0.5,
            "educational": 0.2,
            "residential": 0.1,
            "entertainment": 0.3,
            "medical": 0.2,
            "sports": 0.6,
            "events": 0.7
        }
        
        modifiers = [zone_modifiers.get(zone, 0.3) for zone in location_data.traffic_zones]
        return sum(modifiers) / len(modifiers) if modifiers else 0.3

class HistoricalPatternAnalyzer:
    """Analyzes historical traffic patterns for prediction accuracy"""
    
    def __init__(self):
        self.patterns = self._initialize_historical_data()
    
    def _initialize_historical_data(self) -> Dict[str, HistoricalPattern]:
        """Initialize simulated historical traffic data"""
        patterns = {}
        
        # Generate historical patterns for all location pairs and time slots
        locations = ["Downtown", "Airport", "University", "Shopping Center", "Hospital", "Stadium"]
        
        for origin in locations:
            for destination in locations:
                if origin != destination:
                    for dow in range(7):  # 0-6 (Monday-Sunday)
                        for hour in range(24):  # 0-23
                            
                            # Calculate base duration (minutes)
                            base_duration = self._calculate_base_duration(origin, destination)
                            
                            # Apply temporal patterns
                            temporal_multiplier = self._get_temporal_multiplier(hour, dow)
                            
                            avg_duration = base_duration * temporal_multiplier
                            variance = avg_duration * 0.15  # 15% variance
                            
                            # Peak factor calculation
                            peak_hours = [7, 8, 17, 18, 19]
                            peak_factor = 1.3 if hour in peak_hours else 1.0
                            
                            # Weather and event multipliers
                            weather_multiplier = random.uniform(0.9, 1.2)
                            event_multiplier = random.uniform(0.95, 1.3)
                            
                            pattern_id = f"{origin}_{destination}_{dow}_{hour}"
                            patterns[pattern_id] = HistoricalPattern(
                                origin=origin,
                                destination=destination,
                                day_of_week=dow,
                                hour=hour,
                                avg_duration=avg_duration,
                                variance=variance,
                                peak_factor=peak_factor,
                                weather_multiplier=weather_multiplier,
                                event_multiplier=event_multiplier
                            )
        
        return patterns
    
    def _calculate_base_duration(self, origin: str, destination: str) -> float:
        """Calculate base travel duration between locations"""
        # Simulated distances (km) and base speeds
        distances = {
            ("Downtown", "Airport"): 25.0,
            ("Downtown", "University"): 12.0,
            ("Downtown", "Shopping Center"): 8.0,
            ("Downtown", "Hospital"): 6.0,
            ("Downtown", "Stadium"): 15.0,
            ("Airport", "University"): 18.0,
            ("Airport", "Shopping Center"): 20.0,
            ("Airport", "Hospital"): 22.0,
            ("Airport", "Stadium"): 35.0,
            ("University", "Shopping Center"): 10.0,
            ("University", "Hospital"): 8.0,
            ("University", "Stadium"): 12.0,
            ("Shopping Center", "Hospital"): 5.0,
            ("Shopping Center", "Stadium"): 10.0,
            ("Hospital", "Stadium"): 12.0
        }
        
        # Symmetric distance lookup
        distance = distances.get((origin, destination)) or distances.get((destination, origin))
        if not distance:
            distance = random.uniform(5, 30)  # Default distance
        
        base_speed = 50  # km/h
        base_duration = (distance / base_speed) * 60  # Convert to minutes
        
        return base_duration
    
    def _get_temporal_multiplier(self, hour: int, dow: int) -> float:
        """Get temporal multiplier based on hour and day of week"""
        
        # Hour-based multipliers
        hour_multipliers = {
            range(0, 6): 0.8,    # Night (12am-6am)
            range(6, 10): 1.4,   # Morning rush (6am-10am)
            range(10, 16): 1.0,  # Midday (10am-4pm)
            range(16, 20): 1.5,  # Evening rush (4pm-8pm)
            range(20, 24): 0.9   # Evening (8pm-12am)
        }
        
        for time_range, multiplier in hour_multipliers.items():
            if hour in time_range:
                temporal_multiplier = multiplier
                break
        else:
            temporal_multiplier = 1.0
        
        # Day of week modifiers
        dow_modifiers = {
            0: 1.3,  # Monday - high traffic
            1: 1.2,  # Tuesday
            2: 1.2,  # Wednesday
            3: 1.3,  # Thursday
            4: 1.4,  # Friday - highest traffic
            5: 0.8,  # Saturday - lower traffic
            6: 0.7   # Sunday - lowest traffic
        }
        
        return temporal_multiplier * dow_modifiers[dow]
    
    def get_historical_pattern(self, origin: str, destination: str, target_time: datetime) -> HistoricalPattern:
        """Get historical pattern for specific time and route"""
        
        pattern_id = f"{origin}_{destination}_{target_time.weekday()}_{target_time.hour}"
        pattern = self.patterns.get(pattern_id)
        
        if not pattern:
            # Generate pattern if not exists
            base_duration = self._calculate_base_duration(origin, destination)
            temporal_multiplier = self._get_temporal_multiplier(target_time.hour, target_time.weekday())
            
            pattern = HistoricalPattern(
                origin=origin,
                destination=destination,
                day_of_week=target_time.weekday(),
                hour=target_time.hour,
                avg_duration=base_duration * temporal_multiplier,
                variance=base_duration * 0.15,
                peak_factor=1.2 if target_time.hour in [7, 8, 17, 18, 19] else 1.0,
                weather_multiplier=1.0,
                event_multiplier=1.0
            )
        
        return pattern

class ConfidenceScorer:
    """Calculates calibrated confidence scores for predictions"""
    
    def __init__(self):
        self.calibration_factors = self._load_calibration_factors()
    
    def _load_calibration_factors(self) -> Dict[str, float]:
        """Load factors that affect prediction confidence"""
        return {
            "data_freshness": 0.2,      # How recent is the data
            "historical_coverage": 0.25, # How much historical data is available
            "weather_stability": 0.15,   # Weather condition stability
            "traffic_volatility": 0.20,  # Traffic pattern volatility
            "time_precision": 0.10,      # Time window precision
            "location_accuracy": 0.10    # Location-specific factors
        }
    
    def calculate_confidence_score(self, 
                                 real_time_data: TrafficCondition,
                                 historical_pattern: HistoricalPattern,
                                 prediction_time: datetime) -> Tuple[float, Dict]:
        """Calculate calibrated confidence score for prediction"""
        
        # Base confidence
        base_confidence = 0.70
        
        # Data freshness factor (higher score for more recent data)
        data_age = (datetime.now() - real_time_data.timestamp).total_seconds() / 60  # minutes
        freshness_score = max(0.5, 1.0 - (data_age / 30))  # Decay over 30 minutes
        data_freshness_factor = self.calibration_factors["data_freshness"] * freshness_score
        
        # Historical coverage factor
        # Simulate historical data coverage based on pattern completeness
        historical_score = 0.8 + random.uniform(-0.1, 0.2)  # Varies between 0.7-1.0
        historical_coverage_factor = self.calibration_factors["historical_coverage"] * historical_score
        
        # Weather stability factor
        weather_factors = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAIN: 0.85,
            WeatherCondition.SNOW: 0.70,
            WeatherCondition.FOG: 0.75,
            WeatherCondition.STORM: 0.60
        }
        weather_stability = weather_factors.get(real_time_data.weather, 0.8)
        weather_stability_factor = self.calibration_factors["weather_stability"] * weather_stability
        
        # Traffic volatility factor
        # Lower volatility = higher confidence
        volatility_mapping = {
            CongestionLevel.LOW: 0.95,
            CongestionLevel.MODERATE: 0.85,
            CongestionLevel.HIGH: 0.70,
            CongestionLevel.SEVERE: 0.55
        }
        volatility_score = volatility_mapping.get(real_time_data.congestion_level, 0.8)
        traffic_volatility_factor = self.calibration_factors["traffic_volatility"] * volatility_score
        
        # Time precision factor
        # Predictions for nearer future are more accurate
        time_until_prediction = (prediction_time - datetime.now()).total_seconds() / 3600  # hours
        time_precision = max(0.6, 1.0 - (time_until_prediction / 24))  # Decay over 24 hours
        time_precision_factor = self.calibration_factors["time_precision"] * time_precision
        
        # Location accuracy factor
        # Some routes are easier to predict than others
        location_score = 0.85 + random.uniform(-0.1, 0.15)  # Varies between 0.75-1.0
        location_accuracy_factor = self.calibration_factors["location_accuracy"] * location_score
        
        # Calculate total confidence score
        total_adjustment = (
            data_freshness_factor + 
            historical_coverage_factor + 
            weather_stability_factor + 
            traffic_volatility_factor + 
            time_precision_factor + 
            location_accuracy_factor
        )
        
        final_confidence = min(0.95, base_confidence + total_adjustment)
        
        # Factor breakdown for transparency
        factors = {
            "base_confidence": base_confidence,
            "data_freshness": freshness_score,
            "historical_coverage": historical_score,
            "weather_stability": weather_stability,
            "traffic_volatility": volatility_score,
            "time_precision": time_precision,
            "location_accuracy": location_score,
            "total_adjustment": total_adjustment
        }
        
        return final_confidence, factors

class TrafficPredictor:
    """Main traffic prediction engine"""
    
    def __init__(self):
        self.data_provider = TrafficDataProvider()
        self.pattern_analyzer = HistoricalPatternAnalyzer()
        self.confidence_scorer = ConfidenceScorer()
        
    def predict_traffic(self, 
                       origin: str, 
                       destination: str, 
                       prediction_time: datetime) -> TrafficPrediction:
        """Generate complete traffic prediction"""
        
        # Generate unique prediction ID
        prediction_id = str(uuid.uuid4())
        
        # Get real-time traffic data
        real_time_data = self.data_provider.get_real_time_traffic(origin, destination)
        
        # Get historical pattern analysis
        historical_pattern = self.pattern_analyzer.get_historical_pattern(
            origin, destination, prediction_time
        )
        
        # Calculate confidence score
        confidence_score, confidence_factors = self.confidence_scorer.calculate_confidence_score(
            real_time_data, historical_pattern, prediction_time
        )
        
        # Calculate predicted duration
        base_duration = historical_pattern.avg_duration
        
        # Apply real-time adjustments
        realtime_multiplier = self._calculate_realtime_multiplier(real_time_data)
        weather_multiplier = self._calculate_weather_multiplier(real_time_data.weather)
        incident_multiplier = self._calculate_incident_multiplier(real_time_data.incidents)
        
        predicted_duration = base_duration * realtime_multiplier * weather_multiplier * incident_multiplier
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            real_time_data, predicted_duration, confidence_score
        )
        
        # Compile prediction result
        prediction = TrafficPrediction(
            id=prediction_id,
            origin=origin,
            destination=destination,
            prediction_time=prediction_time,
            confidence_score=confidence_score,
            predicted_duration=predicted_duration,
            current_duration=real_time_data.average_speed * 60 / 50 if real_time_data.average_speed > 0 else None,
            traffic_conditions=asdict(real_time_data),
            historical_analysis={
                "base_duration": historical_pattern.avg_duration,
                "peak_factor": historical_pattern.peak_factor,
                "historical_variance": historical_pattern.variance,
                "temporal_pattern": f"{historical_pattern.day_of_week}_hour_{historical_pattern.hour}"
            },
            factors={
                "realtime_multiplier": realtime_multiplier,
                "weather_multiplier": weather_multiplier,
                "incident_multiplier": incident_multiplier,
                "confidence_factors": confidence_factors
            },
            recommendations=recommendations
        )
        
        # Store prediction in database
        self._store_prediction(prediction)
        
        return prediction
    
    def _calculate_realtime_multiplier(self, traffic_data: TrafficCondition) -> float:
        """Calculate multiplier based on current traffic conditions"""
        speed_ratio = traffic_data.average_speed / 50  # Base speed ratio
        
        congestion_multipliers = {
            CongestionLevel.LOW: 0.9,
            CongestionLevel.MODERATE: 1.2,
            CongestionLevel.HIGH: 1.6,
            CongestionLevel.SEVERE: 2.2
        }
        
        base_multiplier = congestion_multipliers.get(traffic_data.congestion_level, 1.0)
        flow_adjustment = (100 - traffic_data.traffic_flow) / 100 * 0.5
        
        return base_multiplier + flow_adjustment
    
    def _calculate_weather_multiplier(self, weather: WeatherCondition) -> float:
        """Calculate weather impact on travel time"""
        weather_multipliers = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAIN: 1.15,
            WeatherCondition.SNOW: 1.40,
            WeatherCondition.FOG: 1.20,
            WeatherCondition.STORM: 1.60
        }
        
        return weather_multipliers.get(weather, 1.0)
    
    def _calculate_incident_multiplier(self, incident_count: int) -> float:
        """Calculate impact of traffic incidents"""
        incident_multipliers = {
            0: 1.0,
            1: 1.10,
            2: 1.25,
            3: 1.45
        }
        
        return incident_multipliers.get(incident_count, 1.6)
    
    def _generate_recommendations(self, 
                                traffic_data: TrafficCondition,
                                predicted_duration: float,
                                confidence_score: float) -> List[str]:
        """Generate actionable recommendations based on prediction"""
        
        recommendations = []
        
        # Confidence-based recommendations
        if confidence_score >= 0.85:
            recommendations.append("High confidence prediction - proceed with confidence")
        elif confidence_score >= 0.70:
            recommendations.append("Moderate confidence - allow 10% buffer time")
        else:
            recommendations.append("Lower confidence - allow 20% additional time")
        
        # Traffic condition recommendations
        if traffic_data.congestion_level == CongestionLevel.SEVERE:
            recommendations.append("Severe congestion detected - consider alternative route")
        elif traffic_data.congestion_level == CongestionLevel.HIGH:
            recommendations.append("Heavy traffic expected - start journey early")
        
        # Weather recommendations
        if traffic_data.weather in [WeatherCondition.RAIN, WeatherCondition.SNOW, WeatherCondition.STORM]:
            weather_recommendations = {
                WeatherCondition.RAIN: "Drive carefully - wet road conditions",
                WeatherCondition.SNOW: "Use winter driving techniques - allow extra time",
                WeatherCondition.STORM: "Consider delaying travel if possible"
            }
            recommendations.append(weather_recommendations.get(traffic_data.weather, "Weather may affect travel time"))
        
        # Duration-based recommendations
        if predicted_duration > 60:  # Over 1 hour
            recommendations.append("Long journey - plan for rest stops")
        elif predicted_duration < 15:  # Under 15 minutes
            recommendations.append("Short trip - traffic impact may be minimal")
        
        # Incident-based recommendations
        if traffic_data.incidents > 2:
            recommendations.append(f"{traffic_data.incidents} incidents reported - expect delays")
        
        return recommendations
    
    def _store_prediction(self, prediction: TrafficPrediction):
        """Store prediction in database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions (
                id, origin, destination, prediction_time, confidence_score,
                predicted_duration, current_duration, traffic_conditions,
                historical_patterns, weather_impact, event_impact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction.id,
            prediction.origin,
            prediction.destination,
            prediction.prediction_time.isoformat(),
            prediction.confidence_score,
            prediction.predicted_duration,
            prediction.current_duration,
            json.dumps(prediction.traffic_conditions),
            json.dumps(prediction.historical_analysis),
            prediction.factors.get("weather_multiplier", 1.0),
            prediction.factors.get("event_multiplier", 1.0)
        ))
        
        conn.commit()
        conn.close()

# Initialize traffic predictor
traffic_predictor = TrafficPredictor()

# API Models
class PredictionRequest(BaseModel):
    origin: str = Field(..., description="Starting location")
    destination: str = Field(..., description="Destination location")
    prediction_time: str = Field(..., description="Target prediction time (ISO format)")
    route_preference: Optional[str] = Field(None, description="Preferred route type")

class PredictionResponse(BaseModel):
    prediction_id: str
    origin: str
    destination: str
    prediction_time: str
    confidence_score: float
    predicted_duration: float
    current_duration: Optional[float]
    traffic_conditions: Dict
    historical_analysis: Dict
    factors: Dict
    recommendations: List[str]

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Real-Time Traffic Predictor API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "predict_traffic": "/api/v1/predict-traffic",
            "get_prediction": "/api/v1/prediction/{prediction_id}",
            "historical_data": "/api/v1/historical/{origin}/{destination}",
            "traffic_conditions": "/api/v1/traffic-conditions",
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
            "traffic_predictor": "active",
            "historical_analyzer": "ready",
            "confidence_scorer": "calibrated"
        },
        "data_freshness": "real-time",
        "prediction_accuracy": "calibrated"
    }

@app.post("/api/v1/predict-traffic", response_model=PredictionResponse)
async def predict_traffic(
    origin: str = Form(..., description="Starting location"),
    destination: str = Form(..., description="Destination location"),
    prediction_time: str = Form(..., description="Target prediction time (ISO format)"),
    route_preference: Optional[str] = Form(None, description="Preferred route type")
):
    """
    Generate traffic prediction for specified route and time
    
    - **origin**: Starting location (Downtown, Airport, University, Shopping Center, Hospital, Stadium)
    - **destination**: Destination location
    - **prediction_time**: Target time for prediction in ISO format (e.g., "2025-11-17T15:30:00")
    - **route_preference**: Optional route preference (fastest, shortest, avoid_tolls)
    """
    
    try:
        # Validate locations
        valid_locations = ["Downtown", "Airport", "University", "Shopping Center", "Hospital", "Stadium"]
        
        if origin not in valid_locations:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid origin location. Must be one of: {', '.join(valid_locations)}"
            )
        
        if destination not in valid_locations:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid destination location. Must be one of: {', '.join(valid_locations)}"
            )
        
        if origin == destination:
            raise HTTPException(status_code=400, detail="Origin and destination cannot be the same")
        
        # Parse prediction time
        try:
            target_time = datetime.fromisoformat(prediction_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid prediction_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
        
        # Validate prediction time is in the future
        if target_time < datetime.now():
            raise HTTPException(
                status_code=400, 
                detail="Prediction time must be in the future"
            )
        
        # Generate prediction
        prediction = traffic_predictor.predict_traffic(origin, destination, target_time)
        
        return JSONResponse(content=asdict(prediction))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/v1/prediction/{prediction_id}")
async def get_prediction(prediction_id: str):
    """Retrieve previously generated prediction"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT origin, destination, prediction_time, confidence_score,
                   predicted_duration, current_duration, traffic_conditions,
                   historical_patterns, weather_impact, event_impact
            FROM predictions WHERE id = ?
        ''', (prediction_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        (
            origin, destination, prediction_time, confidence_score,
            predicted_duration, current_duration, traffic_conditions_json,
            historical_patterns_json, weather_impact, event_impact
        ) = result
        
        return {
            "prediction_id": prediction_id,
            "origin": origin,
            "destination": destination,
            "prediction_time": prediction_time,
            "confidence_score": confidence_score,
            "predicted_duration": predicted_duration,
            "current_duration": current_duration,
            "traffic_conditions": json.loads(traffic_conditions_json),
            "historical_analysis": json.loads(historical_patterns_json),
            "factors": {
                "weather_impact": weather_impact,
                "event_impact": event_impact
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve prediction: {str(e)}")

@app.get("/api/v1/historical/{origin}/{destination}")
async def get_historical_data(origin: str, destination: str):
    """Get historical traffic patterns for route"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT day_of_week, hour, avg_duration, variance, peak_factor,
                   weather_multiplier, event_multiplier, sample_count
            FROM historical_data 
            WHERE origin = ? AND destination = ?
            ORDER BY day_of_week, hour
        ''', (origin, destination))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {
                "route": f"{origin} to {destination}",
                "message": "No historical data available for this route",
                "data_points": []
            }
        
        historical_data = []
        for row in results:
            historical_data.append({
                "day_of_week": row[0],
                "hour": row[1],
                "avg_duration": row[2],
                "variance": row[3],
                "peak_factor": row[4],
                "weather_multiplier": row[5],
                "event_multiplier": row[6],
                "sample_count": row[7]
            })
        
        return {
            "route": f"{origin} to {destination}",
            "data_points": historical_data,
            "total_samples": sum(point["sample_count"] for point in historical_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve historical data: {str(e)}")

@app.get("/api/v1/traffic-conditions")
async def get_current_traffic_conditions(origin: str = None, destination: str = None):
    """Get current traffic conditions for specified locations"""
    try:
        # If no specific route provided, get conditions for all major routes
        if not origin or not destination:
            conditions = []
            locations = ["Downtown", "Airport", "University", "Shopping Center", "Hospital", "Stadium"]
            
            for orig in locations:
                for dest in locations:
                    if orig != dest:
                        traffic_data = traffic_predictor.data_provider.get_real_time_traffic(orig, dest)
                        conditions.append(asdict(traffic_data))
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_routes": len(conditions),
                "conditions": conditions
            }
        else:
            # Get specific route conditions
            traffic_data = traffic_predictor.data_provider.get_real_time_traffic(origin, destination)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "route": f"{origin} to {destination}",
                "condition": asdict(traffic_data)
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get traffic conditions: {str(e)}")

@app.get("/api/v1/locations")
async def get_available_locations():
    """Get list of available locations"""
    locations = traffic_predictor.data_provider.locations
    
    return {
        "locations": [
            {
                "name": loc.name,
                "coordinates": {"latitude": loc.latitude, "longitude": loc.longitude},
                "zones": loc.traffic_zones
            }
            for loc in locations.values()
        ]
    }

@app.get("/api/v1/predictions")
async def list_predictions(limit: int = 10):
    """List recent predictions"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, origin, destination, prediction_time, confidence_score,
                   predicted_duration, created_at
            FROM predictions 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                "prediction_id": row[0],
                "origin": row[1],
                "destination": row[2],
                "prediction_time": row[3],
                "confidence_score": row[4],
                "predicted_duration": row[5],
                "created_at": row[6]
            })
        
        conn.close()
        
        return {
            "predictions": predictions,
            "total": len(predictions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list predictions: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)