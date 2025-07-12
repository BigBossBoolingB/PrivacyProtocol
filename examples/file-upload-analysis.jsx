import React, { useState } from 'react';
import { FileUploadZone, AnalysisResults } from '@/components';
import { UploadFile, ExtractDataFromUploadedFile, riskScoreCalculator } from '@/api';

function FileUploadAnalysis() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileAnalysis = async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      const uploadResult = await UploadFile({
        file,
        type: file.type.includes('pdf') ? 'pdf' : 'doc',
        extract_text: true
      });

      const extractionResult = await ExtractDataFromUploadedFile({
        file_id: uploadResult.file_id,
        extraction_type: 'privacy_policy',
        language: 'en'
      });

      const analysis = await riskScoreCalculator({
        content: extractionResult.extracted_text,
        company_name: extractionResult.detected_company || 'Unknown Company',
        user_profile: {
          privacy_tolerance: 'strict',
          data_sensitivity: ['financial', 'health', 'biometric']
        }
      });

      setAnalysisResult(analysis);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">File Upload Analysis</h1>
      
      <FileUploadZone
        onAnalyze={handleFileAnalysis}
        acceptedTypes={['pdf', 'doc', 'docx', 'txt']}
        maxSize={10 * 1024 * 1024}
        disabled={loading}
      />

      {loading && (
        <div className="mt-6 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Processing your file...</p>
        </div>
      )}

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">Error: {error.message}</p>
        </div>
      )}

      {analysisResult && (
        <div className="mt-6">
          <AnalysisResults 
            agreement={analysisResult}
            onExport={() => console.log('Export functionality')}
            onSaveToHistory={() => console.log('Save to history')}
          />
        </div>
      )}
    </div>
  );
}

export default FileUploadAnalysis;
