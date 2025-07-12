import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

export default function TrendingRisks({ risks, loading }) {
  if (loading) {
    return (
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Trending Privacy Risks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-gray-700 rounded w-3/4"></div>
                <div className="h-2 bg-gray-700 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          Trending Privacy Risks
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {risks.map((risk, index) => (
            <motion.div
              key={risk.risk}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="space-y-2"
            >
              <div className="flex justify-between items-center">
                <span className="text-white font-medium">{risk.risk}</span>
                <span className="text-gray-400 text-sm">{risk.frequency}%</span>
              </div>
              <Progress value={risk.frequency} className="h-2" />
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}