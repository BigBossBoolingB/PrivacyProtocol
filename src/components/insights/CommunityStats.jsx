import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Activity, BarChart3, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";

export default function CommunityStats({ data, loading }) {
  if (loading || !data) {
    return (
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Community Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-700 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const stats = [
    {
      title: "Total Analyses",
      value: data.totalAnalyses.toLocaleString(),
      icon: BarChart3,
      color: "text-blue-400"
    },
    {
      title: "Active Users",
      value: data.activeUsers.toLocaleString(),
      icon: Users,
      color: "text-green-400"
    },
    {
      title: "Avg Risk Score",
      value: `${data.avgRiskScore}/100`,
      icon: Activity,
      color: "text-orange-400"
    },
    {
      title: "This Month",
      value: "+1,247",
      icon: TrendingUp,
      color: "text-purple-400"
    }
  ];

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Users className="w-5 h-5 text-blue-400" />
          Community Statistics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50 text-center"
            >
              <div className={`w-8 h-8 mx-auto mb-2 ${stat.color}`}>
                <stat.icon className="w-full h-full" />
              </div>
              <div className="text-lg font-bold text-white">{stat.value}</div>
              <div className="text-sm text-gray-400">{stat.title}</div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}