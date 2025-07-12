import React, { useState } from 'react';
import { useApiQuery, useApiMutation } from '@/hooks';
import { subscriptionManager, paypalManager } from '@/api/functions';
import { SubscriptionModal, UsageTracker } from '@/components/subscription';

function SubscriptionManagement() {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  
  const { data: subscription, refetch: refreshSubscription } = useApiQuery(
    'subscription',
    () => subscriptionManager({ action: 'check_limits' })
  );

  const { mutate: upgradeSubscription, loading: upgrading } = useApiMutation(
    async (planId) => {
      const paypalOrder = await paypalManager({
        action: 'create_order',
        plan_id: planId,
        currency: 'USD'
      });

      return subscriptionManager({
        action: 'update',
        plan_id: planId,
        payment_method: {
          type: 'paypal',
          token: paypalOrder.order_id
        }
      });
    },
    {
      onSuccess: () => {
        refreshSubscription();
        setShowUpgradeModal(false);
        alert('Subscription upgraded successfully!');
      },
      onError: (error) => {
        alert(`Upgrade failed: ${error.message}`);
      }
    }
  );

  const handleUpgrade = (planId) => {
    upgradeSubscription(planId);
  };

  if (!subscription) {
    return <div>Loading subscription details...</div>;
  }

  const isNearLimit = (used, limit) => used / limit > 0.8;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Subscription Management</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Current Plan</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Plan</p>
            <p className="font-medium">{subscription.subscription.plan_id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Status</p>
            <p className="font-medium capitalize">{subscription.subscription.status}</p>
          </div>
        </div>
      </div>

      <UsageTracker
        usage={subscription.current_usage}
        limits={subscription.usage_limits}
        onUpgrade={() => setShowUpgradeModal(true)}
        showDetails={true}
      />

      {isNearLimit(subscription.current_usage.analyses_used, subscription.usage_limits.analyses_per_month) && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
          <p className="text-yellow-800">
            ⚠️ You're approaching your monthly analysis limit. Consider upgrading to continue analyzing policies.
          </p>
        </div>
      )}

      <button
        onClick={() => setShowUpgradeModal(true)}
        className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Upgrade Plan
      </button>

      <SubscriptionModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        currentPlan={subscription.subscription}
        onUpgrade={handleUpgrade}
      />
    </div>
  );
}

export default SubscriptionManagement;
