import React, { useEffect } from 'react';
import { 
  PrivacyInsights, 
  RiskTrends, 
  StatsCard, 
  RecentAnalyses 
} from '@/components/dashboard';
import { useApiQuery } from '@/hooks';
import { communityInsights } from '@/api/functions';

function DashboardExample() {
  const { data: userProfile } = useApiQuery('userProfile');
  const { data: recentAnalyses } = useApiQuery('recentAnalyses');
  const { data: insights, refetch: refreshInsights } = useApiQuery(
    'communityInsights',
    () => communityInsights({
      timeframe: '30d',
      include_trends: true
    })
  );

  useEffect(() => {
    const interval = setInterval(refreshInsights, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [refreshInsights]);

  const stats = [
    {
      title: 'Total Analyses',
      value: recentAnalyses?.length || 0,
      change: 12,
      trend: 'up',
      description: 'Privacy policies analyzed this month'
    },
    {
      title: 'Average Risk Score',
      value: recentAnalyses?.reduce((acc, a) => acc + a.risk_score, 0) / (recentAnalyses?.length || 1) || 0,
      change: -5,
      trend: 'down',
      description: 'Lower is better'
    },
    {
      title: 'High Risk Alerts',
      value: recentAnalyses?.filter(a => a.risk_score > 75).length || 0,
      change: -2,
      trend: 'down',
      description: 'Policies requiring attention'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">Privacy Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {stats.map((stat, index) => (
          <StatsCard
            key={index}
            title={stat.title}
            value={stat.value}
            change={stat.change}
            trend={stat.trend}
            description={stat.description}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <PrivacyInsights
            userProfile={userProfile}
            recentAnalyses={recentAnalyses}
          />
          
          <RiskTrends
            data={recentAnalyses}
            timeRange="30d"
            showComparison={true}
          />
        </div>

        <div>
          <RecentAnalyses
            analyses={recentAnalyses}
            limit={5}
            onViewDetails={(id) => console.log('View details:', id)}
            onReanalyze={(id) => console.log('Reanalyze:', id)}
          />
        </div>
      </div>
    </div>
  );
}

export default DashboardExample;
