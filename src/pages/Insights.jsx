import React, { useState, useEffect } from "react";
import { PrivacyAgreement, User } from "@/api/entities";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  Shield, 
  Eye, 
  Target,
  Brain,
  Globe,
  BarChart3
} from "lucide-react";
import { motion } from "framer-motion";

import CommunityStats from "../components/insights/CommunityStats";
import TrendingRisks from "../components/insights/TrendingRisks";
import IndustryInsights from "../components/insights/IndustryInsights";
import GlobalPrivacyTrends from "../components/insights/GlobalPrivacyTrends";

export default function Insights() {
  const [agreements, setAgreements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [communityData, setCommunityData] = useState(null);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      // Load user's agreements for personalized insights
      const user = await User.me();
      const userAgreements = await PrivacyAgreement.filter(
        { created_by: user.email }, 
        '-created_date', 
        100
      );
      setAgreements(userAgreements);

      // Simulate community data (in real app, this would come from aggregated data)
      const mockCommunityData = {
        totalAnalyses: 12847,
        activeUsers: 2156,
        avgRiskScore: 62,
        topRisks: [
          { risk: 'Third-party data sharing', frequency: 87 },
          { risk: 'Unclear data retention', frequency: 73 },
          { risk: 'No explicit consent', frequency: 68 },
          { risk: 'Data selling permissions', frequency: 45 },
          { risk: 'Biometric data collection', frequency: 32 }
        ],
        industryRisks: [
          { industry: 'Social Media', avgRisk: 78, count: 1245 },
          { industry: 'E-commerce', avgRisk: 65, count: 2134 },
          { industry: 'Fintech', avgRisk: 71, count: 987 },
          { industry: 'Healthcare', avgRisk: 58, count: 567 },
          { industry: 'Education', avgRisk: 42, count: 789 }
        ],
        recentTrends: [
          { trend: 'AI data training clauses', change: '+23%', period: 'last 3 months' },
          { trend: 'Biometric data collection', change: '+15%', period: 'last 6 months' },
          { trend: 'Location tracking opt-outs', change: '-8%', period: 'last 3 months' }
        ]
      };
      setCommunityData(mockCommunityData);
    } catch (error) {
      console.error('Error loading insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPersonalizedInsights = () => {
    if (agreements.length === 0) return null;

    const avgRisk = agreements.reduce((sum, a) => sum + (a.risk_score || 0), 0) / agreements.length;
    const highRiskCount = agreements.filter(a => (a.risk_score || 0) >= 70).length;
    const commonRisks = {};

    agreements.forEach(agreement => {
      agreement.flagged_clauses?.forEach(clause => {
        commonRisks[clause.risk_level] = (commonRisks[clause.risk_level] || 0) + 1;
      });
    });

    return {
      avgRisk: Math.round(avgRisk),
      highRiskCount,
      totalAnalyses: agreements.length,
      commonRisks
    };
  };

  const personalInsights = getPersonalizedInsights();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-2"
          >
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Community Insights
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Collective intelligence from privacy analyses worldwide
            </p>
          </motion.div>
        </div>

        {/* Your Privacy Profile vs Community */}
        {personalInsights && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/30 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Target className="w-5 h-5 text-blue-400" />
                  Your Privacy Profile vs Community
                </CardTitle>
              </CardHeader>
              <CardContent className="grid md:grid-cols-3 gap-6">
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-blue-400">{personalInsights.avgRisk}</div>
                  <div className="text-sm text-gray-400">Your Avg Risk Score</div>
                  <div className="text-xs text-gray-500">
                    Community: {communityData?.avgRiskScore || 62}
                  </div>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-purple-400">{personalInsights.totalAnalyses}</div>
                  <div className="text-sm text-gray-400">Your Analyses</div>
                  <div className="text-xs text-gray-500">
                    Community: {communityData?.totalAnalyses?.toLocaleString() || '12,847'}
                  </div>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-indigo-400">{personalInsights.highRiskCount}</div>
                  <div className="text-sm text-gray-400">High Risk Agreements</div>
                  <div className="text-xs text-gray-500">
                    {Math.round((personalInsights.highRiskCount / personalInsights.totalAnalyses) * 100)}% of your portfolio
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Community Stats */}
        <div className="grid lg:grid-cols-2 gap-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <CommunityStats 
              data={communityData} 
              loading={loading}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <TrendingRisks 
              risks={communityData?.topRisks || []}
              loading={loading}
            />
          </motion.div>
        </div>

        {/* Industry Insights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <IndustryInsights 
            industries={communityData?.industryRisks || []}
            loading={loading}
          />
        </motion.div>

        {/* Global Privacy Trends */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <GlobalPrivacyTrends 
            trends={communityData?.recentTrends || []}
            loading={loading}
          />
        </motion.div>

        {/* Privacy Protocol Mission */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card className="bg-gradient-to-r from-slate-900 to-slate-800 border-gray-700/50 backdrop-blur-sm">
            <CardContent className="p-8 text-center space-y-4">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white">
                Building Digital Sovereignty Together
              </h3>
              <p className="text-gray-400 max-w-2xl mx-auto">
                Every privacy agreement you analyze contributes to our collective understanding of digital rights. 
                Together, we're building a more transparent and equitable digital ecosystem.
              </p>
              <div className="flex justify-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-blue-400" />
                  <span className="text-gray-400">Global Impact</span>
                </div>
                <div className="flex items-center gap-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <span className="text-gray-400">AI-Powered</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-indigo-400" />
                  <span className="text-gray-400">Community-Driven</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}