import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import { ScrollArea } from './components/ui/scroll-area';
import { Separator } from './components/ui/separator';
import { 
  Upload, 
  Brain, 
  Target, 
  Settings, 
  FileText, 
  Code, 
  Download, 
  Copy, 
  RefreshCw, 
  Eye,
  CheckCircle,
  AlertTriangle,
  Zap,
  TrendingUp,
  Shield,
  Users,
  Database,
  Cpu,
  Globe
} from 'lucide-react';

/**
 * Project ARCHITECT - Meta-App Generator Frontend
 * Advanced AI system with 5 enhancement features:
 * 1. RSIPV (Recursive Self-Improvement for Plan Validation)
 * 2. CCP-R (Calibrated Confidence Prompting for Risk)
 * 3. CADUG (Context-Aware Decomposition of User Goals)
 * 4. DTCS (Dynamic Tool-Chain Selector)
 * 5. Multi-Modal Input Integration
 */

const ProjectArchitect = () => {
  const [userInput, setUserInput] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [blueprint, setBlueprint] = useState(null);
  const [activeTab, setActiveTab] = useState('input');
  const fileInputRef = useRef(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setImageFile(file);
    }
  };

  const generateBlueprint = async () => {
    if (!userInput.trim()) {
      alert('Please enter an app idea');
      return;
    }

    setIsGenerating(true);
    
    try {
      const formData = new FormData();
      formData.append('user_input', userInput);
      
      if (imageFile) {
        formData.append('image', imageFile);
      }

      const response = await fetch('/api/v1/generate-blueprint', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to generate blueprint');
      }

      const blueprintData = await response.json();
      setBlueprint(blueprintData);
      setActiveTab('blueprint');
    } catch (error) {
      console.error('Error generating blueprint:', error);
      alert('Failed to generate blueprint. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Show success feedback
  };

  const downloadBlueprint = () => {
    const dataStr = JSON.stringify(blueprint, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `project-architect-blueprint-${blueprint.blueprint_id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskLevelColor = (risk) => {
    switch(risk.toLowerCase()) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Brain className="w-12 h-12 text-blue-600 mr-4" />
            <h1 className="text-4xl font-bold text-gray-900">Project ARCHITECT</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Meta-App Generator with Advanced AI Enhancements - Convert natural language ideas into complete development blueprints
          </p>
          <div className="flex flex-wrap justify-center gap-2 mt-4">
            <Badge variant="outline" className="bg-blue-50">
              <RefreshCw className="w-3 h-3 mr-1" />
              RSIPV Enabled
            </Badge>
            <Badge variant="outline" className="bg-green-50">
              <Target className="w-3 h-3 mr-1" />
              CCP-R Active
            </Badge>
            <Badge variant="outline" className="bg-purple-50">
              <Users className="w-3 h-3 mr-1" />
              CADUG Running
            </Badge>
            <Badge variant="outline" className="bg-orange-50">
              <Zap className="w-3 h-3 mr-1" />
              DTCS Optimized
            </Badge>
            <Badge variant="outline" className="bg-pink-50">
              <Eye className="w-3 h-3 mr-1" />
              Multi-Modal Ready
            </Badge>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="input">Input & Analysis</TabsTrigger>
            <TabsTrigger value="blueprint">Generated Blueprint</TabsTrigger>
            <TabsTrigger value="enhancements">Enhancement Features</TabsTrigger>
            <TabsTrigger value="history">History & Export</TabsTrigger>
          </TabsList>

          {/* Input & Analysis Tab */}
          <TabsContent value="input" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  App Idea Input
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Describe your app idea in natural language
                  </label>
                  <Textarea
                    placeholder="e.g., Create a music style extractor where users can upload audio files and get tempo, key, and generate matching instrumentals..."
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    rows={4}
                    className="w-full"
                  />
                </div>

                {/* Multi-Modal Input Section */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  {imageFile ? (
                    <div className="space-y-2">
                      <CheckCircle className="w-8 h-8 text-green-600 mx-auto" />
                      <p className="text-sm font-medium">{imageFile.name}</p>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setImageFile(null)}
                      >
                        Remove Image
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="w-8 h-8 text-gray-400 mx-auto" />
                      <p className="text-sm text-gray-600">
                        Optional: Upload a UI mockup or sketch to enhance blueprint generation
                      </p>
                      <Button 
                        variant="outline" 
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Upload Image
                      </Button>
                    </div>
                  )}
                </div>

                {/* Enhancement Status Indicators */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <RefreshCw className="w-6 h-6 text-blue-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">RSIPV</p>
                    <p className="text-xs text-gray-600">3-iteration validation</p>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <Target className="w-6 h-6 text-green-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">CCP-R</p>
                    <p className="text-xs text-gray-600">Risk assessment</p>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <Users className="w-6 h-6 text-purple-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">CADUG</p>
                    <p className="text-xs text-gray-600">Goal decomposition</p>
                  </div>
                  <div className="text-center p-3 bg-orange-50 rounded-lg">
                    <Zap className="w-6 h-6 text-orange-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">DTCS</p>
                    <p className="text-xs text-gray-600">Tool optimization</p>
                  </div>
                  <div className="text-center p-3 bg-pink-50 rounded-lg">
                    <Eye className="w-6 h-6 text-pink-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">Vision</p>
                    <p className="text-xs text-gray-600">Multi-modal input</p>
                  </div>
                </div>

                <Button 
                  onClick={generateBlueprint}
                  disabled={isGenerating || !userInput.trim()}
                  className="w-full"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Generating Blueprint with AI Enhancements...
                    </>
                  ) : (
                    <>
                      <Brain className="w-4 h-4 mr-2" />
                      Generate Complete Blueprint
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* AI Systems Database Integration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  AI Systems Database Integration
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 border rounded-lg">
                    <Code className="w-6 h-6 text-blue-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">1000+ AI Tools</p>
                    <p className="text-xs text-gray-600">Auto-selection</p>
                  </div>
                  <div className="text-center p-3 border rounded-lg">
                    <Globe className="w-6 h-6 text-green-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">Real-time</p>
                    <p className="text-xs text-gray-600">Performance data</p>
                  </div>
                  <div className="text-center p-3 border rounded-lg">
                    <TrendingUp className="w-6 h-6 text-purple-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">Smart Matching</p>
                    <p className="text-xs text-gray-600">Requirements-based</p>
                  </div>
                  <div className="text-center p-3 border rounded-lg">
                    <Shield className="w-6 h-6 text-orange-600 mx-auto mb-1" />
                    <p className="text-xs font-medium">Validated</p>
                    <p className="text-xs text-gray-600">Security checked</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Generated Blueprint Tab */}
          <TabsContent value="blueprint" className="space-y-6">
            {blueprint ? (
              <>
                {/* Blueprint Header */}
                <Card>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="flex items-center">
                          <Brain className="w-5 h-5 mr-2 text-blue-600" />
                          Generated Blueprint #{blueprint.blueprint_id}
                        </CardTitle>
                        <p className="text-sm text-gray-600 mt-1">
                          Generated: {new Date(blueprint.timestamp).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={downloadBlueprint}>
                          <Download className="w-4 h-4 mr-1" />
                          Export
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => copyToClipboard(blueprint.master_prompt)}>
                          <Copy className="w-4 h-4 mr-1" />
                          Copy Prompt
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                </Card>

                {/* 1. Recommended Toolkit */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Settings className="w-5 h-5 mr-2" />
                      1. Recommended Toolkit
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {blueprint.recommended_toolkit.map((tool, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-semibold">{tool.tool_name}</h4>
                            <Badge variant="outline">{tool.category}</Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{tool.capability}</p>
                          <div className="flex items-center gap-4 text-sm">
                            <span className={`font-medium ${getConfidenceColor(tool.confidence_score)}`}>
                              Confidence: {(tool.confidence_score * 100).toFixed(0)}%
                            </span>
                            <span className="text-gray-600">
                              Complexity: {tool.integration_complexity}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-2">{tool.performance_reason}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 2. App Blueprint & Data Flow */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Target className="w-5 h-5 mr-2" />
                      2. App Blueprint & Data Flow
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2">Goal</h4>
                        <p className="text-sm bg-blue-50 p-3 rounded">{blueprint.app_blueprint_dataflow.goal}</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold mb-2">Core Logic</h4>
                        <p className="text-sm bg-green-50 p-3 rounded">{blueprint.app_blueprint_dataflow.core_logic}</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold mb-2">Data/File Flow</h4>
                        <p className="text-sm bg-purple-50 p-3 rounded">{blueprint.app_blueprint_dataflow.data_file_flow}</p>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold mb-2">User Interface</h4>
                        <p className="text-sm bg-orange-50 p-3 rounded">{blueprint.app_blueprint_dataflow.user_interface}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 3. Execution Steps with Confidence Scoring */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Cpu className="w-5 h-5 mr-2" />
                      3. Execution Steps for AI Coder
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {blueprint.execution_steps.map((step, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-semibold">Step {step.step_number}: {step.action}</h4>
                            <div className="flex gap-2">
                              <Badge className={getRiskLevelColor(step.risk_level)}>
                                {step.risk_level} Risk
                              </Badge>
                              <span className={`text-sm font-medium ${getConfidenceColor(step.confidence_score)}`}>
                                {(step.confidence_score * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{step.detailed_description}</p>
                          <Progress value={step.confidence_score * 100} className="mb-2" />
                          
                          {step.actionable_constraints.length > 0 && (
                            <div className="bg-yellow-50 p-2 rounded text-xs">
                              <strong>Critical Constraints:</strong>
                              <ul className="list-disc list-inside mt-1">
                                {step.actionable_constraints.map((constraint, i) => (
                                  <li key={i}>{constraint}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 4. Master Prompt */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Code className="w-5 h-5 mr-2" />
                      4. Master Prompt for AI Coding Agent
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="relative">
                      <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
                        {blueprint.master_prompt}
                      </pre>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="absolute top-2 right-2"
                        onClick={() => copyToClipboard(blueprint.master_prompt)}
                      >
                        <Copy className="w-3 h-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No blueprint generated yet. Enter an app idea to get started.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Enhancement Features Tab */}
          <TabsContent value="enhancements" className="space-y-6">
            {blueprint ? (
              <>
                {/* User Goal Analysis */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Users className="w-5 h-5 mr-2" />
                      CADUG: Context-Aware Goal Decomposition
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-3">
                        <div>
                          <h4 className="font-semibold text-sm text-gray-700">Core Problem</h4>
                          <p className="text-sm">{blueprint.user_goal_analysis.core_problem}</p>
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm text-gray-700">Primary Persona</h4>
                          <Badge>{blueprint.user_goal_analysis.primary_persona}</Badge>
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm text-gray-700">Key Feature</h4>
                          <p className="text-sm">{blueprint.user_goal_analysis.most_important_feature}</p>
                        </div>
                      </div>
                      <div className="space-y-3">
                        <div>
                          <h4 className="font-semibold text-sm text-gray-700">Success Metric</h4>
                          <p className="text-sm bg-green-50 p-2 rounded">{blueprint.user_goal_analysis.user_success_metric}</p>
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm text-gray-700">Inferred Motivation</h4>
                          <p className="text-sm">{blueprint.user_goal_analysis.inferred_motivation}</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Recursive Self-Improvement */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <RefreshCw className="w-5 h-5 mr-2" />
                      RSIPV: Recursive Self-Improvement Validation
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {blueprint.recursive_improvement.map((critique, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-semibold">Iteration {critique.iteration}: {critique.critique_focus}</h4>
                            <div className="flex items-center gap-2">
                              <span className="text-sm">Security Score:</span>
                              <span className={`font-bold ${getConfidenceColor(critique.security_score)}`}>
                                {(critique.security_score).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <h5 className="font-medium text-sm text-red-700 mb-2">Issues Found</h5>
                              <ul className="text-xs space-y-1">
                                {critique.issues_found.map((issue, i) => (
                                  <li key={i} className="flex items-start">
                                    <AlertTriangle className="w-3 h-3 text-red-500 mr-1 mt-0.5 flex-shrink-0" />
                                    {issue}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <h5 className="font-medium text-sm text-green-700 mb-2">Improvements Made</h5>
                              <ul className="text-xs space-y-1">
                                {critique.improvements_made.map((improvement, i) => (
                                  <li key={i} className="flex items-start">
                                    <CheckCircle className="w-3 h-3 text-green-500 mr-1 mt-0.5 flex-shrink-0" />
                                    {improvement}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Vision Analysis */}
                {blueprint.vision_analysis && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Eye className="w-5 h-5 mr-2" />
                        Multi-Modal Vision Analysis
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-semibold mb-2">Detected UI Elements</h4>
                          <div className="flex flex-wrap gap-2">
                            {blueprint.vision_analysis.ui_layout_from_vision.ui_elements_detected.map((element, index) => (
                              <Badge key={index} variant="outline">
                                {element.type}: {element.text || element.placeholder || element.purpose}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-semibold text-sm">Layout Structure</h4>
                            <p className="text-sm text-gray-600">{blueprint.vision_analysis.ui_layout_from_vision.layout_structure}</p>
                          </div>
                          <div>
                            <h4 className="font-semibold text-sm">Color Scheme</h4>
                            <p className="text-sm text-gray-600">{blueprint.vision_analysis.ui_layout_from_vision.color_scheme}</p>
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="font-semibold text-sm">User Flow</h4>
                          <p className="text-sm text-gray-600">{blueprint.vision_analysis.ui_layout_from_vision.ui_flow}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Generate a blueprint to see enhancement features in action.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* History & Export Tab */}
          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Blueprint History & Export
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Mock history data */}
                  <div className="space-y-3">
                    {[
                      { id: 'bp001', input: 'Music style extractor with AI generation', status: 'completed', timestamp: '2025-11-17 10:30' },
                      { id: 'bp002', input: 'Todo list manager with collaboration', status: 'completed', timestamp: '2025-11-17 09:15' },
                      { id: 'bp003', input: 'Weather dashboard with forecasting', status: 'completed', timestamp: '2025-11-17 08:45' }
                    ].map((item) => (
                      <div key={item.id} className="border rounded-lg p-3 flex justify-between items-center">
                        <div>
                          <h4 className="font-medium text-sm">#{item.id}</h4>
                          <p className="text-xs text-gray-600">{item.input}</p>
                          <p className="text-xs text-gray-500">{item.timestamp}</p>
                        </div>
                        <div className="flex gap-2">
                          <Badge variant="outline">{item.status}</Badge>
                          <Button variant="outline" size="sm">
                            <Download className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <Separator />
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold text-2xl text-blue-600">40+</h3>
                      <p className="text-sm text-gray-600">AI Templates Available</p>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold text-2xl text-green-600">1000+</h3>
                      <p className="text-sm text-gray-600">AI Systems Database</p>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold text-2xl text-purple-600">5</h3>
                      <p className="text-sm text-gray-600">Enhancement Features</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ProjectArchitect;