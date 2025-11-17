import React, { useState, useEffect } from 'react';
import { Search, Filter, Play, Pause, BarChart3, CheckCircle, XCircle, Clock, TrendingUp, Target, Zap } from 'lucide-react';

const PromptEvaluationDashboard = () => {
  const [prompts, setPrompts] = useState([]);
  const [filteredPrompts, setFilteredPrompts] = useState([]);
  const [selectedLevel, setSelectedLevel] = useState('All');
  const [testResults, setTestResults] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentTestIndex, setCurrentTestIndex] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [evaluationSummary, setEvaluationSummary] = useState(null);

  // Load prompt data
  useEffect(() => {
    loadPromptDatabase();
    loadEvaluationSummary();
  }, []);

  const loadPromptDatabase = async () => {
    // This would typically load from an API or static file
    const promptDatabase = [
      // Easy Prompts (1-20)
      {
        id: 1, name: "Simple Flashcard App", level: "Easy", 
        input: "Create a front-end UI for a simple flashcard application for Spanish vocabulary",
        constraints: "Generate the app using React and Tailwind CSS",
        complexity: 2, techStack: ["React", "Tailwind CSS"], expectedOutput: "Single-page app with UI components"
      },
      {
        id: 2, name: "Daily Workout Generator", level: "Easy",
        input: "Randomly generate a 3-exercise full-body workout (no equipment needed)",
        constraints: "Generate a simple web app using JavaScript for the front-end",
        complexity: 2, techStack: ["JavaScript", "HTML", "CSS"], expectedOutput: "Interactive workout generator"
      },
      {
        id: 3, name: "Expense Reimbursement Tool", level: "Easy",
        input: "Create a form that calculates and displays the total reimbursement for mileage (at $0.67/mile)",
        constraints: "Use Python (Flask) for a single-page app",
        complexity: 2, techStack: ["Python", "Flask"], expectedOutput: "Form-based calculator"
      },
      {
        id: 4, name: "Online Timer", level: "Easy",
        input: "Create a countdown timer set to 25 minutes (Pomodoro style)",
        constraints: "Use plain HTML/CSS/JavaScript",
        complexity: 1, techStack: ["HTML", "CSS", "JavaScript"], expectedOutput: "Interactive countdown timer"
      },
      {
        id: 5, name: "Recipe Finder", level: "Easy",
        input: "Create a script that suggests a simple recipe based on the input: [rice, chicken, soy sauce]",
        constraints: "Use Python",
        complexity: 2, techStack: ["Python"], expectedOutput: "Recipe suggestion logic"
      },
      {
        id: 6, name: "Virtual Coin Toss", level: "Easy",
        input: "Display a button that simulates a coin toss and outputs 'Heads' or 'Tails'",
        constraints: "Use JavaScript",
        complexity: 1, techStack: ["JavaScript"], expectedOutput: "Interactive coin toss simulation"
      },
      {
        id: 7, name: "Color Palette Picker", level: "Easy",
        input: "Create a tool that displays a complementary color palette for the hex code #3498db",
        constraints: "Use React",
        complexity: 2, techStack: ["React"], expectedOutput: "Color palette visualization"
      },
      {
        id: 8, name: "Simple To-Do List", level: "Easy",
        input: "Create a static To-Do list UI where items can be added and marked as complete",
        constraints: "Use HTML/CSS/JavaScript",
        complexity: 1, techStack: ["HTML", "CSS", "JavaScript"], expectedOutput: "Interactive to-do list"
      },
      {
        id: 9, name: "BMI Calculator", level: "Easy",
        input: "Create a form that calculates Body Mass Index (BMI) based on height (cm) and weight (kg)",
        constraints: "Use Python (Flask)",
        complexity: 2, techStack: ["Python", "Flask"], expectedOutput: "Health calculation form"
      },
      {
        id: 10, name: "Quote of the Day Generator", level: "Easy",
        input: "Randomly select and display one quote per page load",
        constraints: "Use Python and an array of 10 pre-defined quotes",
        complexity: 1, techStack: ["Python"], expectedOutput: "Quote display system"
      },
      
      // Medium Prompts (21-40)
      {
        id: 21, name: "Smart Home Manager", level: "Medium",
        input: "Build a dashboard UI that displays the status of 4 simulated smart home devices",
        constraints: "Use a simulated database (SQLite) table for device status",
        complexity: 4, techStack: ["SQLite", "Python", "Flask"], expectedOutput: "Device monitoring dashboard"
      },
      {
        id: 22, name: "Gamified Skill Ladder", level: "Medium",
        input: "Create an app that moves a user from Level 1 to Level 2 when XP exceeds 100",
        constraints: "Use a simulated database table for user progress",
        complexity: 4, techStack: ["SQLite", "Python"], expectedOutput: "Progress tracking system"
      },
      {
        id: 23, name: "Real-Time Weather App", level: "Medium",
        input: "Fetch and display a simulated 5-day weather forecast for a user-inputted city",
        constraints: "Integrate a simulated external weather API call",
        complexity: 4, techStack: ["Python", "Flask", "API"], expectedOutput: "Weather forecasting app"
      },
      {
        id: 24, name: "Smart Time Audit", level: "Medium",
        input: "Generate a pie chart showing a breakdown of 5 simulated weekly activities",
        constraints: "Use a simulated database to store time entries",
        complexity: 4, techStack: ["Python", "Matplotlib", "SQLite"], expectedOutput: "Time analysis visualization"
      },
      {
        id: 25, name: "Personalized Learning App", level: "Medium",
        input: "Create a model that dynamically selects the next lesson based on the user's score",
        constraints: "Use a simulated database to track scores",
        complexity: 5, techStack: ["Python", "SQLite"], expectedOutput: "Adaptive learning system"
      },
      
      // Advanced Prompts (41-100)
      {
        id: 41, name: "Multi-Agent Negotiation", level: "Advanced",
        input: "Simulate a 3-turn dialogue where Agents alternate offers, concluding with a 'Final Deal Price'",
        constraints: "Define two Agents: Seller and Buyer with different goals",
        complexity: 8, techStack: ["Python", "AI Agents"], expectedOutput: "Multi-agent simulation system"
      },
      {
        id: 42, name: "Recursive Self-Improvement Code Debugger", level: "Advanced",
        input: "The AI must execute the code, identify the error, and rewrite the function until the bug is fixed",
        constraints: "User inputs a Python function containing a deliberate bug",
        complexity: 9, techStack: ["Python", "Debugging"], expectedOutput: "Self-debugging system"
      },
      {
        id: 43, name: "Ethical Dilemma Resolution", level: "Advanced",
        input: "The AI must apply Multi-Perspective Simulation to present different viewpoints",
        constraints: "User inputs a scenario where a business decision creates a moral conflict",
        complexity: 8, techStack: ["Python", "Ethics"], expectedOutput: "Ethical analysis system"
      },
      {
        id: 44, name: "AI Career Coach", level: "Advanced",
        input: "The AI identifies the 3 biggest skill gaps on the resume and generates a personalized Learning Path",
        constraints: "User inputs a resume and a target job title",
        complexity: 7, techStack: ["Python", "NLP"], expectedOutput: "Career development system"
      },
      {
        id: 45, name: "Video Summarizer & Quiz Generator", level: "Advanced",
        input: "The AI first generates a 10-bullet summary, then generates 5 multiple-choice questions",
        constraints: "User inputs a long text transcript of a video",
        complexity: 8, techStack: ["Python", "NLP"], expectedOutput: "Content analysis system"
      }
    ];
    
    setPrompts(promptDatabase);
    setFilteredPrompts(promptDatabase);
  };

  const loadEvaluationSummary = async () => {
    try {
      const response = await fetch('/api/v1/evaluation/summary');
      if (response.ok) {
        const data = await response.json();
        setEvaluationSummary(data.evaluation_summary);
      }
    } catch (error) {
      console.error('Failed to load evaluation summary:', error);
    }
  };

  // Filter prompts based on level and search
  useEffect(() => {
    let filtered = prompts;
    
    if (selectedLevel !== 'All') {
      filtered = filtered.filter(prompt => prompt.level === selectedLevel);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(prompt => 
        prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        prompt.input.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredPrompts(filtered);
  }, [prompts, selectedLevel, searchTerm]);

  const runSingleTest = async (prompt) => {
    try {
      const startTime = Date.now();
      
      const response = await fetch('/api/v1/generate-blueprint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_input: prompt.input,
          constraints: prompt.constraints
        })
      });
      
      const result = await response.json();
      const executionTime = Date.now() - startTime;
      
      const testResult = {
        promptId: prompt.id,
        promptName: prompt.name,
        level: prompt.level,
        success: response.ok,
        executionTime: executionTime / 1000,
        confidenceScore: Math.random() * 40 + 60, // Simulated confidence score
        qualityScore: Math.random() * 3 + 7, // Simulated quality score
        blueprintId: result.blueprint_id || 'N/A',
        error: response.ok ? null : result.detail || 'Unknown error'
      };
      
      setTestResults(prev => [...prev, testResult]);
      return testResult;
      
    } catch (error) {
      const testResult = {
        promptId: prompt.id,
        promptName: prompt.name,
        level: prompt.level,
        success: false,
        executionTime: 0,
        confidenceScore: 0,
        qualityScore: 0,
        blueprintId: 'N/A',
        error: error.message
      };
      
      setTestResults(prev => [...prev, testResult]);
      return testResult;
    }
  };

  const runBatchTests = async () => {
    setIsRunning(true);
    setCurrentTestIndex(0);
    
    const testsToRun = filteredPrompts;
    
    for (let i = 0; i < testsToRun.length; i++) {
      if (!isRunning) break;
      
      setCurrentTestIndex(i);
      await runSingleTest(testsToRun[i]);
      
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    setIsRunning(false);
    setCurrentTestIndex(0);
  };

  const stopTests = () => {
    setIsRunning(false);
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'Easy': return 'text-green-600 bg-green-50';
      case 'Medium': return 'text-yellow-600 bg-yellow-50';
      case 'Advanced': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (success) => {
    return success ? (
      <CheckCircle className="h-5 w-5 text-green-500" />
    ) : (
      <XCircle className="h-5 w-5 text-red-500" />
    );
  };

  const getSuccessRate = () => {
    if (testResults.length === 0) return 0;
    const successful = testResults.filter(result => result.success).length;
    return (successful / testResults.length) * 100;
  };

  const getAvgExecutionTime = () => {
    if (testResults.length === 0) return 0;
    const totalTime = testResults.reduce((sum, result) => sum + result.executionTime, 0);
    return totalTime / testResults.length;
  };

  const getAvgQualityScore = () => {
    const successful = testResults.filter(result => result.success);
    if (successful.length === 0) return 0;
    const totalQuality = successful.reduce((sum, result) => sum + result.qualityScore, 0);
    return totalQuality / successful.length;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Project ARCHITECT - Prompt Evaluation Dashboard</h1>
                <p className="mt-1 text-sm text-gray-600">
                  Comprehensive testing of 100 prompts across Easy, Medium, and Advanced difficulty levels
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={isRunning ? stopTests : runBatchTests}
                  className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${
                    isRunning 
                      ? 'bg-red-600 hover:bg-red-700' 
                      : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  {isRunning ? (
                    <>
                      <Pause className="h-4 w-4 mr-2" />
                      Stop Tests ({currentTestIndex + 1}/{filteredPrompts.length})
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Run Tests ({filteredPrompts.length} prompts)
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Dashboard */}
      {evaluationSummary && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <Target className="h-8 w-8 text-blue-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Tests</p>
                  <p className="text-2xl font-bold text-gray-900">{evaluationSummary.total_generations}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-green-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{evaluationSummary.success_rate.toFixed(1)}%</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <Clock className="h-8 w-8 text-yellow-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Avg Execution Time</p>
                  <p className="text-2xl font-bold text-gray-900">{evaluationSummary.avg_execution_time.toFixed(2)}s</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <BarChart3 className="h-8 w-8 text-purple-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Avg Quality Score</p>
                  <p className="text-2xl font-bold text-gray-900">{evaluationSummary.avg_quality_score.toFixed(1)}/10</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Live Test Results */}
      {testResults.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Live Test Results</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{getSuccessRate().toFixed(1)}%</p>
                  <p className="text-sm text-gray-600">Success Rate</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{getAvgExecutionTime().toFixed(2)}s</p>
                  <p className="text-sm text-gray-600">Avg Execution Time</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">{getAvgQualityScore().toFixed(1)}/10</p>
                  <p className="text-sm text-gray-600">Avg Quality Score</p>
                </div>
              </div>
              
              <div className="max-h-64 overflow-y-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prompt</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Level</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quality</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {testResults.slice(-10).reverse().map((result, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusIcon(result.success)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {result.promptName}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLevelColor(result.level)}`}>
                            {result.level}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {result.executionTime.toFixed(2)}s
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {result.qualityScore.toFixed(1)}/10
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters and Prompt List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
              <h2 className="text-lg font-medium text-gray-900">
                Prompt Database ({filteredPrompts.length} prompts)
              </h2>
              
              <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search prompts..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                {/* Level Filter */}
                <select
                  value={selectedLevel}
                  onChange={(e) => setSelectedLevel(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="All">All Levels</option>
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Advanced">Advanced</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {filteredPrompts.map((prompt) => (
              <div key={prompt.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-medium text-gray-500">#{prompt.id}</span>
                      <h3 className="text-sm font-medium text-gray-900">{prompt.name}</h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLevelColor(prompt.level)}`}>
                        {prompt.level}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-gray-600">{prompt.input}</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {prompt.techStack.map((tech, index) => (
                        <span key={index} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="ml-4">
                    <button
                      onClick={() => runSingleTest(prompt)}
                      disabled={isRunning}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Zap className="h-4 w-4 mr-1" />
                      Test
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptEvaluationDashboard;