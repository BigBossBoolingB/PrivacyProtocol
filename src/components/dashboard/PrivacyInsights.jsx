import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, AlertTriangle, Shield, Target } from "lucide-react";
import { motion } from "framer-motion";

export default function PrivacyInsights({ agreements, profile, loading }) {
  if (loading) {
    return (
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Privacy Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-700 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const generateInsights = () => {
    if (agreements.length === 0) return [];

    const insights = [];
    const avgRisk = agreements.reduce((sum, a) => sum + (a.risk_score || 0), 0) / agreements.length;
    const highRiskCount = agreements.filter(a => (a.risk_score || 0) >= 70).length;
    
    // Risk level insight
    if (avgRisk >= 70) {
      insights.push({
        type: 'warning',
        title: 'High Risk Portfolio',
        description: `Your average risk score is ${Math.round(avgRisk)}/100. Consider reviewing high-risk agreements.`,
        icon: AlertTriangle,
        color: 'red'
      });
    } else if (avgRisk >= 40) {
      insights.push({
        type: 'info',
        title: 'Moderate Risk Level',
        description: `Your privacy risk is moderate (${Math.round(avgRisk)}/100). Some agreements may need attention.`,
        icon: Shield,
        color: 'orange'
      });
    } else {
      insights.push({
        type: 'success',
        title: 'Low Risk Portfolio',
        description: `Good news! Your average risk score is only ${Math.round(avgRisk)}/100.`,
        icon: Shield,
        color: 'green'
      });
    }

    // Data category insights
    const dataCategories = {};
    agreements.forEach(agreement => {
      agreement.data_usage_categories?.forEach(category => {
        dataCategories[category] = (dataCategories[category] || 0) + 1;
      });
    });

    const mostCommonCategory = Object.entries(dataCategories).sort((a, b) => b[1] - a[1])[0];
    if (mostCommonCategory) {
      insights.push({
        type: 'info',
        title: 'Common Data Usage',
        description: `Most agreements involve ${mostCommonCategory[0].replace(/_/g, ' ')} (${mostCommonCategory[1]} agreements).`,
        icon: Target,
        color: 'blue'
      });
    }

    // Profile-based insights
    if (profile?.privacy_tolerance === 'strict' && avgRisk > 30) {
      insights.push({
        type: 'warning',
        title: 'Profile Mismatch',
        description: 'Your strict privacy settings suggest you might want to review some agreements.',
        icon: Brain,
        color: 'purple'
      });
    }

    return insights.slice(0, 3);
  };

  const insights = generateInsights();

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Brain className="w-5 h-5 text-blue-400" />
          Privacy Insights
        </CardTitle>
      </CardHeader>
      <CardContent>
        {insights.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p>Analyze more agreements to get personalized insights.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {insights.map((insight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50"
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    insight.color === 'red' ? 'bg-red-500/20 text-red-400' :
                    insight.color === 'orange' ? 'bg-orange-500/20 text-orange-400' :
                    insight.color === 'green' ? 'bg-green-500/20 text-green-400' :
                    insight.color === 'blue' ? 'bg-blue-500/20 text-blue-400' :
                    'bg-purple-500/20 text-purple-400'
                  }`}>
                    <insight.icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-white mb-1">{insight.title}</h4>
                    <p className="text-sm text-gray-400">{insight.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}