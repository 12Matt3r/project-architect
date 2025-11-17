import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { 
  User, 
  ShoppingBag, 
  Brain, 
  TrendingUp, 
  Heart,
  Star,
  DollarSign,
  Target,
  Sparkles,
  Lightbulb,
  CheckCircle2,
  AlertCircle,
  Info,
  Eye,
  Clock,
  Zap
} from 'lucide-react';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const HyperPersonalizedRecommendationSystem = () => {
  const [viewedProducts, setViewedProducts] = useState('');
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [analysisMetadata, setAnalysisMetadata] = useState({});
  const [error, setError] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [activeTab, setActiveTab] = useState('profile');

  // Sample product catalog for selection
  const sampleProducts = {
    tech_001: { name: "iPhone 15 Pro", category: "Technology", price: 999.99 },
    tech_002: { name: "Samsung Galaxy S24", category: "Technology", price: 899.99 },
    tech_003: { name: "MacBook Air M3", category: "Technology", price: 1299.99 },
    tech_004: { name: "Sony WH-1000XM5", category: "Technology", price: 399.99 },
    tech_005: { name: "Apple Watch Series 9", category: "Technology", price: 429.99 },
    fash_001: { name: "Nike Air Force 1", category: "Fashion", price: 90.00 },
    fash_002: { name: "Levi's 501 Jeans", category: "Fashion", price: 79.99 },
    fash_003: { name: "North Face Jacket", category: "Fashion", price: 199.99 },
    fash_004: { name: "Ray-Ban Aviator", category: "Fashion", price: 163.00 },
    home_001: { name: "Dyson V15 Vacuum", category: "Home & Garden", price: 749.99 },
    home_002: { name: "Instant Pot Duo", category: "Home & Garden", price: 99.95 },
    health_001: { name: "Peloton Bike", category: "Health & Fitness", price: 2495.00 },
    health_002: { name: "Fitbit Charge 5", category: "Health & Fitness", price: 179.95 },
    media_001: { name: "Kindle Paperwhite", category: "Books & Media", price: 139.99 },
    media_002: { name: "AirPods Pro", category: "Books & Media", price: 249.99 }
  };

  // User segments data for visualization
  const segmentData = {
    "Budget-Conscious": {
      color: "bg-green-100 text-green-800",
      characteristics: ["Value-focused", "Price-sensitive", "Practical"],
      motivation: "Smart savings with quality"
    },
    "Premium-Seeker": {
      color: "bg-blue-100 text-blue-800",
      characteristics: ["Quality-focused", "Performance-oriented", "Status-conscious"],
      motivation: "Premium experiences and craftsmanship"
    },
    "Trend-Follower": {
      color: "bg-purple-100 text-purple-800",
      characteristics: ["Trend-aware", "Social", "Early-adopter"],
      motivation: "Being first with what's hot"
    },
    "Practical-Buyer": {
      color: "bg-orange-100 text-orange-800",
      characteristics: ["Research-driven", "Functional", "Reliable"],
      motivation: "Proven solutions that work"
    },
    "Luxury-Collector": {
      color: "bg-yellow-100 text-yellow-800",
      characteristics: ["Luxury-focused", "Exclusive", "Collector"],
      motivation: "Investment pieces and exclusivity"
    }
  };

  // Risk tolerance visualization data
  const riskToleranceData = [
    { subject: 'Risk Tolerance', value: 0, fullMark: 100 },
  ];

  // Confidence scores data
  const confidenceData = [
    { name: 'Profile Accuracy', score: 0, color: '#8884d8' },
    { name: 'Recommendation Quality', score: 0, color: '#82ca9d' },
    { name: 'Behavioral Prediction', score: 0, color: '#ffc658' }
  ];

  const addProductToSelection = (productId) => {
    const currentProducts = viewedProducts.split(',').map(p => p.trim()).filter(p => p);
    if (currentProducts.length < 5 && !currentProducts.includes(productId)) {
      setViewedProducts(currentProducts.concat(productId).join(', '));
    }
  };

  const removeProductFromSelection = (productId) => {
    const currentProducts = viewedProducts.split(',').map(p => p.trim()).filter(p => p);
    setViewedProducts(currentProducts.filter(p => p !== productId).join(', '));
  };

  const analyzeProfile = async () => {
    if (!viewedProducts.trim()) {
      setError('Please add at least one product to analyze');
      return;
    }

    const products = viewedProducts.split(',').map(p => p.trim()).filter(p => p);
    if (products.length === 0) {
      setError('Please provide valid product IDs');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/analyze-profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo-token'}`
        },
        body: JSON.stringify({
          viewed_products: products
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.synthetic_profile) {
        setProfile(data.synthetic_profile);
        setRecommendations(data.recommendations || []);
        setAnalysisMetadata(data.analysis_metadata || {});
        setSessionId(data.session_id);
        setActiveTab('recommendations');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      setError(`Analysis failed: ${err.message}`);
      console.error('Profile analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderUserSegmentInfo = (segment) => {
    const info = segmentData[segment];
    if (!info) return null;

    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge className={info.color}>
            {segment}
          </Badge>
        </div>
        <div>
          <h4 className="font-semibold text-sm mb-2">Characteristics</h4>
          <div className="flex flex-wrap gap-1">
            {info.characteristics.map((char, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {char}
              </Badge>
            ))}
          </div>
        </div>
        <div className="text-sm text-slate-600">
          <strong>Motivation:</strong> {info.motivation}
        </div>
      </div>
    );
  };

  const renderConfidenceScores = () => {
    if (!analysisMetadata.confidence_scores) return null;

    const scores = analysisMetadata.confidence_scores;
    const scoreData = [
      { name: 'Profile Accuracy', score: scores.profile_accuracy * 100, color: '#8884d8' },
      { name: 'Recommendation Quality', score: scores.recommendation_quality * 100, color: '#82ca9d' },
      { name: 'Behavioral Prediction', score: scores.behavioral_prediction * 100, color: '#ffc658' }
    ];

    return (
      <div className="space-y-4">
        <h4 className="font-semibold">Analysis Confidence</h4>
        {scoreData.map((item, index) => (
          <div key={index} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{item.name}</span>
              <span>{item.score.toFixed(1)}%</span>
            </div>
            <Progress value={item.score} className="h-2" />
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <div className="p-3 bg-gradient-to-r from-pink-500 to-purple-500 rounded-xl">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
              Hyper-Personalized Recommendation System
            </h1>
          </div>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto">
            AI analyzes your product viewing patterns to create a synthetic user profile and generate 
            3 hyper-targeted recommendations for tomorrow's projected interests
          </p>
        </div>

        {/* Product Selection */}
        <Card className="border-2 border-pink-200 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-pink-50 to-purple-50">
            <CardTitle className="flex items-center gap-2 text-pink-700">
              <ShoppingBag className="w-5 h-5" />
              Select Your Recent Products (Max 5)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Selected Products Display */}
            <div className="space-y-2">
              <h4 className="font-medium">Selected Products:</h4>
              <div className="flex flex-wrap gap-2 min-h-[2rem] p-2 border rounded-lg">
                {viewedProducts.split(',').map((productId, index) => {
                  const product = productId.trim() && sampleProducts[productId.trim()];
                  if (!product) return null;
                  
                  return (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      className="cursor-pointer hover:bg-red-100"
                      onClick={() => removeProductFromSelection(productId.trim())}
                    >
                      {product.name} (${product.price})
                      <span className="ml-1 text-xs">×</span>
                    </Badge>
                  );
                })}
                {viewedProducts.split(',').filter(p => p.trim()).length === 0 && (
                  <span className="text-slate-400 italic">No products selected</span>
                )}
              </div>
            </div>

            {/* Product Catalog */}
            <div className="space-y-4">
              <h4 className="font-medium">Available Products:</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(sampleProducts).map(([id, product]) => {
                  const isSelected = viewedProducts.split(',').map(p => p.trim()).includes(id);
                  
                  return (
                    <Card 
                      key={id} 
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        isSelected ? 'ring-2 ring-pink-400 bg-pink-50' : 'hover:bg-slate-50'
                      }`}
                      onClick={() => addProductToSelection(id)}
                    >
                      <CardContent className="p-4 space-y-2">
                        <h5 className="font-medium text-sm">{product.name}</h5>
                        <div className="flex justify-between items-center">
                          <Badge variant="outline" className="text-xs">
                            {product.category}
                          </Badge>
                          <span className="text-sm font-semibold">${product.price}</span>
                        </div>
                        {isSelected && (
                          <div className="flex items-center gap-1 text-pink-600 text-xs">
                            <CheckCircle2 className="w-3 h-3" />
                            Selected
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>

            <div className="flex gap-3">
              <Button 
                onClick={analyzeProfile}
                disabled={loading || viewedProducts.split(',').filter(p => p.trim()).length === 0}
                className="bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600"
              >
                {loading ? (
                  <>
                    <Brain className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing Profile...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate Profile & Recommendations
                  </>
                )}
              </Button>
            </div>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <span className="text-red-700">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Analysis Results */}
        {profile && recommendations.length > 0 && (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="profile" className="flex items-center gap-2">
                <User className="w-4 h-4" />
                Profile
              </TabsTrigger>
              <TabsTrigger value="recommendations" className="flex items-center gap-2">
                <Target className="w-4 h-4" />
                Recommendations
              </TabsTrigger>
              <TabsTrigger value="psychology" className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4" />
                Psychology
              </TabsTrigger>
              <TabsTrigger value="insights" className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Insights
              </TabsTrigger>
            </TabsList>

            {/* User Profile Tab */}
            <TabsContent value="profile" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Demographics */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="w-5 h-5 text-purple-500" />
                      Synthesized Demographics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-slate-600">Age Range</label>
                        <p className="text-lg font-semibold">{profile.age_range}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-600">Income</label>
                        <p className="text-lg font-semibold">{profile.income_bracket}</p>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-slate-600 mb-2 block">Primary Interests</label>
                      <div className="flex flex-wrap gap-2">
                        {profile.primary_interests.map((interest, index) => (
                          <Badge key={index} variant="outline">
                            {interest}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-600 mb-2 block">Lifestyle Traits</label>
                      <div className="flex flex-wrap gap-2">
                        {profile.lifestyle_traits.map((trait, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {trait}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Behavioral Analysis */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="w-5 h-5 text-purple-500" />
                      Behavioral Profile
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-slate-600">Shopping Behavior</label>
                      <p className="text-sm mt-1">{profile.shopping_behavior}</p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-600">Tech Adoption</label>
                      <Badge className="mt-1">{profile.tech_adoption}</Badge>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium text-slate-600">Price Sensitivity</label>
                        <Progress value={profile.price_sensitivity * 100} className="mt-1" />
                        <p className="text-xs text-slate-500 mt-1">
                          {profile.price_sensitivity > 0.7 ? 'High sensitivity' : 
                           profile.price_sensitivity < 0.3 ? 'Low sensitivity' : 'Moderate sensitivity'}
                        </p>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-slate-600">Risk Tolerance</label>
                        <Progress value={profile.risk_tolerance * 100} className="mt-1" />
                        <p className="text-xs text-slate-500 mt-1">
                          {profile.risk_tolerance > 0.7 ? 'High tolerance' : 
                           profile.risk_tolerance < 0.3 ? 'Low tolerance' : 'Moderate tolerance'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* User Segment Classification */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-purple-500" />
                    User Segment Classification
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {renderUserSegmentInfo(profile.shopping_behavior.includes('Quality-focused') ? 'Premium-Seeker' :
                                        profile.shopping_behavior.includes('price-conscious') ? 'Budget-Conscious' :
                                        profile.shopping_behavior.includes('research') ? 'Practical-Buyer' :
                                        profile.price_sensitivity < 0.3 ? 'Luxury-Collector' : 'Trend-Follower')}
                </CardContent>
              </Card>

              {/* Confidence Scores */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-purple-500" />
                    Analysis Confidence
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {renderConfidenceScores()}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Recommendations Tab */}
            <TabsContent value="recommendations" className="space-y-6">
              <div className="grid gap-6">
                {recommendations.map((rec, index) => {
                  const product = sampleProducts[rec.product_id];
                  if (!product) return null;

                  return (
                    <Card key={index} className="border-2 border-purple-200">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="flex items-center gap-2">
                            <Target className="w-5 h-5 text-purple-500" />
                            Recommendation #{index + 1}
                          </CardTitle>
                          <div className="flex items-center gap-2">
                            <Badge className="bg-purple-100 text-purple-800">
                              {Math.round(rec.confidence_score * 100)}% Match
                            </Badge>
                            <Badge variant="outline">
                              Appeal Score: {Math.round(rec.projected_appeal_score * 100)}%
                            </Badge>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="md:col-span-2 space-y-3">
                            <div>
                              <h4 className="font-semibold text-lg">{product.name}</h4>
                              <div className="flex items-center gap-4 mt-1">
                                <Badge variant="outline">{product.category}</Badge>
                                <span className="text-xl font-bold text-green-600">${product.price}</span>
                              </div>
                            </div>

                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                              <h5 className="font-medium text-blue-800 mb-2 flex items-center gap-2">
                                <Info className="w-4 h-4" />
                                Reasoning
                              </h5>
                              <p className="text-blue-700 text-sm">{rec.reason}</p>
                            </div>
                          </div>

                          <div className="space-y-3">
                            <div>
                              <h5 className="font-medium mb-2">Confidence Metrics</h5>
                              <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span>Match Score</span>
                                  <span>{Math.round(rec.confidence_score * 100)}%</span>
                                </div>
                                <Progress value={rec.confidence_score * 100} className="h-2" />
                                
                                <div className="flex justify-between text-sm">
                                  <span>Appeal Score</span>
                                  <span>{Math.round(rec.projected_appeal_score * 100)}%</span>
                                </div>
                                <Progress value={rec.projected_appeal_score * 100} className="h-2" />
                              </div>
                            </div>

                            <Button className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
                              <Heart className="w-4 h-4 mr-2" />
                              Add to Wishlist
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {/* Psychology Tab */}
            <TabsContent value="psychology" className="space-y-6">
              <div className="grid gap-6">
                {recommendations.map((rec, index) => (
                  <Card key={index} className="border-2 border-pink-200">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Lightbulb className="w-5 h-5 text-pink-500" />
                        Psychological Insight #{index + 1}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                        <p className="text-pink-800 font-medium">{rec.psychological_justification}</p>
                      </div>
                      
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="text-center p-3 bg-slate-50 rounded-lg">
                          <Brain className="w-6 h-6 mx-auto mb-2 text-purple-500" />
                          <h6 className="font-medium text-sm">Psychological Trigger</h6>
                          <p className="text-xs text-slate-600 mt-1">
                            {index === 0 ? 'Status & Identity' : 
                             index === 1 ? 'Social Proof' : 'Future Self-Optimization'}
                          </p>
                        </div>
                        
                        <div className="text-center p-3 bg-slate-50 rounded-lg">
                          <Eye className="w-6 h-6 mx-auto mb-2 text-blue-500" />
                          <h6 className="font-medium text-sm">Behavioral Driver</h6>
                          <p className="text-xs text-slate-600 mt-1">
                            {index === 0 ? 'Premium Self-Image' : 
                             index === 1 ? 'Peer Validation' : 'Continuous Improvement'}
                          </p>
                        </div>
                        
                        <div className="text-center p-3 bg-slate-50 rounded-lg">
                          <TrendingUp className="w-6 h-6 mx-auto mb-2 text-green-500" />
                          <h6 className="font-medium text-sm">Long-term Impact</h6>
                          <p className="text-xs text-slate-600 mt-1">
                            {index === 0 ? 'Brand Loyalty' : 
                             index === 1 ? 'Purchase Confidence' : 'Lifestyle Enhancement'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Insights Tab */}
            <TabsContent value="insights" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Session Summary */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="w-5 h-5 text-blue-500" />
                      Analysis Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-slate-600">Session ID</label>
                        <p className="text-sm font-mono">{sessionId}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-600">Processing Time</label>
                        <p className="text-sm">{analysisMetadata.processing_time_ms}ms</p>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-600">Analysis Timestamp</label>
                      <p className="text-sm">{analysisMetadata.timestamp}</p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-600 mb-2 block">Input Products Analyzed</label>
                      <div className="flex flex-wrap gap-1">
                        {viewedProducts.split(',').map((productId, index) => {
                          const product = productId.trim() && sampleProducts[productId.trim()];
                          if (!product) return null;
                          
                          return (
                            <Badge key={index} variant="outline" className="text-xs">
                              {product.name}
                            </Badge>
                          );
                        })}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Market Insights */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-green-500" />
                      Market Intelligence
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Seasonal Factor</span>
                        <Badge className="bg-orange-100 text-orange-800">
                          {Math.round(analysisMetadata.seasonal_factors * 100)}% Winter Adjustment
                        </Badge>
                      </div>
                      
                      <div className="text-sm">
                        <label className="font-medium text-slate-600">Competitive Analysis</label>
                        <p className="text-slate-700 mt-1">{analysisMetadata.competitive_analysis}</p>
                      </div>

                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <h6 className="font-medium text-green-800 mb-2">Key Insights</h6>
                        <ul className="text-sm text-green-700 space-y-1">
                          <li>• Your viewing patterns suggest high engagement with premium technology</li>
                          <li>• Cross-category browsing indicates diverse interests</li>
                          <li>• Price point analysis shows balanced purchasing behavior</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Recommendation Strategy */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-purple-500" />
                    Tomorrow's Targeting Strategy
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <h6 className="font-semibold text-purple-800">Short-term (24h)</h6>
                      <p className="text-sm text-purple-700 mt-2">
                        Focus on impulse-compatible products with immediate utility value
                      </p>
                    </div>
                    
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <h6 className="font-semibold text-blue-800">Mid-term (1 week)</h6>
                      <p className="text-sm text-blue-700 mt-2">
                        Promote products that align with established interest patterns
                      </p>
                    </div>
                    
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <h6 className="font-semibold text-green-800">Long-term (1 month)</h6>
                      <p className="text-sm text-green-700 mt-2">
                        Introduce variety to expand interest categories gradually
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
};

export default HyperPersonalizedRecommendationSystem;