
import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { format } from "date-fns";
import {
  X,
  ExternalLink,
  AlertTriangle,
  Shield,
  Eye,
  CheckCircle,
  Calendar,
  Building2,
  DatabaseZap,
  BookUser,
  Share2,
  Timer,
  Info
} from "lucide-react";


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

export default function AgreementModal({ agreement, onClose }) {
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

  const getClauseRiskColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] bg-gray-900 border-gray-800 text-white">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Building2 className="w-6 h-6 text-blue-400" />
              <div>
                <h2 className="text-xl font-bold">{agreement.title}</h2>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Calendar className="w-4 h-4" />
                  <span>{format(new Date(agreement.created_date), 'MMM d, yyyy')}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Badge className={`${getRiskBadgeColor(agreement.risk_score)} border text-lg px-3 py-1`}>
                {agreement.risk_score}/100
              </Badge>
              {agreement.url && (
                <a
                  href={agreement.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <ExternalLink className="w-5 h-5" />
                </a>
              )}
            </div>
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh]">
          <div className="space-y-6 pr-4">
            {/* Analysis Summary */}
            <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
              <h3 className="font-semibold text-white mb-2">Analysis Summary</h3>
              <p className="text-gray-300">{agreement.analysis_summary}</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
                {/* Data Collection Breakdown */}
                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                    <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                        <DatabaseZap className="w-4 h-4 text-blue-400" />
                        Data Collection
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                    {dataCollectionItems.map(item => (
                        <RightsChecklistItem
                        key={item.key}
                        label={item.label}
                        granted={agreement.data_collection_breakdown?.[item.key]}
                        />
                    ))}
                    </div>
                </div>

                {/* User Rights Summary */}
                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                    <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                        <BookUser className="w-4 h-4 text-green-400" />
                        Your Rights
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                        <RightsChecklistItem label="Data Access" granted={agreement.user_rights_summary?.data_access} />
                        <RightsChecklistItem label="Data Deletion" granted={agreement.user_rights_summary?.data_deletion} />
                        <RightsChecklistItem label="Data Portability" granted={agreement.user_rights_summary?.data_portability} />
                        <RightsChecklistItem label="Opt-out of Sale" granted={agreement.user_rights_summary?.opt_out_of_sale} />
                    </div>
                </div>
            </div>

            {/* Data Usage Categories */}
            {agreement.data_usage_categories && agreement.data_usage_categories.length > 0 && (
              <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <Eye className="w-4 h-4 text-blue-400" />
                  Data Usage Categories
                </h3>
                <div className="flex flex-wrap gap-2">
                  {agreement.data_usage_categories.map((category, index) => (
                    <Badge key={index} variant="outline" className="border-blue-500/50 text-blue-400">
                      {category.replace(/_/g, ' ')}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Flagged Clauses */}
            {agreement.flagged_clauses && agreement.flagged_clauses.length > 0 && (
              <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                  Flagged Clauses ({agreement.flagged_clauses.length})
                </h3>
                <div className="space-y-4">
                  {agreement.flagged_clauses.map((clause, index) => (
                    <div key={index} className="p-3 bg-gray-700/50 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <Badge className={`${getClauseRiskColor(clause.risk_level)} border text-xs`}>
                          {clause.risk_level} risk
                        </Badge>
                      </div>
                      <blockquote className="text-gray-300 border-l-4 border-gray-600 pl-3 mb-2 italic text-sm">
                        "{clause.clause_text}"
                      </blockquote>
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-400">Plain Language:</span>
                          <p className="text-white">{clause.plain_language}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-400">Explanation:</span>
                          <p className="text-gray-300">{clause.explanation}</p>
                        </div>
                         {clause.what_if_scenario && (
                           <div className="p-2 bg-red-900/30 rounded-lg border border-red-500/30 mt-2">
                            <span className="text-xs font-medium text-red-400 flex items-center gap-1">
                              <Info className="w-3 h-3" />
                              What If Scenario:
                            </span>
                            <p className="text-gray-300 text-xs mt-1">{clause.what_if_scenario}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {agreement.recommendations && agreement.recommendations.length > 0 && (
              <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  Recommendations
                </h3>
                <div className="space-y-3">
                  {agreement.recommendations.map((rec, index) => (
                    <div key={index} className="p-3 bg-gray-700/50 rounded-lg">
                      <h4 className="font-medium text-white text-sm">{rec.action}</h4>
                      <p className="text-gray-300 text-sm">{rec.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Third-Party & Retention */}
             <div className="grid lg:grid-cols-2 gap-6">
                {agreement.third_party_trackers && agreement.third_party_trackers.length > 0 && (
                    <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                        <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                        <Share2 className="w-4 h-4 text-purple-400" />
                        Third-Party Sharing
                        </h3>
                        <div className="flex flex-wrap gap-2">
                        {agreement.third_party_trackers.map((tracker, index) => (
                            <Badge key={index} variant="outline" className="border-purple-500/50 text-purple-400">
                            {tracker}
                            </Badge>
                        ))}
                        </div>
                    </div>
                )}
                 <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                    <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                        <Timer className="w-4 h-4 text-yellow-400" />
                        Data Retention
                    </h3>
                    <p className="text-white font-medium">{agreement.data_retention_policy}</p>
                 </div>
            </div>

            {/* Opt-out Options */}
            {agreement.opt_out_options && agreement.opt_out_options.length > 0 && (
              <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <Shield className="w-4 h-4 text-green-400" />
                  Opt-out Options
                </h3>
                <div className="space-y-3">
                  {agreement.opt_out_options.map((option, index) => (
                    <div key={index} className="p-3 bg-gray-700/50 rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-white text-sm">{option.type}</h4>
                          <p className="text-gray-300 text-sm">{option.instructions}</p>
                        </div>
                        {option.url && (
                          <a
                            href={option.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 transition-colors ml-2"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
