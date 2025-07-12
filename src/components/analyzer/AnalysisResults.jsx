
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  ExternalLink, 
  RefreshCw,
  Target,
  Eye,
  Users,
  DatabaseZap,
  BookUser,
  Share2,
  Timer,
  Info,
  X
} from "lucide-react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { createPageUrl } from "@/utils";

const DataPoint = ({ icon: Icon, label, value, colorClass }) => (
  <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
    <Icon className={`w-5 h-5 ${colorClass}`} />
    <div>
      <div className="text-sm text-gray-400">{label}</div>
      <div className="text-white font-medium">{value}</div>
    </div>
  </div>
);

const RightsChecklistItem = ({ label, granted }) => (
  <div className="flex items-center gap-2">
    {granted ? (
      <CheckCircle className="w-4 h-4 text-green-400" />
    ) : (
      <X className="w-4 h-4 text-red-400" />
    )}
    <span className={`text-sm ${granted ? 'text-gray-300' : 'text-gray-500'}`}>{label}</span>
  </div>
);

export default function AnalysisResults({ agreement, onNewAnalysis }) {
  const getRiskColor = (score) => {
    if (score >= 80) return 'text-red-400';
    if (score >= 60) return 'text-orange-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getRiskLabel = (score) => {
    if (score >= 80) return 'Critical Risk';
    if (score >= 60) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  const getRiskBadgeColor = (score) => {
    if (score >= 80) return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (score >= 60) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    if (score >= 40) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    return 'bg-green-500/20 text-green-400 border-green-500/30';
  };

  const getClauseRiskColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const dataCollectionItems = [
    { key: 'contact_info', label: 'Contact Info' },
    { key: 'financial_info', label: 'Financial Info' },
    { key: 'health_info', label: 'Health Info' },
    { key: 'location_info', label: 'Location Info' },
    { key: 'biometric_info', label: 'Biometric Info' },
    { key: 'usage_data', label: 'Usage Data' },
    { key: 'device_info', label: 'Device Info' },
    { key: 'user_content', label: 'User Content' }
  ];

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="bg-gradient-to-r from-gray-900 to-gray-800 border-gray-700/50 backdrop-blur-sm">
          <CardContent className="p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">{agreement.title}</h2>
                <p className="text-gray-400">{agreement.company}</p>
              </div>
              <div className="text-right">
                <div className={`text-4xl font-bold ${getRiskColor(agreement.risk_score)}`}>
                  {agreement.risk_score}/100
                </div>
                <Badge className={`${getRiskBadgeColor(agreement.risk_score)} border`}>
                  {getRiskLabel(agreement.risk_score)}
                </Badge>
              </div>
            </div>
            
            <div className="mb-6">
              <div className="text-sm text-gray-400 mb-2">Risk Score</div>
              <Progress value={agreement.risk_score} className="h-3" />
            </div>
            
            <p className="text-gray-300 mb-6">{agreement.analysis_summary}</p>
            
            <div className="flex flex-wrap gap-3">
              <Button onClick={onNewAnalysis} variant="outline" className="border-gray-700 text-gray-300">
                <RefreshCw className="w-4 h-4 mr-2" />
                Analyze Another
              </Button>
              <Link to={createPageUrl("Dashboard")}>
                <Button variant="outline" className="border-gray-700 text-gray-300">
                  <Target className="w-4 h-4 mr-2" />
                  View Dashboard
                </Button>
              </Link>
              {agreement.url && (
                <a
                  href={agreement.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  <ExternalLink className="w-4 h-4" />
                  View Original
                </a>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Data Collection Breakdown */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <DatabaseZap className="w-5 h-5 text-blue-400" />
                  Data Collection Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {dataCollectionItems.map(item => (
                    <RightsChecklistItem
                      key={item.key}
                      label={item.label}
                      granted={agreement.data_collection_breakdown?.[item.key]}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* User Rights Summary */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <BookUser className="w-5 h-5 text-green-400" />
                  Your Rights
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-2">
                <RightsChecklistItem label="Data Access" granted={agreement.user_rights_summary?.data_access} />
                <RightsChecklistItem label="Data Deletion" granted={agreement.user_rights_summary?.data_deletion} />
                <RightsChecklistItem label="Data Portability" granted={agreement.user_rights_summary?.data_portability} />
                <RightsChecklistItem label="Opt-out of Sale" granted={agreement.user_rights_summary?.opt_out_of_sale} />
              </CardContent>
            </Card>
          </motion.div>
          
          {/* Third-Party Sharing */}
          {agreement.third_party_trackers && agreement.third_party_trackers.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Share2 className="w-5 h-5 text-purple-400" />
                    Third-Party Sharing
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                  {agreement.third_party_trackers.map((tracker, index) => (
                    <Badge key={index} variant="outline" className="border-purple-500/50 text-purple-400">
                      {tracker}
                    </Badge>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Data Retention */}
          {agreement.data_retention_policy && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Timer className="w-5 h-5 text-yellow-400" />
                    Data Retention Policy
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-white font-medium">{agreement.data_retention_policy}</p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Flagged Clauses */}
          {agreement.flagged_clauses && agreement.flagged_clauses.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    Flagged Clauses ({agreement.flagged_clauses.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {agreement.flagged_clauses.map((clause, index) => (
                    <div key={index} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                      <div className="flex items-start justify-between mb-3">
                        <Badge className={`${getClauseRiskColor(clause.risk_level)} border`}>
                          {clause.risk_level} risk
                        </Badge>
                      </div>
                      <blockquote className="text-gray-300 border-l-4 border-gray-600 pl-4 mb-3 italic">
                        "{clause.clause_text}"
                      </blockquote>
                      <div className="space-y-3">
                        <div>
                          <span className="text-sm font-medium text-gray-400">Plain Language:</span>
                          <p className="text-white">{clause.plain_language}</p>
                        </div>
                        <div>
                          <span className="text-sm font-medium text-gray-400">Why this matters:</span>
                          <p className="text-gray-300">{clause.explanation}</p>
                        </div>
                        {clause.what_if_scenario && (
                           <div className="p-3 bg-red-900/30 rounded-lg border border-red-500/30">
                            <span className="text-sm font-medium text-red-400 flex items-center gap-2">
                              <Info className="w-4 h-4" />
                              What If Scenario:
                            </span>
                            <p className="text-gray-300 text-sm mt-1">{clause.what_if_scenario}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Recommendations */}
          {agreement.recommendations && agreement.recommendations.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {agreement.recommendations.map((rec, index) => (
                    <div key={index} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-white">{rec.action}</h4>
                        <Badge className={`${getPriorityColor(rec.priority)} border`}>
                          {rec.priority}
                        </Badge>
                      </div>
                      <p className="text-gray-300">{rec.description}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </div>

      {/* Opt-out Options and Data Usage Categories */}
      <div className="grid lg:grid-cols-2 gap-6">
        {agreement.opt_out_options && agreement.opt_out_options.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Shield className="w-5 h-5 text-green-400" />
                  Opt-out Options
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {agreement.opt_out_options.map((option, index) => (
                  <div key={index} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-white">{option.type}</h4>
                      {option.url && (
                        <a
                          href={option.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                    <p className="text-gray-300">{option.instructions}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}
        
        {agreement.data_usage_categories && agreement.data_usage_categories.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm h-full">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Eye className="w-5 h-5 text-blue-400" />
                  General Data Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {agreement.data_usage_categories.map((category, index) => (
                    <Badge key={index} variant="outline" className="border-blue-500/50 text-blue-400">
                      {category.replace(/_/g, ' ')}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
}
