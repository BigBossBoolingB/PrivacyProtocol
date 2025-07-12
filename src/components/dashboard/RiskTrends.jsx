import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, BarChart3 } from "lucide-react";
import { motion } from "framer-motion";

export default function RiskTrends({ agreements, loading }) {
  if (loading) {
    return (
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Risk Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse">
            <div className="h-32 bg-gray-700 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getRiskTrendData = () => {
    if (agreements.length === 0) return [];

    const grouped = agreements.reduce((acc, agreement) => {
      const month = new Date(agreement.created_date).toLocaleDateString('en-US', { month: 'short' });
      if (!acc[month]) {
        acc[month] = { total: 0, riskSum: 0 };
      }
      acc[month].total += 1;
      acc[month].riskSum += agreement.risk_score || 0;
      return acc;
    }, {});

    return Object.entries(grouped).map(([month, data]) => ({
      month,
      avgRisk: Math.round(data.riskSum / data.total),
      count: data.total
    }));
  };

  const trendData = getRiskTrendData();

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-400" />
          Risk Trends
        </CardTitle>
      </CardHeader>
      <CardContent>
        {trendData.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-600" />
            <p>Not enough data to show trends yet.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {trendData.map((item, index) => (
              <motion.div
                key={item.month}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
              >
                <div>
                  <div className="font-medium text-white">{item.month}</div>
                  <div className="text-sm text-gray-400">{item.count} analyses</div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${
                    item.avgRisk >= 70 ? 'text-red-400' : 
                    item.avgRisk >= 40 ? 'text-orange-400' : 'text-green-400'
                  }`}>
                    {item.avgRisk}
                  </div>
                  <div className="text-sm text-gray-400">avg risk</div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}