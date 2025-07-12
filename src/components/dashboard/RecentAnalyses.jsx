import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, ExternalLink, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { format } from "date-fns";
import { Link } from "react-router-dom";
import { createPageUrl } from "@/utils";

export default function RecentAnalyses({ agreements, loading, getRiskColor, getRiskBadgeColor }) {
  if (loading) {
    return (
      <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Recent Analyses</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-700 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-400" />
          Recent Analyses
        </CardTitle>
        <Link to={createPageUrl("History")}>
          <Button variant="ghost" size="sm" className="text-blue-400 hover:text-blue-300">
            View All
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {agreements.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p>No privacy agreements analyzed yet.</p>
            <Link to={createPageUrl("Analyzer")}>
              <Button className="mt-4 bg-blue-600 hover:bg-blue-700">
                Analyze Your First Agreement
              </Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {agreements.map((agreement, index) => (
              <motion.div
                key={agreement.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50 hover:bg-gray-800/70 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h4 className="font-medium text-white">{agreement.title}</h4>
                    <p className="text-sm text-gray-400">
                      {format(new Date(agreement.created_date), 'MMM d, yyyy')}
                    </p>
                  </div>
                  <Badge className={`${getRiskBadgeColor(agreement.risk_score)} border`}>
                    {agreement.risk_score}/100
                  </Badge>
                </div>
                <p className="text-sm text-gray-300 mb-3">
                  {agreement.analysis_summary}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {agreement.flagged_clauses?.length > 0 && (
                      <Badge variant="outline" className="text-red-400 border-red-500/50">
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        {agreement.flagged_clauses.length} issues
                      </Badge>
                    )}
                  </div>
                  {agreement.url && (
                    <a
                      href={agreement.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}