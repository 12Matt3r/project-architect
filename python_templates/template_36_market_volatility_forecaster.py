#!/usr/bin/env python3
"""
Template #36: Market Volatility Forecaster

A sophisticated financial analysis application that processes stock market data to calculate
key risk metrics and provide narrative risk profiles in plain language.

Calculates: Sharpe Ratio, Sortino Ratio, and Maximum Drawdown with comprehensive analysis.

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
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class TickerRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA)")
    period: str = Field(default="3y", description="Analysis period (1y, 2y, 3y, 5y)")
    risk_free_rate: float = Field(default=0.02, description="Annual risk-free rate (default 2%)")

class RiskMetrics(BaseModel):
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    annualized_return: float
    annualized_volatility: float
    best_day_return: float
    worst_day_return: float
    total_return: float

class RiskAssessment(BaseModel):
    risk_level: str  # "Low", "Moderate", "High", "Very High"
    risk_factors: List[str]
    volatility_assessment: str
    return_assessment: str
    drawdown_assessment: str
    overall_narrative: str
    investment_recommendation: str

class AnalysisResponse(BaseModel):
    ticker: str
    analysis_period: str
    risk_metrics: RiskMetrics
    risk_assessment: RiskAssessment
    market_context: Dict[str, Any]
    confidence_level: float
    analysis_timestamp: datetime

# Dataclasses for internal processing
@dataclass
class StockData:
    ticker: str
    dates: List[str]
    prices: List[float]
    returns: List[float]
    analysis_period: str

@dataclass
class FinancialAnalysis:
    metrics: RiskMetrics
    assessment: RiskAssessment
    market_context: Dict[str, Any]
    confidence_score: float

# Initialize FastAPI app
app = FastAPI(
    title="Market Volatility Forecaster",
    description="Advanced financial risk analysis and volatility assessment tool",
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

class StockDataGenerator:
    """Generate or fetch stock price data with realistic market behavior"""
    
    def __init__(self):
        self.market_scenarios = {
            "bull_market": {"trend": 0.15, "volatility": 0.18, "name": "Strong Bull Market"},
            "bear_market": {"trend": -0.10, "volatility": 0.25, "name": "Bear Market"},
            "sideways_market": {"trend": 0.02, "volatility": 0.15, "name": "Sideways Market"},
            "high_volatility": {"trend": 0.05, "volatility": 0.35, "name": "High Volatility Market"},
            "stable_growth": {"trend": 0.08, "volatility": 0.12, "name": "Stable Growth"}
        }
    
    def fetch_real_data(self, ticker: str, period: str = "3y") -> Optional[StockData]:
        """Fetch real stock data using yfinance"""
        try:
            # Map period to yfinance format
            period_map = {
                "1y": "1y",
                "2y": "2y", 
                "3y": "3y",
                "5y": "5y"
            }
            
            yf_period = period_map.get(period, "3y")
            
            # Fetch data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=yf_period)
            
            if hist.empty or len(hist) < 252:  # Need at least 1 year of data
                logger.warning(f"Insufficient real data for {ticker}, using simulated data")
                return None
            
            # Calculate returns
            returns = hist['Close'].pct_change().dropna()
            
            return StockData(
                ticker=ticker,
                dates=hist.index.strftime('%Y-%m-%d').tolist(),
                prices=hist['Close'].tolist(),
                returns=returns.tolist(),
                analysis_period=period
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch real data for {ticker}: {str(e)}")
            return None
    
    def generate_simulated_data(self, ticker: str, period: str = "3y") -> StockData:
        """Generate realistic simulated stock data"""
        
        # Map period to business days
        period_days = {
            "1y": 252,
            "2y": 504,
            "3y": 756,
            "5y": 1260
        }
        
        trading_days = period_days.get(period, 756)
        
        # Determine market scenario based on ticker or random
        ticker_lower = ticker.lower()
        if any(tech in ticker_lower for tech in ['tsla', 'aapl', 'amzn', 'nvda']):
            scenario = "high_volatility"  # Tech stocks tend to be volatile
        elif any(finance in ticker_lower for finance in ['jpm', 'bac', 'gs']):
            scenario = "stable_growth"  # Finance stocks more stable
        elif any(energy in ticker_lower for energy in ['xom', 'cvx']):
            scenario = "sideways_market"  # Energy stocks cyclical
        else:
            scenario = np.random.choice(list(self.market_scenarios.keys()))
        
        scenario_params = self.market_scenarios[scenario]
        
        # Generate dates (business days only)
        start_date = datetime.now() - timedelta(days=trading_days * 1.4)  # Account for weekends
        dates = []
        current_date = start_date
        while len(dates) < trading_days:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # Generate stock prices using geometric Brownian motion
        np.random.seed(hash(ticker) % 2**32)  # Consistent results for same ticker
        
        # Parameters
        mu = scenario_params["trend"]  # Annual drift
        sigma = scenario_params["volatility"]  # Annual volatility
        dt = 1/252  # Daily time step
        
        # Starting price
        S0 = np.random.uniform(50, 200)  # Random starting price
        
        # Generate price path
        prices = [S0]
        for i in range(1, trading_days):
            z = np.random.standard_normal()
            S_t = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)
            prices.append(S_t)
        
        # Calculate returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        return StockData(
            ticker=ticker,
            dates=dates,
            prices=prices,
            returns=returns,
            analysis_period=period
        )

class FinancialMetricsCalculator:
    """Calculate advanced financial risk metrics"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
    
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe Ratio"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - (self.risk_free_rate / 252)  # Daily risk-free rate
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)  # Annualized
        return float(sharpe)
    
    def calculate_sortino_ratio(self, returns: List[float]) -> float:
        """Calculate Sortino Ratio (focuses only on downside deviation)"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - (self.risk_free_rate / 252)
        
        # Only consider negative excess returns
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf') if np.mean(excess_returns) > 0 else 0.0
        
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0.0
        
        sortino = np.mean(excess_returns) / downside_std * np.sqrt(252)
        return float(sortino)
    
    def calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calculate Maximum Drawdown"""
        if not prices:
            return 0.0
        
        prices_array = np.array(prices)
        
        # Calculate running maximum
        peak = np.maximum.accumulate(prices_array)
        
        # Calculate drawdown
        drawdown = (prices_array - peak) / peak
        
        # Return maximum drawdown (most negative value)
        max_drawdown = np.min(drawdown)
        return float(max_drawdown)
    
    def calculate_additional_metrics(self, returns: List[float], prices: List[float]) -> Dict[str, float]:
        """Calculate additional risk metrics"""
        if not returns or not prices:
            return {}
        
        returns_array = np.array(returns)
        
        # Annualized return
        total_return = (prices[-1] - prices[0]) / prices[0]
        years = len(returns) / 252
        annualized_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        # Annualized volatility
        annualized_volatility = np.std(returns) * np.sqrt(252)
        
        # Best and worst day returns
        best_day = np.max(returns)
        worst_day = np.min(returns)
        
        return {
            "annualized_return": float(annualized_return),
            "annualized_volatility": float(annualized_volatility),
            "best_day_return": float(best_day),
            "worst_day_return": float(worst_day),
            "total_return": float(total_return)
        }

class RiskAssessmentEngine:
    """Generate comprehensive risk assessments and narratives"""
    
    def __init__(self):
        self.risk_thresholds = {
            "sharpe": {"excellent": 1.5, "good": 1.0, "fair": 0.5, "poor": 0.0},
            "sortino": {"excellent": 2.0, "good": 1.5, "fair": 1.0, "poor": 0.0},
            "drawdown": {"low": 0.10, "moderate": 0.20, "high": 0.30, "very_high": 0.50}
        }
    
    def assess_risk_level(self, metrics: RiskMetrics) -> str:
        """Determine overall risk level"""
        risk_score = 0
        
        # Sharpe ratio assessment
        if metrics.sharpe_ratio >= 1.5:
            risk_score -= 2  # Good sign
        elif metrics.sharpe_ratio >= 1.0:
            risk_score -= 1
        elif metrics.sharpe_ratio < 0:
            risk_score += 2  # Bad sign
        
        # Sortino ratio assessment
        if metrics.sortino_ratio >= 2.0:
            risk_score -= 2
        elif metrics.sortino_ratio >= 1.5:
            risk_score -= 1
        elif metrics.sortino_ratio < 1.0:
            risk_score += 1
        
        # Drawdown assessment
        if abs(metrics.max_drawdown) <= 0.10:
            risk_score -= 2
        elif abs(metrics.max_drawdown) <= 0.20:
            risk_score -= 1
        elif abs(metrics.max_drawdown) >= 0.30:
            risk_score += 2
        
        # Volatility assessment
        if metrics.annualized_volatility <= 0.15:
            risk_score -= 1
        elif metrics.annualized_volatility >= 0.30:
            risk_score += 2
        
        # Determine risk level
        if risk_score <= -3:
            return "Low"
        elif risk_score <= -1:
            return "Moderate"
        elif risk_score <= 2:
            return "High"
        else:
            return "Very High"
    
    def identify_risk_factors(self, metrics: RiskMetrics, context: Dict[str, Any]) -> List[str]:
        """Identify key risk factors"""
        risk_factors = []
        
        if metrics.sharpe_ratio < 0:
            risk_factors.append("Negative risk-adjusted returns")
        elif metrics.sharpe_ratio < 0.5:
            risk_factors.append("Poor risk-adjusted performance")
        
        if metrics.sortino_ratio < 1.0:
            risk_factors.append("Significant downside risk")
        
        if abs(metrics.max_drawdown) > 0.30:
            risk_factors.append("High maximum drawdown risk")
        elif abs(metrics.max_drawdown) > 0.20:
            risk_factors.append("Moderate drawdown risk")
        
        if metrics.annualized_volatility > 0.30:
            risk_factors.append("High price volatility")
        elif metrics.annualized_volatility > 0.20:
            risk_factors.append("Elevated volatility")
        
        if metrics.annualized_return < 0:
            risk_factors.append("Negative long-term returns")
        elif metrics.annualized_return > 0.15:
            risk_factors.append("High return potential with increased risk")
        
        if metrics.best_day_return > 0.10:
            risk_factors.append("High positive price swings")
        
        if metrics.worst_day_return < -0.08:
            risk_factors.append("Significant downside risk")
        
        return risk_factors[:5]  # Limit to top 5 risk factors
    
    def generate_narrative(self, ticker: str, metrics: RiskMetrics, assessment: Dict[str, str]) -> str:
        """Generate comprehensive narrative explanation"""
        
        risk_level = assessment["risk_level"]
        
        narrative = f"""
**{ticker.upper()} Risk Profile Analysis**

This analysis of {ticker.upper()} over the past 3 years reveals a **{risk_level.lower()} risk** investment profile with the following characteristics:

**Return Profile:**
{assessment["return_assessment"]}

**Risk Characteristics:**
{assessment["volatility_assessment"]}

**Drawdown Analysis:**
{assessment["drawdown_assessment"]}

**Investment Considerations:**
{assessment["investment_recommendation"]}

**Key Metrics Summary:**
• Sharpe Ratio: {metrics.sharpe_ratio:.2f} (Risk-adjusted returns)
• Sortino Ratio: {metrics.sortino_ratio:.2f} (Downside risk-adjusted)
• Maximum Drawdown: {metrics.max_drawdown:.1%} (Peak-to-trough decline)
• Annualized Return: {metrics.annualized_return:.1%}
• Annualized Volatility: {metrics.annualized_volatility:.1%}
        """
        
        return narrative.strip()
    
    def create_assessment(self, ticker: str, metrics: RiskMetrics, context: Dict[str, Any]) -> RiskAssessment:
        """Create comprehensive risk assessment"""
        
        risk_level = self.assess_risk_level(metrics)
        risk_factors = self.identify_risk_factors(metrics, context)
        
        # Volatility assessment
        if metrics.annualized_volatility <= 0.15:
            volatility_assessment = "Low volatility with stable price movements. Suitable for conservative investors."
        elif metrics.annualized_volatility <= 0.25:
            volatility_assessment = "Moderate volatility with balanced risk-return profile. Appropriate for balanced portfolios."
        else:
            volatility_assessment = "High volatility with significant price swings. Suitable for aggressive investors only."
        
        # Return assessment
        if metrics.annualized_return >= 0.12:
            return_assessment = "Strong long-term returns with above-market performance potential."
        elif metrics.annualized_return >= 0.08:
            return_assessment = "Solid returns with reasonable growth prospects."
        elif metrics.annualized_return >= 0.04:
            return_assessment = "Moderate returns suitable for income-focused investors."
        else:
            return_assessment = "Below-average returns with limited growth potential."
        
        # Drawdown assessment
        drawdown_pct = abs(metrics.max_drawdown)
        if drawdown_pct <= 0.15:
            drawdown_assessment = "Minimal peak-to-trough declines indicate strong downside protection."
        elif drawdown_pct <= 0.25:
            drawdown_assessment = "Manageable drawdowns with reasonable recovery potential."
        else:
            drawdown_assessment = "Significant drawdown risk requiring careful position sizing."
        
        # Investment recommendation
        if risk_level == "Low":
            investment_recommendation = "Suitable for conservative portfolios and income-focused investors."
        elif risk_level == "Moderate":
            investment_recommendation = "Appropriate for balanced portfolios with moderate risk tolerance."
        elif risk_level == "High":
            investment_recommendation = "Suitable for aggressive growth strategies with high risk tolerance."
        else:
            investment_recommendation = "High-risk investment requiring careful risk management and diversification."
        
        # Generate overall narrative
        assessment_dict = {
            "risk_level": risk_level,
            "volatility_assessment": volatility_assessment,
            "return_assessment": return_assessment,
            "drawdown_assessment": drawdown_assessment,
            "investment_recommendation": investment_recommendation
        }
        
        overall_narrative = self.generate_narrative(ticker, metrics, assessment_dict)
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_factors=risk_factors,
            volatility_assessment=volatility_assessment,
            return_assessment=return_assessment,
            drawdown_assessment=drawdown_assessment,
            overall_narrative=overall_narrative,
            investment_recommendation=investment_recommendation
        )

# Initialize components
data_generator = StockDataGenerator()
metrics_calculator = FinancialMetricsCalculator()
assessment_engine = RiskAssessmentEngine()

class DatabaseManager:
    def __init__(self, db_path: str = "market_analysis.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for analysis storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    analysis_id TEXT PRIMARY KEY,
                    ticker TEXT,
                    analysis_period TEXT,
                    risk_metrics TEXT,
                    risk_assessment TEXT,
                    market_context TEXT,
                    confidence_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_analysis(self, analysis_id: str, ticker: str, response_data: Dict):
        """Save analysis to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO analyses 
                (analysis_id, ticker, analysis_period, risk_metrics, risk_assessment, market_context, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                ticker,
                response_data["analysis_period"],
                json.dumps(response_data["risk_metrics"]),
                json.dumps(response_data["risk_assessment"]),
                json.dumps(response_data["market_context"]),
                response_data["confidence_level"]
            ))
    
    def get_analysis_history(self, ticker: str = None, limit: int = 20) -> List[Dict]:
        """Get analysis history"""
        with sqlite3.connect(self.db_path) as conn:
            if ticker:
                cursor = conn.execute("""
                    SELECT analysis_id, ticker, analysis_period, timestamp 
                    FROM analyses 
                    WHERE ticker = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (ticker, limit))
            else:
                cursor = conn.execute("""
                    SELECT analysis_id, ticker, analysis_period, timestamp 
                    FROM analyses 
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
        "message": "Market Volatility Forecaster API",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "Real-time stock data analysis",
            "Advanced risk metrics calculation",
            "Comprehensive risk assessment",
            "Plain language narratives"
        ]
    }

@app.get("/api/v1/supported-tickers")
async def get_supported_tickers():
    """Get list of supported tickers for analysis"""
    popular_tickers = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"],
        "Finance": ["JPM", "BAC", "GS", "MS", "C", "WFC", "AXP", "BLK"],
        "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK", "TMO", "ABT", "DHR"],
        "Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "MPC"],
        "Consumer": ["WMT", "HD", "PG", "KO", "PEP", "MCD", "NKE", "SBUX"],
        "Industrial": ["BA", "CAT", "GE", "MMM", "HON", "UPS", "LMT", "RTX"],
        "Utilities": ["NEE", "DUK", "SO", "D", "AEP", "EXC", "XEL", "SRE"]
    }
    
    return {
        "supported_tickers": popular_tickers,
        "note": "Any valid ticker symbol can be analyzed",
        "data_sources": ["Yahoo Finance API", "Simulated market data"]
    }

@app.post("/api/v1/analyze-ticker", response_model=AnalysisResponse)
async def analyze_ticker(request: TickerRequest):
    """Perform comprehensive risk analysis on ticker symbol"""
    
    try:
        analysis_id = str(uuid.uuid4())
        
        # Generate or fetch stock data
        stock_data = data_generator.fetch_real_data(request.ticker, request.period)
        if stock_data is None:
            stock_data = data_generator.generate_simulated_data(request.ticker, request.period)
        
        # Update metrics calculator with custom risk-free rate
        metrics_calculator.risk_free_rate = request.risk_free_rate
        
        # Calculate core metrics
        sharpe_ratio = metrics_calculator.calculate_sharpe_ratio(stock_data.returns)
        sortino_ratio = metrics_calculator.calculate_sortino_ratio(stock_data.returns)
        max_drawdown = metrics_calculator.calculate_max_drawdown(stock_data.prices)
        
        # Calculate additional metrics
        additional_metrics = metrics_calculator.calculate_additional_metrics(stock_data.returns, stock_data.prices)
        
        # Create risk metrics object
        risk_metrics = RiskMetrics(
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            annualized_return=additional_metrics["annualized_return"],
            annualized_volatility=additional_metrics["annualized_volatility"],
            best_day_return=additional_metrics["best_day_return"],
            worst_day_return=additional_metrics["worst_day_return"],
            total_return=additional_metrics["total_return"]
        )
        
        # Generate market context
        market_context = {
            "data_source": "real" if data_generator.fetch_real_data(request.ticker, request.period) else "simulated",
            "analysis_period": request.period,
            "trading_days_analyzed": len(stock_data.returns),
            "price_range": {
                "min": min(stock_data.prices),
                "max": max(stock_data.prices),
                "current": stock_data.prices[-1]
            },
            "return_distribution": {
                "mean": np.mean(stock_data.returns),
                "std": np.std(stock_data.returns),
                "skewness": float(pd.Series(stock_data.returns).skew()),
                "kurtosis": float(pd.Series(stock_data.returns).kurtosis())
            }
        }
        
        # Generate risk assessment
        risk_assessment = assessment_engine.create_assessment(request.ticker, risk_metrics, market_context)
        
        # Calculate confidence level
        confidence_level = min(95.0, 60.0 + (len(stock_data.returns) / 252 * 10))
        
        # Create response
        response = AnalysisResponse(
            ticker=request.ticker,
            analysis_period=request.period,
            risk_metrics=risk_metrics,
            risk_assessment=risk_assessment,
            market_context=market_context,
            confidence_level=confidence_level,
            analysis_timestamp=datetime.now()
        )
        
        # Save to database
        db_manager.save_analysis(analysis_id, request.ticker, response.dict())
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing ticker {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/analysis-history")
async def get_analysis_history(ticker: str = None, limit: int = 20):
    """Get analysis history"""
    try:
        history = db_manager.get_analysis_history(ticker, limit)
        return {
            "history": history,
            "total_analyses": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/compare-tickers")
async def compare_tickers(tickers: str, period: str = "3y", risk_free_rate: float = 0.02):
    """Compare multiple tickers side by side"""
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(",")]
        if len(ticker_list) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 tickers can be compared")
        
        comparisons = []
        for ticker in ticker_list:
            try:
                request = TickerRequest(
                    ticker=ticker,
                    period=period,
                    risk_free_rate=risk_free_rate
                )
                analysis = await analyze_ticker(request)
                
                comparisons.append({
                    "ticker": ticker,
                    "sharpe_ratio": analysis.risk_metrics.sharpe_ratio,
                    "sortino_ratio": analysis.risk_metrics.sortino_ratio,
                    "max_drawdown": analysis.risk_metrics.max_drawdown,
                    "annualized_return": analysis.risk_metrics.annualized_return,
                    "annualized_volatility": analysis.risk_metrics.annualized_volatility,
                    "risk_level": analysis.risk_assessment.risk_level,
                    "data_source": analysis.market_context["data_source"]
                })
            except Exception as e:
                logger.error(f"Error comparing {ticker}: {str(e)}")
                comparisons.append({
                    "ticker": ticker,
                    "error": str(e)
                })
        
        return {
            "comparisons": comparisons,
            "analysis_period": period,
            "risk_free_rate": risk_free_rate
        }
        
    except Exception as e:
        logger.error(f"Error in ticker comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.get("/api/v1/market-indicators")
async def get_market_indicators():
    """Get current market indicators and context"""
    
    # Simulated market indicators
    indicators = {
        "market_sentiment": {
            "value": np.random.uniform(0.3, 0.8),
            "description": "Overall market sentiment index"
        },
        "volatility_index": {
            "value": np.random.uniform(0.15, 0.35),
            "description": "Market-wide volatility indicator"
        },
        "interest_rates": {
            "federal_funds": 0.0525,
            "十年国债": 0.042,
            "description": "Current interest rate environment"
        },
        "sector_performance": {
            "technology": np.random.uniform(-0.15, 0.25),
            "healthcare": np.random.uniform(-0.10, 0.20),
            "finance": np.random.uniform(-0.08, 0.18),
            "energy": np.random.uniform(-0.20, 0.30),
            "description": "Recent sector performance trends"
        },
        "economic_indicators": {
            "gdp_growth": np.random.uniform(0.01, 0.04),
            "inflation_rate": np.random.uniform(0.02, 0.06),
            "unemployment": np.random.uniform(0.03, 0.06),
            "description": "Key economic indicators"
        }
    }
    
    return {
        "indicators": indicators,
        "timestamp": datetime.now().isoformat(),
        "note": "Indicators are simulated for demonstration purposes"
    }

# Run server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "template_36_market_volatility_forecaster:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )