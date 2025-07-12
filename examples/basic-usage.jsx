import React, { useState } from 'react';
import { useApiQuery } from '@/hooks';
import { riskScoreCalculator } from '@/api/functions';
import { AnalysisResults, LoadingSpinner, ErrorAlert } from '@/components';

function BasicPolicyAnalysis() {
  const [policyContent, setPolicyContent] = useState('');
  const [companyName, setCompanyName] = useState('');
  
  const { 
    data: analysisResult, 
    loading, 
    error,
    refetch: analyzePolicy 
  } = useApiQuery(
    ['policy-analysis', policyContent, companyName],
    () => riskScoreCalculator({
      content: policyContent,
      company_name: companyName,
      user_profile: {
        privacy_tolerance: 'moderate'
      }
    }),
    { enabled: false }
  );

  const handleAnalyze = () => {
    if (policyContent && companyName) {
      analyzePolicy();
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Privacy Policy Analysis</h1>
      
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            Company Name
          </label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full p-2 border rounded-md"
            placeholder="Enter company name"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">
            Privacy Policy Content
          </label>
          <textarea
            value={policyContent}
            onChange={(e) => setPolicyContent(e.target.value)}
            className="w-full p-2 border rounded-md h-32"
            placeholder="Paste privacy policy content here"
          />
        </div>
        
        <button
          onClick={handleAnalyze}
          disabled={!policyContent || !companyName || loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Analyze Policy'}
        </button>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorAlert error={error} />}
      {analysisResult && <AnalysisResults agreement={analysisResult} />}
    </div>
  );
}

export default BasicPolicyAnalysis;
