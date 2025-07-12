
import React, { useState, useEffect } from "react";
import { PrivacyAgreement, UserPrivacyProfile, User } from "@/api/entities";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Shield, 
  AlertTriangle, 
  TrendingUp, 
  FileText, 
  Users, 
  Clock,
  ChevronRight,
  Activity,
  Target,
  Zap
} from "lucide-react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { createPageUrl } from "@/utils";

import StatsCard from "../components/dashboard/StatsCard";
import RecentAnalyses from "../components/dashboard/RecentAnalyses";
import RiskTrends from "../components/dashboard/RiskTrends";
import PrivacyInsights from "../components/dashboard/PrivacyInsights";
import { subscriptionManager } from "@/api/functions";
import UsageTracker from "../components/subscription/UsageTracker";
import SubscriptionModal from "../components/subscription/SubscriptionModal";

export default function Dashboard() {
  const [agreements, setAgreements] = useState([]);
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  useEffect(() => {
    loadDashboardData();
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      const { data } = await subscriptionManager({ action: 'get_subscription' });
      setSubscriptionData(data);
    } catch (error) {
      console.error('Error loading subscription:', error);
    }
  };

  const loadDashboardData = async () => {
    try {
      const [agreementsData, profileData, userData] = await Promise.all([
        PrivacyAgreement.filter({ created_by: (await User.me()).email }, '-created_date', 50),
        UserPrivacyProfile.filter({ created_by: (await User.me()).email }, '-created_date', 1),
        User.me()
      ]);

      setAgreements(agreementsData);
      setProfile(profileData[0] || null);
      setUser(userData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getOverallRiskScore = () => {
    if (agreements.length === 0) return 0;
    const total = agreements.reduce((sum, agreement) => sum + (agreement.risk_score || 0), 0);
    return Math.round(total / agreements.length);
  };

  const getHighRiskAgreements = () => {
    return agreements.filter(agreement => (agreement.risk_score || 0) >= 70);
  };

  const getRecentAgreements = () => {
    return agreements.slice(0, 5);
  };

  const getRiskColor = (score) => {
    if (score >= 80) return 'text-red-500';
    if (score >= 60) return 'text-orange-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getRiskBadgeColor = (score) => {
    if (score >= 80) return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (score >= 60) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    if (score >= 40) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    return 'bg-green-500/20 text-green-400 border-green-500/30';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-2"
          >
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Privacy Command Center
            </h1>
            <p className="text-gray-400 text-lg md:text-xl max-w-3xl mx-auto">
              Your digital sovereignty dashboard. Monitor, analyze, and protect your privacy rights across all platforms.
            </p>
          </motion.div>
          
          <div className="flex justify-center gap-4">
            <Link to={createPageUrl("Analyzer")}>
              <Button className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg">
                <Zap className="w-5 h-5 mr-2" />
                Analyze New Agreement
              </Button>
            </Link>
            <Link to={createPageUrl("Profile")}>
              <Button variant="outline" className="border-gray-700 text-gray-300 hover:bg-gray-800 px-6 py-3 rounded-xl">
                <Target className="w-5 h-5 mr-2" />
                Configure Profile
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Agreements"
            value={agreements.length}
            icon={FileText}
            trend={`+${agreements.filter(a => {
              const weekAgo = new Date();
              weekAgo.setDate(weekAgo.getDate() - 7);
              return new Date(a.created_date) > weekAgo;
            }).length} this week`}
            color="blue"
          />
          <StatsCard
            title="Average Risk Score"
            value={getOverallRiskScore()}
            icon={Shield}
            trend="Based on your profile"
            color={getOverallRiskScore() >= 70 ? 'red' : getOverallRiskScore() >= 40 ? 'orange' : 'green'}
          />
          <StatsCard
            title="High Risk Alerts"
            value={getHighRiskAgreements().length}
            icon={AlertTriangle}
            trend="Require attention"
            color="red"
          />
          <StatsCard
            title="Privacy Score"
            value={profile?.privacy_tolerance === 'strict' ? 'Strict' : profile?.privacy_tolerance === 'moderate' ? 'Moderate' : 'Relaxed'}
            icon={Activity}
            trend="Your privacy stance"
            color="purple"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Recent Analyses */}
          <div className="lg:col-span-2 space-y-8">
            <RecentAnalyses 
              agreements={getRecentAgreements()} 
              loading={loading}
              getRiskColor={getRiskColor}
              getRiskBadgeColor={getRiskBadgeColor}
            />
            
            <RiskTrends agreements={agreements} loading={loading} />
          </div>

          {/* Right Column - Insights */}
          <div className="space-y-8">
            {/* Usage Tracker */}
            {subscriptionData && (
              <UsageTracker 
                subscription={subscriptionData.subscription}
                features={subscriptionData.features}
              />
            )}
            <PrivacyInsights 
              agreements={agreements} 
              profile={profile}
              loading={loading}
            />
            
            {/* Quick Actions */}
            <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-400" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link to={createPageUrl("Analyzer")}>
                  <Button variant="ghost" className="w-full justify-start text-gray-300 hover:bg-gray-800/50">
                    <FileText className="w-4 h-4 mr-2" />
                    Analyze New Agreement
                    <ChevronRight className="w-4 h-4 ml-auto" />
                  </Button>
                </Link>
                <Link to={createPageUrl("History")}>
                  <Button variant="ghost" className="w-full justify-start text-gray-300 hover:bg-gray-800/50">
                    <Clock className="w-4 h-4 mr-2" />
                    View Analysis History
                    <ChevronRight className="w-4 h-4 ml-auto" />
                  </Button>
                </Link>
                <Link to={createPageUrl("Insights")}>
                  <Button variant="ghost" className="w-full justify-start text-gray-300 hover:bg-gray-800/50">
                    <Users className="w-4 h-4 mr-2" />
                    Community Insights
                    <ChevronRight className="w-4 h-4 ml-auto" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
        {/* Subscription Modal */}
        <SubscriptionModal 
          open={showUpgradeModal}
          onClose={() => setShowUpgradeModal(false)}
        />
      </div>
    </div>
  );
}
