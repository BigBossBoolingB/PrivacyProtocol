import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2 } from "lucide-react";
import { motion } from "framer-motion";

export default function IndustryInsights({ industries, loading }) {
  if (loading) {
    return (
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Industry Risk Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-700 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const getRiskColor = (risk) => {
    if (risk >= 70) return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (risk >= 50) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    return 'bg-green-500/20 text-green-400 border-green-500/30';
  };

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Building2 className="w-5 h-5 text-blue-400" />
          Industry Risk Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {industries.map((industry, index) => (
            <motion.div
              key={industry.industry}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50"
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-white">{industry.industry}</h4>
                <Badge className={`${getRiskColor(industry.avgRisk)} border`}>
                  {industry.avgRisk}/100
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">{industry.count.toLocaleString()} analyses</span>
                <span className={`${
                  industry.avgRisk >= 70 ? 'text-red-400' :
                  industry.avgRisk >= 50 ? 'text-orange-400' : 'text-green-400'
                }`}>
                  {industry.avgRisk >= 70 ? 'High Risk' :
                   industry.avgRisk >= 50 ? 'Medium Risk' : 'Low Risk'}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}