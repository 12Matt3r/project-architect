import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Database, 
  Code, 
  Copy, 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  Sparkles,
  Terminal,
  Layers,
  FileText
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';

const CrossDatabaseQueryGenerator = () => {
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState('');
  const [queries, setQueries] = useState({
    postgresql: '',
    mysql: '',
    mongodb: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [copiedText, setCopiedText] = useState('');
  const [queryHistory, setQueryHistory] = useState([]);
  const [syntaxAnalysis, setSyntaxAnalysis] = useState({
    postgresql: { features: [], complexity: '', performance: '' },
    mysql: { features: [], complexity: '', performance: '' },
    mongodb: { features: [], complexity: '', performance: '' }
  });

  // Mock database schema information
  const sampleSchema = {
    products: ['id', 'name', 'category', 'price', 'profit_margin', 'created_at'],
    sales: ['id', 'product_id', 'quantity', 'sale_date', 'total_amount', 'quarter'],
    customers: ['id', 'name', 'email', 'age', 'income', 'region']
  };

  const databaseFeatures = {
    postgresql: {
      name: 'PostgreSQL',
      icon: '🐘',
      color: 'bg-blue-100 text-blue-800',
      features: [
        'Window functions (ROW_NUMBER, RANK)',
        'Common Table Expressions (WITH)',
        'Advanced aggregation (FILTER, GROUPING SETS)',
        'JSON/JSONB support',
        'Full-text search',
        'ACID transactions'
      ],
      syntax: 'ANSI SQL standard with extensions',
      best_for: 'Complex analytical queries, data warehousing'
    },
    mysql: {
      name: 'MySQL',
      icon: '🐬',
      color: 'bg-orange-100 text-orange-800',
      features: [
        'LIMIT and OFFSET for pagination',
        'GROUP_CONCAT for string aggregation',
        'IFNULL and COALESCE functions',
        'JSON functions',
        'InnoDB storage engine',
        'Partitioning support'
      ],
      syntax: 'ANSI SQL with MySQL-specific functions',
      best_for: 'High-performance web applications, OLTP'
    },
    mongodb: {
      name: 'MongoDB',
      icon: '🍃',
      color: 'bg-green-100 text-green-800',
      features: [
        'Aggregation pipeline ($match, $group, $project)',
        'Complex document queries with $elemMatch',
        'Array manipulation ($unwind, $push)',
        'Geographic queries ($geoNear)',
        'Text search with stemming',
        'Real-time analytics'
      ],
      syntax: 'JSON-like query document format',
      best_for: 'Document-based applications, real-time analytics'
    }
  };

  // Performance analysis data
  const performanceData = [
    { database: 'PostgreSQL', complexity: 85, performance: 90, scalability: 85 },
    { database: 'MySQL', complexity: 75, performance: 95, scalability: 90 },
    { database: 'MongoDB', complexity: 60, performance: 85, scalability: 95 }
  ];

  const analyzeSyntax = (query, database) => {
    const features = [];
    let complexity = 'Medium';
    let performance = 'Good';

    if (database === 'postgresql') {
      if (query.includes('WITH') || query.includes('ROW_NUMBER')) {
        features.push('Common Table Expression', 'Window Function');
        complexity = 'High';
      }
      if (query.includes('JSON') || query.includes('jsonb')) {
        features.push('JSON Processing');
      }
    } else if (database === 'mysql') {
      if (query.includes('GROUP_CONCAT') || query.includes('IFNULL')) {
        features.push('String Aggregation', 'Null Handling');
        complexity = 'Medium';
      }
      if (query.includes('LIMIT') && query.includes('OFFSET')) {
        features.push('Advanced Pagination');
      }
    } else if (database === 'mongodb') {
      if (query.includes('$match') || query.includes('$group')) {
        features.push('Aggregation Pipeline', 'Data Transformation');
        complexity = 'High';
        performance = 'Excellent';
      }
      if (query.includes('$elemMatch')) {
        features.push('Nested Document Query');
      }
    }

    return { features, complexity, performance };
  };

  const generateQueries = async () => {
    if (!naturalLanguageQuery.trim()) {
      setError('Please enter a natural language question');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/v1/generate-queries', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo-token'}`
        },
        body: JSON.stringify({
          question: naturalLanguageQuery,
          schema_context: sampleSchema
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setQueries(data.queries);
        
        // Analyze syntax for each database
        const analysis = {};
        Object.entries(data.queries).forEach(([db, query]) => {
          analysis[db] = analyzeSyntax(query, db);
        });
        setSyntaxAnalysis(analysis);
        
        setSuccess('Queries generated successfully!');
        setQueryHistory(prev => [
          {
            id: Date.now(),
            input: naturalLanguageQuery,
            timestamp: new Date().toLocaleString(),
            databases: Object.keys(data.queries)
          },
          ...prev.slice(0, 9) // Keep last 10 entries
        ]);
      } else {
        throw new Error(data.error || 'Failed to generate queries');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
      console.error('Query generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(label);
      setTimeout(() => setCopiedText(''), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const getComplexityColor = (complexity) => {
    switch (complexity) {
      case 'Low': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPerformanceColor = (performance) => {
    switch (performance) {
      case 'Good': return 'bg-green-100 text-green-800';
      case 'Excellent': return 'bg-blue-100 text-blue-800';
      case 'Fair': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <div className="p-3 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl">
              <Database className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Cross-Database Query Generator
            </h1>
          </div>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Transform natural language questions into optimized SQL queries for PostgreSQL, MySQL, and MongoDB
          </p>
        </div>

        {/* Input Section */}
        <Card className="border-2 border-purple-200 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50">
            <CardTitle className="flex items-center gap-2 text-purple-700">
              <Sparkles className="w-5 h-5" />
              Natural Language Input
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="e.g., 'Show the profit margin of all products sold in Q4 2023 where profit margin is above 20%'"
              value={naturalLanguageQuery}
              onChange={(e) => setNaturalLanguageQuery(e.target.value)}
              className="min-h-24 text-base"
            />
            
            <div className="flex gap-3">
              <Button 
                onClick={generateQueries}
                disabled={loading || !naturalLanguageQuery.trim()}
                className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
              >
                {loading ? (
                  <>
                    <Terminal className="w-4 h-4 mr-2 animate-spin" />
                    Generating Queries...
                  </>
                ) : (
                  <>
                    <Code className="w-4 h-4 mr-2" />
                    Generate Queries
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

            {success && (
              <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <span className="text-green-700">{success}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Sample Questions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="w-5 h-5 text-blue-500" />
              Sample Questions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {[
                "Show total sales by category for the last quarter",
                "Find customers who purchased more than 5 items",
                "Calculate average order value by region",
                "List top 10 best-selling products with their profit margins",
                "Count unique customers who made purchases in Q4",
                "Show monthly sales trends for electronics category"
              ].map((sample, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="text-left h-auto p-3 whitespace-normal"
                  onClick={() => setNaturalLanguageQuery(sample)}
                >
                  {sample}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Generated Queries */}
        {Object.values(queries).some(query => query) && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layers className="w-5 h-5 text-purple-500" />
                  Generated Queries Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="database" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="complexity" fill="#8884d8" name="Query Complexity" />
                      <Bar dataKey="performance" fill="#82ca9d" name="Performance" />
                      <Bar dataKey="scalability" fill="#ffc658" name="Scalability" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Tabs defaultValue="postgresql" className="space-y-4">
              <TabsList className="grid w-full grid-cols-3">
                {Object.entries(databaseFeatures).map(([key, db]) => (
                  <TabsTrigger 
                    key={key} 
                    value={key}
                    className="flex items-center gap-2"
                  >
                    <span className="text-lg">{db.icon}</span>
                    {db.name}
                  </TabsTrigger>
                ))}
              </TabsList>

              {Object.entries(databaseFeatures).map(([key, db]) => (
                <TabsContent key={key} value={key} className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{db.icon}</span>
                          {db.name} Query
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={db.color}>
                            {db.best_for}
                          </Badge>
                          {syntaxAnalysis[key] && (
                            <Badge className={getComplexityColor(syntaxAnalysis[key].complexity)}>
                              {syntaxAnalysis[key].complexity} Complexity
                            </Badge>
                          )}
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="relative">
                        <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto text-sm">
                          <code>{queries[key] || '// Query will appear here after generation'}</code>
                        </pre>
                        {queries[key] && (
                          <Button
                            size="sm"
                            variant="secondary"
                            className="absolute top-2 right-2"
                            onClick={() => copyToClipboard(queries[key], `${db.name} Query`)}
                          >
                            {copiedText === `${db.name} Query` ? (
                              <CheckCircle2 className="w-4 h-4" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </Button>
                        )}
                      </div>

                      {syntaxAnalysis[key] && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-semibold mb-2 flex items-center gap-2">
                              <Code className="w-4 h-4" />
                              Features Used
                            </h4>
                            <div className="flex flex-wrap gap-2">
                              {syntaxAnalysis[key].features.map((feature, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {feature}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="font-semibold mb-2 flex items-center gap-2">
                              <Database className="w-4 h-4" />
                              Performance Profile
                            </h4>
                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="text-sm">Complexity:</span>
                                <Badge className={getComplexityColor(syntaxAnalysis[key].complexity)}>
                                  {syntaxAnalysis[key].complexity}
                                </Badge>
                              </div>
                              <div className="flex items-center justify-between">
                                <span className="text-sm">Performance:</span>
                                <Badge className={getPerformanceColor(syntaxAnalysis[key].performance)}>
                                  {syntaxAnalysis[key].performance}
                                </Badge>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <h4 className="font-semibold text-blue-800 mb-2 flex items-center gap-2">
                          <Info className="w-4 h-4" />
                          {db.name} Specifics
                        </h4>
                        <p className="text-sm text-blue-700 mb-2">{db.syntax}</p>
                        <ul className="text-xs text-blue-600 space-y-1">
                          {db.features.slice(0, 3).map((feature, index) => (
                            <li key={index} className="flex items-center gap-2">
                              <span className="w-1 h-1 bg-blue-400 rounded-full"></span>
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              ))}
            </Tabs>
          </div>
        )}

        {/* Query History */}
        {queryHistory.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-purple-500" />
                Recent Queries
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {queryHistory.map((item) => (
                  <div 
                    key={item.id}
                    className="p-3 border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
                    onClick={() => setNaturalLanguageQuery(item.input)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <p className="font-medium text-slate-800 mb-1">{item.input}</p>
                        <p className="text-xs text-slate-500">{item.timestamp}</p>
                      </div>
                      <div className="flex gap-1">
                        {item.databases.map((db, index) => (
                          <span key={index} className="text-xs px-2 py-1 bg-slate-100 rounded">
                            {db}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Database Features Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5 text-purple-500" />
              Database Features Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.entries(databaseFeatures).map(([key, db]) => (
                <div key={key} className="space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{db.icon}</span>
                    <h3 className="font-semibold text-lg">{db.name}</h3>
                  </div>
                  <p className="text-sm text-slate-600">{db.syntax}</p>
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm">Key Features:</h4>
                    <ul className="text-xs space-y-1">
                      {db.features.slice(0, 4).map((feature, index) => (
                        <li key={index} className="flex items-center gap-2">
                          <span className="w-1 h-1 bg-purple-400 rounded-full"></span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <Badge className={db.color}>
                    {db.best_for}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CrossDatabaseQueryGenerator;