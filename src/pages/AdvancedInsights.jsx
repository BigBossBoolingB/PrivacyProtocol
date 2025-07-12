import React, { useState, useEffect } from "react";
import { PrivacyInsight, PrivacyAgreement, User } from "@/api/entities";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  Target, 
  Globe,
  Lightbulb,
  BarChart3,
  Shield,
  Eye,
  Zap
} from "lucide-react";
import { motion } from "framer-motion";
import { communityInsights } from "@/api/functions";

export default function AdvancedInsights() {
  const [insights, setInsights] = useState([]);
  const [communityData, setCommunityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('trends');

  useEffect(() => {
    loadInsights();
    loadCommunityData();
  }, []);

  const loadInsights = async () => {
    try {
      const data = await PrivacyInsight.list('-created_date', 50);
      setInsights(data);
    } catch (error) {
      console.error('Error loading insights:', error);
    }
  };

  const loadCommunityData = async () => {
    try {
      const { data } = await communityInsights();
      setCommunityData(data);
    } catch (error) {
      console.error('Error loading community data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getImpactColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'trend': return <TrendingUp className="w-5 h-5" />;
      case 'risk_pattern': return <AlertTriangle className="w-5 h-5" />;
      case 'recommendation': return <Lightbulb className="w-5 h-5" />;
      case 'industry_analysis': return <BarChart3 className="w-5 h-5" />;
      case 'regulatory_update': return <Shield className="w-5 h-5" />;
      default: return <Brain className="w-5 h-5" />;
    }
  };

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
              Advanced Privacy Intelligence
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Deep insights, predictive analysis, and cutting-edge privacy intelligence powered by AI
            </p>
          </motion.div>
        </div>

        {/* Intelligence Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-gray-900/50 border border-gray-800/50">
            <TabsTrigger value="trends" className="text-gray-400 data-[state=active]:text-white">
              <TrendingUp className="w-4 h-4 mr-2" />
              Trends
            </TabsTrigger>
            <TabsTrigger value="patterns" className="text-gray-400 data-[state=active]:text-white">
              <Brain className="w-4 h-4 mr-2" />
              Patterns
            </TabsTrigger>
            <TabsTrigger value="predictions" className="text-gray-400 data-[state=active]:text-white">
              <Zap className="w-4 h-4 mr-2" />
              Predictions
            </TabsTrigger>
            <TabsTrigger value="research" className="text-gray-400 data-[state=active]:text-white">
              <Globe className="w-4 h-4 mr-2" />
              Research
            </TabsTrigger>
          </TabsList>

          <TabsContent value="trends" className="space-y-6">
            {/* Privacy Trends */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-blue-400" />
                    Emerging Privacy Trends
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {communityData?.data_usage_trends?.slice(0, 5).map((trend, index) => (
                    <motion.div
                      key={trend.category}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
                    >
                      <span className="text-white capitalize">{trend.category}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 transition-all duration-500"
                            style={{ width: `${trend.frequency}%` }}
                          />
                        </div>
                        <span className="text-blue-400 font-medium">{trend.frequency}%</span>
                      </div>
                    </motion.div>
                  ))}
                </CardContent>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Eye className="w-5 h-5 text-purple-400" />
                    Most Tracked Data Types
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {communityData?.common_trackers?.slice(0, 5).map((tracker, index) => (
                    <motion.div
                      key={tracker.tracker}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="p-3 bg-gray-800/50 rounded-lg"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium">{tracker.tracker}</span>
                        <Badge variant="outline" className="border-purple-500/50 text-purple-400">
                          {tracker.frequency}%
                        </Badge>
                      </div>
                      <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-purple-500 transition-all duration-500"
                          style={{ width: `${tracker.frequency}%` }}
                        />
                      </div>
                    </motion.div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="patterns" className="space-y-6">
            {/* AI-Detected Patterns */}
            <div className="grid gap-6">
              {insights.filter(i => i.insight_type === 'risk_pattern').map((insight, index) => (
                <motion.div
                  key={insight.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-red-500/20 rounded-lg">
                            {getInsightIcon(insight.insight_type)}
                          </div>
                          <div>
                            <h3 className="font-semibold text-white">{insight.title}</h3>
                            <p className="text-sm text-gray-400">
                              Confidence: {insight.confidence_score}%
                            </p>
                          </div>
                        </div>
                        <Badge className={`${getImpactColor(insight.impact_level)} border`}>
                          {insight.impact_level} impact
                        </Badge>
                      </div>
                      
                      <p className="text-gray-300 mb-4">{insight.description}</p>
                      
                      {insight.actionable_steps && insight.actionable_steps.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="font-medium text-white">Recommended Actions:</h4>
                          <ul className="space-y-1">
                            {insight.actionable_steps.map((step, idx) => (
                              <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                                <Target className="w-4 h-4 mt-0.5 text-blue-400 flex-shrink-0" />
                                {step}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="predictions" className="space-y-6">
            {/* Predictive Analysis */}
            <Card className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/30 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-400" />
                  AI Predictions & Forecasts
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium text-white">Privacy Risk Forecast</h4>
                    <div className="p-4 bg-gray-800/50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400">Next 30 Days</span>
                        <span className="text-yellow-400 font-medium">Medium Risk</span>
                      </div>
                      <p className="text-sm text-gray-300">
                        Based on current trends, expect 2-3 policy changes in your monitored agreements.
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="font-medium text-white">Industry Predictions</h4>
                    <div className="p-4 bg-gray-800/50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400">Social Media</span>
                        <span className="text-red-400 font-medium">High Risk</span>
                      </div>
                      <p className="text-sm text-gray-300">
                        Social media platforms likely to introduce new data collection clauses.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                  <h4 className="font-medium text-green-400 mb-2">Emerging Opportunities</h4>
                  <p className="text-sm text-gray-300">
                    New privacy regulations in the EU may strengthen user rights across platforms. 
                    Expect better data portability options in Q2 2024.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="research" className="space-y-6">
            {/* Research & Analysis */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Globe className="w-5 h-5 text-green-400" />
                    Global Privacy Research
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-gray-800/50 rounded-lg">
                    <h4 className="font-medium text-white mb-2">GDPR Impact Analysis</h4>
                    <p className="text-sm text-gray-300 mb-3">
                      5 years post-GDPR: How European privacy laws shaped global data practices
                    </p>
                    <Badge variant="outline" className="border-green-500/50 text-green-400">
                      Research Paper
                    </Badge>
                  </div>
                  
                  <div className="p-4 bg-gray-800/50 rounded-lg">
                    <h4 className="font-medium text-white mb-2">AI Training Data Rights</h4>
                    <p className="text-sm text-gray-300 mb-3">
                      Emerging legal frameworks around AI training data and user consent
                    </p>
                    <Badge variant="outline" className="border-blue-500/50 text-blue-400">
                      Legal Analysis
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Shield className="w-5 h-5 text-purple-400" />
                    Privacy Technology Advances
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-gray-800/50 rounded-lg">
                    <h4 className="font-medium text-white mb-2">Zero-Knowledge Protocols</h4>
                    <p className="text-sm text-gray-300 mb-3">
                      How emerging cryptographic techniques could reshape data privacy
                    </p>
                    <Badge variant="outline" className="border-purple-500/50 text-purple-400">
                      Tech Report
                    </Badge>
                  </div>
                  
                  <div className="p-4 bg-gray-800/50 rounded-lg">
                    <h4 className="font-medium text-white mb-2">Decentralized Identity</h4>
                    <p className="text-sm text-gray-300 mb-3">
                      The future of user-controlled digital identity and data sovereignty
                    </p>
                    <Badge variant="outline" className="border-indigo-500/50 text-indigo-400">
                      Future Tech
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}