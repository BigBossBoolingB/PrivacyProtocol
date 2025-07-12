import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Globe, TrendingUp, TrendingDown } from "lucide-react";
import { motion } from "framer-motion";

export default function GlobalPrivacyTrends({ trends, loading }) {
  if (loading) {
    return (
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Global Privacy Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-700 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const getTrendIcon = (change) => {
    return change.startsWith('+') ? TrendingUp : TrendingDown;
  };

  const getTrendColor = (change) => {
    return change.startsWith('+') ? 'text-red-400' : 'text-green-400';
  };

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Globe className="w-5 h-5 text-blue-400" />
          Global Privacy Trends
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {trends.map((trend, index) => {
            const TrendIcon = getTrendIcon(trend.change);
            return (
              <motion.div
                key={trend.trend}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-white mb-1">{trend.trend}</h4>
                    <p className="text-sm text-gray-400">{trend.period}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendIcon className={`w-4 h-4 ${getTrendColor(trend.change)}`} />
                    <Badge 
                      variant="outline" 
                      className={`${getTrendColor(trend.change)} border-current`}
                    >
                      {trend.change}
                    </Badge>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}