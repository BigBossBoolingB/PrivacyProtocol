import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";

export default function StatsCard({ title, value, icon: Icon, trend, color }) {
  const getColorClasses = (color) => {
    switch (color) {
      case 'blue':
        return 'bg-blue-500 text-blue-400';
      case 'green':
        return 'bg-green-500 text-green-400';
      case 'red':
        return 'bg-red-500 text-red-400';
      case 'orange':
        return 'bg-orange-500 text-orange-400';
      case 'purple':
        return 'bg-purple-500 text-purple-400';
      default:
        return 'bg-blue-500 text-blue-400';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm hover:bg-gray-900/70 transition-colors">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-xl ${getColorClasses(color)} bg-opacity-20`}>
              <Icon className={`w-6 h-6 ${getColorClasses(color).split(' ')[1]}`} />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-white">{value}</div>
              <div className="text-sm text-gray-400">{title}</div>
            </div>
          </div>
          {trend && (
            <div className="text-xs text-gray-500 border-t border-gray-800 pt-2">
              {trend}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}