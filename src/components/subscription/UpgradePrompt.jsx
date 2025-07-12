import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Crown, Zap, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

export default function UpgradePrompt({ onUpgrade, type = "limit", customMessage }) {
  const prompts = {
    limit: {
      icon: AlertTriangle,
      title: "Analysis Limit Reached",
      message: "You've reached your monthly analysis limit. Upgrade to Premium for unlimited analyses.",
      buttonText: "Upgrade for $1.99/month",
      color: "orange"
    },
    feature: {
      icon: Crown,
      title: "Premium Feature",
      message: customMessage || "This feature is available with Premium subscription.",
      buttonText: "Unlock Premium Features",
      color: "blue"
    },
    monitor: {
      icon: Zap,
      title: "Real-time Monitoring",
      message: "Enable 24/7 policy monitoring and instant alerts with Premium.",
      buttonText: "Enable Monitoring",
      color: "purple"
    }
  };

  const prompt = prompts[type] || prompts.feature;
  const Icon = prompt.icon;

  const colorClasses = {
    orange: "border-orange-500/30 bg-orange-500/10",
    blue: "border-blue-500/30 bg-blue-500/10",
    purple: "border-purple-500/30 bg-purple-500/10"
  };

  const iconColors = {
    orange: "text-orange-400",
    blue: "text-blue-400", 
    purple: "text-purple-400"
  };

  const buttonColors = {
    orange: "bg-orange-600 hover:bg-orange-700",
    blue: "bg-blue-600 hover:bg-blue-700",
    purple: "bg-purple-600 hover:bg-purple-700"
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-6"
    >
      <Card className={`${colorClasses[prompt.color]} border backdrop-blur-sm`}>
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-full bg-gray-800/50 flex items-center justify-center`}>
              <Icon className={`w-6 h-6 ${iconColors[prompt.color]}`} />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-1">{prompt.title}</h3>
              <p className="text-gray-300 text-sm">{prompt.message}</p>
            </div>
            <Button
              onClick={onUpgrade}
              className={`${buttonColors[prompt.color]} text-white font-medium px-6 py-2 rounded-lg`}
            >
              <Crown className="w-4 h-4 mr-2" />
              {prompt.buttonText}
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}