
import React, { useState, useEffect } from "react";
import { PolicyChange, PrivacyAgreement, User } from "@/api/entities";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Bell, 
  TrendingUp, 
  AlertTriangle, 
  Clock, 
  Eye,
  ArrowRight,
  Calendar,
  Zap,
  Shield,
  Loader2 // Added for loading state in button
} from "lucide-react";
import { motion } from "framer-motion";
import { format } from "date-fns";
import { policyMonitor } from "@/api/functions";
import { notificationEngine } from "@/api/functions"; // New import
import { useToast } from "@/components/ui/use-toast"; // New import

export default function PolicyTracker() {
  const [policyChanges, setPolicyChanges] = useState([]);
  const [agreements, setAgreements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [monitoring, setMonitoring] = useState(false);
  const [notifying, setNotifying] = useState(null); // Track which change is being notified
  const { toast } = useToast(); // Initialize useToast

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const user = await User.me();
      const [changesData, agreementsData] = await Promise.all([
        PolicyChange.filter({ created_by: user.email }, '-detected_date', 50),
        PrivacyAgreement.filter({ created_by: user.email }, '-created_date', 100)
      ]);

      setPolicyChanges(changesData);
      setAgreements(agreementsData);
    } catch (error) {
      console.error('Error loading policy tracker data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startMonitoring = async (agreementId) => {
    setMonitoring(true);
    try {
      const { data } = await policyMonitor({ agreementId });
      if (data.has_changed) {
        loadData(); // Refresh data to show new changes
        toast({ title: "Policy Scan Complete", description: "New changes have been detected and logged." });
      } else {
        toast({ title: "Policy Scan Complete", description: "No significant changes found." });
      }
    } catch (error) {
      console.error('Error monitoring policy:', error);
      toast({ title: "Error", description: "Failed to monitor policy.", variant: "destructive" });
    } finally {
      setMonitoring(false);
    }
  };

  const handleNotify = async (change) => {
    setNotifying(change.id);
    try {
      const agreement = agreements.find(a => a.id === change.agreement_id);
      await notificationEngine({
        notificationType: 'policy_change',
        data: {
          companyName: agreement?.title || 'a service',
          changes: [change.change_summary],
          riskImpact: change.risk_impact,
          analysisUrl: '#' // Placeholder URL
        }
      });
      toast({ title: "Notification Sent", description: "User has been notified about this policy change." });
    } catch (error) {
      console.error('Error sending notification:', error);
      toast({ title: "Error", description: "Failed to send notification.", variant: "destructive" });
    } finally {
      setNotifying(null);
    }
  }

  const getRiskColor = (impact) => {
    if (impact >= 70) return 'text-red-400 bg-red-500/20 border-red-500/30';
    if (impact >= 40) return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
    return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'data_collection': return <Eye className="w-4 h-4" />;
      case 'sharing': return <ArrowRight className="w-4 h-4" />;
      case 'user_rights': return <Shield className="w-4 h-4" />;
      case 'tracking': return <TrendingUp className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-2"
          >
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Policy Change Tracker
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Monitor your privacy agreements for changes and stay informed about policy updates
            </p>
          </motion.div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
            <CardContent className="p-6 text-center">
              <Bell className="w-8 h-8 mx-auto mb-2 text-blue-400" />
              <div className="text-2xl font-bold text-white">{policyChanges.length}</div>
              <div className="text-sm text-gray-400">Total Changes Detected</div>
            </CardContent>
          </Card>
          <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
            <CardContent className="p-6 text-center">
              <Eye className="w-8 h-8 mx-auto mb-2 text-green-400" />
              <div className="text-2xl font-bold text-white">{agreements.length}</div>
              <div className="text-sm text-gray-400">Agreements Monitored</div>
            </CardContent>
          </Card>
          <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
            <CardContent className="p-6 text-center">
              <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-red-400" />
              <div className="text-2xl font-bold text-white">
                {policyChanges.filter(c => c.risk_impact >= 70).length}
              </div>
              <div className="text-sm text-gray-400">High-Risk Changes</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Recent Changes */}
          <div className="lg:col-span-2">
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-400" />
                  Recent Policy Changes
                </CardTitle>
              </CardHeader>
              <CardContent>
                {policyChanges.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <Bell className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                    <p>No policy changes detected yet.</p>
                    <p className="text-sm mt-2">We'll monitor your agreements and notify you of any changes.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {policyChanges.map((change, index) => (
                      <motion.div
                        key={change.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h4 className="font-medium text-white">
                              {agreements.find(a => a.id === change.agreement_id)?.title || 'Unknown Agreement'}
                            </h4>
                            <p className="text-sm text-gray-400">
                              {format(new Date(change.detected_date), 'MMM d, yyyy')}
                            </p>
                          </div>
                          <Badge className={`${getRiskColor(change.risk_impact)} border`}>
                            Risk: {change.risk_impact}/100
                          </Badge>
                        </div>
                        
                        <p className="text-gray-300 mb-3">{change.change_summary}</p>
                        
                        <div className="flex items-center justify-between mt-4">
                          <div className="flex flex-wrap gap-2">
                            {change.change_categories?.map((category, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs border-gray-600 text-gray-400">
                                {getCategoryIcon(category)}
                                <span className="ml-1">{category.replace(/_/g, ' ')}</span>
                              </Badge>
                            ))}
                          </div>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleNotify(change)}
                            disabled={notifying === change.id}
                            className="text-blue-400 hover:bg-blue-900/50"
                          >
                            {notifying === change.id ? (
                               <Loader2 className="w-4 h-4 animate-spin"/>
                            ) : (
                               <Bell className="w-4 h-4 mr-2" />
                            )}
                            Notify
                          </Button>
                        </div>
                        
                        {change.new_clauses?.length > 0 && (
                          <div className="mt-3 p-3 bg-red-900/20 rounded-lg border border-red-500/30">
                            <h5 className="text-sm font-medium text-red-400 mb-1">New Concerning Clauses:</h5>
                            <ul className="text-sm text-gray-300 space-y-1">
                              {change.new_clauses.slice(0, 2).map((clause, idx) => (
                                <li key={idx}>• {clause}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Monitoring Controls */}
          <div className="space-y-6">
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-400" />
                  Active Monitoring
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                    <Shield className="w-8 h-8 text-white" />
                  </div>
                  <p className="text-white font-medium mb-2">24/7 Policy Monitoring</p>
                  <p className="text-sm text-gray-400 mb-4">
                    We continuously monitor your agreements for changes and alert you to important updates.
                  </p>
                  <Button
                    onClick={() => startMonitoring()}
                    disabled={monitoring}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {monitoring ? 'Checking...' : 'Check All Policies Now'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-green-400" />
                  Monitoring Schedule
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Daily Checks</span>
                    <Badge variant="outline" className="border-green-500/50 text-green-400">Active</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Weekly Deep Scan</span>
                    <Badge variant="outline" className="border-green-500/50 text-green-400">Active</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Instant Alerts</span>
                    <Badge variant="outline" className="border-green-500/50 text-green-400">Active</Badge>
                  </div>
                </div>
                
                <Alert className="border-blue-500/50 bg-blue-500/10">
                  <AlertTriangle className="h-4 w-4 text-blue-400" />
                  <AlertDescription className="text-blue-400 text-sm">
                    Next scheduled scan: Today at 6:00 PM
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
