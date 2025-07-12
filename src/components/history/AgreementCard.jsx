
import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";
import { Building2, Calendar, Eye, ExternalLink, AlertTriangle, Share2 } from "lucide-react";
import { motion } from "framer-motion";

export default function AgreementCard({ agreement, onView }) {
  const getRiskColor = (score) => {
    if (score >= 80) return 'text-red-400';
    if (score >= 60) return 'text-orange-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getRiskBadgeColor = (score) => {
    if (score >= 80) return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (score >= 60) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    if (score >= 40) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    return 'bg-green-500/20 text-green-400 border-green-500/30';
  };

  const getRiskLabel = (score) => {
    if (score >= 80) return 'Critical';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    return 'Low';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm hover:bg-gray-900/70 transition-colors cursor-pointer">
        <CardContent className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <Building2 className="w-4 h-4 text-gray-400" />
                <h3 className="font-semibold text-white truncate">{agreement.title}</h3>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Calendar className="w-4 h-4" />
                <span>{format(new Date(agreement.created_date), 'MMM d, yyyy')}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={`${getRiskBadgeColor(agreement.risk_score)} border`}>
                {getRiskLabel(agreement.risk_score)} ({agreement.risk_score}/100)
              </Badge>
            </div>
          </div>

          <p className="text-gray-300 text-sm mb-4 line-clamp-2">
            {agreement.analysis_summary}
          </p>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {agreement.flagged_clauses?.length > 0 && (
                <Badge variant="outline" className="text-red-400 border-red-500/50 text-xs">
                  <AlertTriangle className="w-3 h-3 mr-1" />
                  {agreement.flagged_clauses.length} issues
                </Badge>
              )}
              {agreement.third_party_trackers?.length > 0 && (
                <Badge variant="outline" className="text-purple-400 border-purple-500/50 text-xs">
                  <Share2 className="w-3 h-3 mr-1" />
                  {agreement.third_party_trackers.length} trackers
                </Badge>
              )}
              {agreement.data_usage_categories?.length > 0 && (
                <Badge variant="outline" className="text-blue-400 border-blue-500/50 text-xs">
                  {agreement.data_usage_categories.length} data types
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              {agreement.url && (
                <a
                  href={agreement.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 transition-colors"
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
              <Button
                size="sm"
                variant="ghost"
                onClick={onView}
                className="text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
              >
                <Eye className="w-4 h-4 mr-2" />
                View Details
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
