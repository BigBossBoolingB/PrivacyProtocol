import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { BarChart3, Crown, TrendingUp } from "lucide-react";

export default function UsageTracker({ subscription, features }) {
  if (!subscription || !features) return null;

  const isPremium = features.unlimited_analyses;
  const currentUsage = subscription.monthly_analyses_used || 0;
  const limit = features.monthly_analyses_limit;
  const usagePercentage = isPremium ? 0 : Math.min(100, (currentUsage / limit) * 100);

  const getUsageColor = () => {
    if (isPremium) return 'text-green-400';
    if (usagePercentage >= 90) return 'text-red-400';
    if (usagePercentage >= 70) return 'text-orange-400';
    return 'text-blue-400';
  };

  const getProgressColor = () => {
    if (isPremium) return 'bg-green-500';
    if (usagePercentage >= 90) return 'bg-red-500';
    if (usagePercentage >= 70) return 'bg-orange-500';
    return 'bg-blue-500';
  };

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-white flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          Usage This Month
          {isPremium && (
            <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
              <Crown className="w-3 h-3 mr-1" />
              Premium
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Privacy Analyses</span>
          <span className={`font-bold ${getUsageColor()}`}>
            {currentUsage}{isPremium ? '' : ` / ${limit}`}
            {isPremium && <span className="text-gray-400 ml-1">(Unlimited)</span>}
          </span>
        </div>

        {!isPremium && (
          <div className="space-y-2">
            <Progress value={usagePercentage} className="h-2" />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0</span>
              <span>{limit}</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-gray-800">
          <div className="text-center">
            <div className="text-lg font-bold text-white">{subscription.total_analyses || 0}</div>
            <div className="text-xs text-gray-400">Total Analyses</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-blue-400">
              {isPremium ? '∞' : Math.max(0, limit - currentUsage)}
            </div>
            <div className="text-xs text-gray-400">Remaining</div>
          </div>
        </div>

        {!isPremium && usagePercentage >= 80 && (
          <div className="p-3 bg-orange-900/30 rounded-lg border border-orange-500/30">
            <div className="flex items-center gap-2 text-orange-400 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>Running low on analyses</span>
            </div>
            <p className="text-xs text-gray-300 mt-1">
              Upgrade to Premium for unlimited analyses at just $1.99/month
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}