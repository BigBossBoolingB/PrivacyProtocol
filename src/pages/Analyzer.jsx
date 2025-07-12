
import React, { useState, useRef, useEffect } from "react";
import { PrivacyAgreement, User } from "@/api/entities";
import { UploadFile, ExtractDataFromUploadedFile, InvokeLLM } from "@/api/integrations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Upload,
  Link as LinkIcon,
  FileText,
  Loader2,
  AlertCircle,
  Shield,
  Zap,
  Brain,
  Search
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { createPageUrl } from "@/utils";
import { analyzePolicyText, calculateRiskScore, extractClauses } from "@/utils/webWorkers";

import FileUploadZone from "../components/analyzer/FileUploadZone";
import URLAnalyzer from "../components/analyzer/URLAnalyzer";
import AnalysisResults from "../components/analyzer/AnalysisResults";
import { subscriptionManager } from "@/api/functions";
import { riskScoreCalculator } from "@/api/functions";
import UpgradePrompt from "../components/subscription/UpgradePrompt";
import SubscriptionModal from "../components/subscription/SubscriptionModal";

export default function Analyzer() {
  const navigate = useNavigate();
  const [analysisMode, setAnalysisMode] = useState('file'); // 'file' or 'url'
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysisStep, setAnalysisStep] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  useEffect(() => {
    checkSubscription();
  }, []);

  const checkSubscription = async () => {
    try {
      const { data } = await subscriptionManager({ action: 'check_usage_limits' });
      setSubscriptionData(data);
    } catch (error) {
      console.error('Error checking subscription:', error);
      // Optionally set an error state or display a message to the user
    }
  };

  const handleAnalysisAttempt = async () => {
    // Check if user can perform analysis
    if (subscriptionData && !subscriptionData.usage.can_analyze) {
      setShowUpgradeModal(true);
      return false;
    }
    return true;
  };

  const analyzePrivacyAgreement = async (content, title, url = null, fileUrl = null) => {
    // Check subscription limits before analysis
    const canAnalyze = await handleAnalysisAttempt();
    if (!canAnalyze) {
      setIsAnalyzing(false); // Ensure analysis state is reset if blocked
      return; // Stop the function execution
    }

    setIsAnalyzing(true);
    setProgress(0);
    setError(null);
    setResults(null);

    try {
      // Step 1: Extract and analyze content
      setAnalysisStep('Extracting content...');
      setProgress(20);

      // Step 2: Use Web Worker for heavy text analysis
      setAnalysisStep('Analyzing text structure...');
      setProgress(30);
      
      const textAnalysis = await analyzePolicyText(content, {
        includeReadability: true,
        extractKeyTerms: true
      });

      setAnalysisStep('Extracting privacy clauses...');
      setProgress(35);
      
      const extractedClauses = await extractClauses(content);

      // Step 3: AI Analysis
      setAnalysisStep('AI analyzing privacy risks...');
      setProgress(40);

      const analysisPrompt = `
        You are PrivacyProtocol's AI engine, a world-class expert in privacy law and data protection. Your task is to perform a deep, detailed analysis of a privacy policy.

        Analyze the following privacy agreement content and provide a comprehensive assessment. Be extremely thorough and detailed in your response.

        CONTENT TO ANALYZE:
        ${content}

        Provide the analysis in a structured JSON format. Here are the required fields:

        1.  **analysis_summary**: A concise, executive summary of the key findings and overall privacy posture.
        2.  **flagged_clauses**: Identify problematic clauses. For each clause:
            *   **clause_text**: The exact text of the clause.
            *   **risk_level**: 'low', 'medium', 'high', or 'critical'.
            *   **explanation**: A detailed explanation of why this clause is a risk.
            *   **plain_language**: Translate the legalese into simple, easy-to-understand language.
            *   **what_if_scenario**: Describe a realistic negative "what if" scenario that could result from this clause.
        3.  **data_collection_breakdown**: A boolean checklist of specific data types collected. The keys are: "contact_info", "financial_info", "health_info", "location_info", "biometric_info", "usage_data", "device_info", "user_content".
        4.  **data_usage_categories**: A list of general data usage categories from this enum: ["personal_info", "tracking", "advertising", "third_party_sharing", "data_selling", "profiling", "location", "biometric", "financial", "health"].
        5.  **third_party_trackers**: A list of specific third-party companies, services, or trackers mentioned (e.g., "Google Analytics", "Meta Pixel").
        6.  **data_retention_policy**: A brief summary of their data retention policy (e.g., "Indefinite", "Until account deletion", "90 days after inactivity").
        7.  **user_rights_summary**: A boolean checklist of user rights explicitly granted. The keys are: "data_access", "data_deletion", "data_portability", "opt_out_of_sale".
        8.  **recommendations**: A list of actionable recommendations for the user. For each recommendation:
            *   **action**: A short title for the action.
            *   **description**: A clear explanation of what to do.
            *   **priority**: 'low', 'medium', 'high', or 'urgent'.
            *   **category**: 'settings_change', 'account_action', 'awareness', or 'external_tool'.
        9. **opt_out_options**: A list of available opt-out mechanisms. For each:
            *   **type**: The type of opt-out (e.g., "Ad Personalization").
            *   **url**: A direct URL if available.
            *   **instructions**: How to perform the opt-out.

        Your analysis must be rigorous, precise, and user-centric, prioritizing the user's digital sovereignty.
      `;

      const analysisResult = await InvokeLLM({
        prompt: analysisPrompt,
        response_json_schema: {
          type: "object",
          properties: {
            analysis_summary: { type: "string" },
            flagged_clauses: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  clause_text: { type: "string" },
                  risk_level: { type: "string", enum: ["low", "medium", "high", "critical"] },
                  explanation: { type: "string" },
                  plain_language: { type: "string" },
                  what_if_scenario: { type: "string" }
                },
                required: ["clause_text", "risk_level", "explanation", "plain_language", "what_if_scenario"]
              }
            },
            data_collection_breakdown: {
              type: "object",
              properties: {
                contact_info: { type: "boolean" },
                financial_info: { type: "boolean" },
                health_info: { type: "boolean" },
                location_info: { type: "boolean" },
                biometric_info: { type: "boolean" },
                usage_data: { type: "boolean" },
                device_info: { type: "boolean" },
                user_content: { type: "boolean" }
              }
            },
            data_usage_categories: {
              type: "array",
              items: { type: "string", enum: ["personal_info", "tracking", "advertising", "third_party_sharing", "data_selling", "profiling", "location", "biometric", "financial", "health"] }
            },
            third_party_trackers: { type: "array", items: { "type": "string" } },
            data_retention_policy: { type: "string" },
            user_rights_summary: {
              type: "object",
              properties: {
                data_access: { type: "boolean" },
                data_deletion: { type: "boolean" },
                data_portability: { type: "boolean" },
                opt_out_of_sale: { type: "boolean" }
              }
            },
            recommendations: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  action: { type: "string" },
                  description: { type: "string" },
                  priority: { type: "string", enum: ["low", "medium", "high", "urgent"] },
                  category: { type: "string", enum: ["settings_change", "account_action", "awareness", "external_tool"] }
                }
              }
            },
            opt_out_options: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  type: { type: "string" },
                  url: { type: "string" },
                  instructions: { type: "string" }
                }
              }
            }
          },
          required: ["analysis_summary", "flagged_clauses", "data_collection_breakdown", "data_usage_categories", "third_party_trackers", "data_retention_policy", "user_rights_summary", "recommendations", "opt_out_options"]
        }
      });

      setAnalysisStep('Calculating personalized risk score...');
      setProgress(60);

      // Step 4: Calculate Risk Score with Web Worker and dedicated function
      const webWorkerRiskAnalysis = await calculateRiskScore(extractedClauses);
      const { data: riskData } = await riskScoreCalculator({ 
        agreementData: analysisResult,
        preAnalysis: {
          textAnalysis,
          extractedClauses,
          webWorkerRiskAnalysis
        }
      });
      
      setAnalysisStep('Generating insights...');
      setProgress(80);

      // Step 5: Save results
      setAnalysisStep('Saving analysis...');
      setProgress(90);

      const agreementData = {
        title,
        company: title,
        url: url || '',
        file_url: fileUrl || '',
        risk_score: riskData.risk_score,
        analysis_summary: analysisResult.analysis_summary,
        flagged_clauses: analysisResult.flagged_clauses || [],
        data_usage_categories: analysisResult.data_usage_categories || [],
        data_collection_breakdown: analysisResult.data_collection_breakdown || {},
        third_party_trackers: analysisResult.third_party_trackers || [],
        data_retention_policy: analysisResult.data_retention_policy || 'Not specified',
        user_rights_summary: analysisResult.user_rights_summary || {},
        recommendations: analysisResult.recommendations || [],
        opt_out_options: analysisResult.opt_out_options || [],
        textAnalysis,
        extractedClauses,
        webWorkerRiskAnalysis,
        status: 'completed'
      };

      const savedAgreement = await PrivacyAgreement.create(agreementData);

      // Update usage count after successful analysis
      if (subscriptionData?.subscription) {
        await subscriptionManager({
          action: 'increment_usage',
          data: { subscription_id: subscriptionData.subscription.id }
        });
        await checkSubscription(); // Refresh subscription data
      }

      setProgress(100);
      setResults(savedAgreement);
      setAnalysisStep('Analysis complete!');

    } catch (error) {
      console.error('Analysis error:', error);
      setError(error.message || 'Failed to analyze privacy agreement');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileUpload = async (file) => {
    try {
      const { file_url } = await UploadFile({ file });

      const extractResult = await ExtractDataFromUploadedFile({
        file_url,
        json_schema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "Full text content of the privacy agreement"
            },
            title: {
              type: "string",
              description: "Title or company name from the document"
            }
          }
        }
      });

      if (extractResult.status === 'success' && extractResult.output) {
        await analyzePrivacyAgreement(
          extractResult.output.content,
          extractResult.output.title || file.name,
          null,
          file_url
        );
      } else {
        throw new Error('Could not extract content from file');
      }
    } catch (error) {
      setError(error.message || 'Failed to process file');
    }
  };

  const handleUrlAnalysis = async (url, title) => {
    try {
      const fetchPrompt = `
        Please fetch and extract the complete privacy policy content from this URL: ${url}

        Extract the full text content of the privacy policy or terms of service.
        Focus on getting all the important privacy-related sections.
      `;

      const fetchResult = await InvokeLLM({
        prompt: fetchPrompt,
        add_context_from_internet: true,
        response_json_schema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "Full privacy policy content"
            },
            extracted_title: {
              type: "string",
              description: "Company or service name"
            }
          }
        }
      });

      if (fetchResult.content) {
        await analyzePrivacyAgreement(
          fetchResult.content,
          title || fetchResult.extracted_title || 'Privacy Policy',
          url
        );
      } else {
        throw new Error('Could not fetch privacy policy content from URL');
      }
    } catch (error) {
      setError(error.message || 'Failed to analyze URL');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-2"
          >
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Privacy Agreement Analyzer
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Upload documents or paste URLs to decode privacy policies with AI-powered analysis
            </p>
          </motion.div>
        </div>

        {/* Analysis Mode Toggle */}
        <div className="flex justify-center">
          <div className="bg-gray-900/50 p-1 rounded-xl border border-gray-800/50">
            <Button
              variant={analysisMode === 'file' ? 'default' : 'ghost'}
              onClick={() => setAnalysisMode('file')}
              className={analysisMode === 'file' ? 'bg-blue-500 hover:bg-blue-600' : 'text-gray-400 hover:text-white'}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload File
            </Button>
            <Button
              variant={analysisMode === 'url' ? 'default' : 'ghost'}
              onClick={() => setAnalysisMode('url')}
              className={analysisMode === 'url' ? 'bg-blue-500 hover:bg-blue-600' : 'text-gray-400 hover:text-white'}
            >
              <LinkIcon className="w-4 h-4 mr-2" />
              Analyze URL
            </Button>
          </div>
        </div>

        {/* Usage Limit Warning */}
        {subscriptionData && !subscriptionData.usage.can_analyze && (
          <UpgradePrompt
            type="limit"
            onUpgrade={() => setShowUpgradeModal(true)}
          />
        )}

        {/* Error Alert */}
        {error && (
          <Alert className="border-red-500/50 bg-red-500/10">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-400">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Analysis Interface */}
        <AnimatePresence mode="wait">
          {!isAnalyzing && !results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {analysisMode === 'file' ? (
                <FileUploadZone onFileUpload={handleFileUpload} />
              ) : (
                <URLAnalyzer onAnalyze={handleUrlAnalysis} />
              )}
            </motion.div>
          )}

          {isAnalyzing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardContent className="p-8">
                  <div className="text-center space-y-6">
                    <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                      <Brain className="w-8 h-8 text-white animate-pulse" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-2">AI Analysis In Progress</h3>
                      <p className="text-gray-400">{analysisStep}</p>
                    </div>
                    <div className="space-y-2">
                      <Progress value={progress} className="h-2" />
                      <p className="text-sm text-gray-500">{progress}% Complete</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <AnalysisResults
                agreement={results}
                onNewAnalysis={() => {
                  setResults(null);
                  setError(null);
                  setProgress(0);
                  setAnalysisStep('');
                  checkSubscription(); // Re-check subscription after completing an analysis or starting a new one
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Subscription Modal */}
        <SubscriptionModal
          open={showUpgradeModal}
          onClose={() => setShowUpgradeModal(false)}
        />
      </div>
    </div>
  );
}
