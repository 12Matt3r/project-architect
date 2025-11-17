import React, { useState } from 'react';

const SimplifiedUI = () => {
  const [userInputA, setUserInputA] = useState('');
  const [userInputB, setUserInputB] = useState('');
  const [file, setFile] = useState(null);
  const [blueprint, setBlueprint] = useState(null);
  const [randomTool, setRandomTool] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleGenerate = async () => {
    if (!userInputA.trim()) {
      alert('Please enter an app idea.');
      return;
    }

    setIsGenerating(true);
    setBlueprint(null);
    setRandomTool(null);

    try {
      const formData = new FormData();
      formData.append('user_input_a', userInputA);
      if (userInputB.trim()) {
        formData.append('user_input_b', userInputB);
      }
      if (file) {
        formData.append('file', file);
      }

      const response = await fetch('/api/v1/generate-blueprint', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to generate blueprint');
      }

      const data = await response.json();
      setBlueprint(data);
    } catch (error) {
      console.error('Error generating blueprint:', error);
      alert('Failed to generate blueprint. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRandomTool = async () => {
    setIsGenerating(true);
    setBlueprint(null);
    setRandomTool(null);

    try {
      const response = await fetch('/api/v1/tools/random');
      if (!response.ok) {
        throw new Error('Failed to fetch random tool');
      }
      const data = await response.json();
      setRandomTool(data);
    } catch (error) {
      console.error('Error fetching random tool:', error);
      alert('Failed to fetch a random tool. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const promptSuggestions = [
    "Design a complex RAG pipeline",
    "Generate a Recursive Feature Generator",
    "Create a multi-agent system for customer service",
  ];

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center' }}>Project ARCHITECT</h1>
      <div style={{ marginBottom: '20px' }}>
        <textarea
          value={userInputA}
          onChange={(e) => setUserInputA(e.target.value)}
          placeholder="Enter your first app idea here..."
          rows="4"
          style={{ width: '100%', padding: '10px', boxSizing: 'border-box' }}
        />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <textarea
          value={userInputB}
          onChange={(e) => setUserInputB(e.target.value)}
          placeholder="Enter your second app idea to fuse (optional)..."
          rows="4"
          style={{ width: '100%', padding: '10px', boxSizing: 'border-box' }}
        />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <input type="file" onChange={handleFileChange} />
      </div>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'center', gap: '10px' }}>
        <button onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating ? 'Generating...' : 'Generate Blueprint'}
        </button>
        <button onClick={handleRandomTool} disabled={isGenerating}>
          Suggest a Random Tool
        </button>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <p>Prompt Suggestions:</p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', flexWrap: 'wrap' }}>
          {promptSuggestions.map((prompt, index) => (
            <button key={index} onClick={() => setUserInputA(prompt)} style={{ background: '#f0f0f0', border: '1px solid #ccc', borderRadius: '4px', padding: '5px 10px', cursor: 'pointer' }}>
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {blueprint && (
        <div style={{ border: '1px solid #ccc', padding: '20px', whiteSpace: 'pre-wrap' }}>
          <h2>Blueprint Generated!</h2>
          <p><strong>Idea Viability Score:</strong> {blueprint.idea_viability_score}/100</p>
          {blueprint.cost_prediction && (
            <p>
              <strong>Estimated Cost:</strong> ${blueprint.cost_prediction.estimated_cost_usd} for an estimated {blueprint.cost_prediction.estimated_tokens} tokens.
            </p>
          )}
          <pre>{JSON.stringify(blueprint, null, 2)}</pre>
        </div>
      )}

      {randomTool && (
        <div style={{ border: '1px solid #ccc', padding: '20px' }}>
          <h2>Random Tool Suggestion</h2>
          <p><strong>Name:</strong> {randomTool.name}</p>
          <p><strong>Category:</strong> {randomTool.category}</p>
          <p><strong>Description:</strong> {randomTool.description}</p>
        </div>
      )}
    </div>
  );
};

export default SimplifiedUI;
