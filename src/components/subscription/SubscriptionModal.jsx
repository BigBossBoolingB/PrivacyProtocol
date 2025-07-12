
import React, { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label"; // Added import for Label
import { 
  Crown, 
  Check, 
  X, 
  Zap, 
  Shield, 
  TrendingUp, 
  Users,
  FileText,
  Bell,
  Loader2
} from "lucide-react";
import { motion } from "framer-motion";
import { subscriptionManager } from "@/api/functions";

export default function SubscriptionModal({ open, onClose }) {
  const [subscription, setSubscription] = useState(null);
  const [features, setFeatures] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('stripe'); // New state for payment method

  useEffect(() => {
    if (open) {
      loadSubscriptionData();
    }
  }, [open]);

  const loadSubscriptionData = async () => {
    try {
      const { data } = await subscriptionManager({ action: 'get_subscription' });
      setSubscription(data.subscription);
      setFeatures(data.features);
      setPricing(data.pricing);
    } catch (error) {
      console.error('Error loading subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (provider = 'stripe') => {
    setUpgrading(true);
    try {
      let response;
      
      if (provider === 'paypal') {
        response = await subscriptionManager({ action: 'create_paypal_checkout_session' });
        if (response.data.success && response.data.approval_url) {
          // Redirect to PayPal for approval
          window.location.href = response.data.approval_url;
          return;
        }
      } else { // Default to stripe
        response = await subscriptionManager({ action: 'create_checkout_session' });
        if (response.data.success) {
          // In real implementation, redirect to Stripe checkout
          await loadSubscriptionData(); // Refresh subscription data
        }
      }
    } catch (error) {
      console.error('Error upgrading:', error);
    } finally {
      setUpgrading(false);
    }
  };

  const isPremium = subscription?.plan_type === 'premium' && subscription?.status === 'active';
  const isTrialActive = subscription?.status === 'trial' && 
                       new Date() <= new Date(subscription?.trial_end);

  const premiumFeatures = [
    { name: 'Unlimited privacy analyses', icon: FileText, premium: true },
    { name: 'Real-time policy monitoring', icon: Bell, premium: true },
    { name: 'Advanced AI insights', icon: Zap, premium: true },
    { name: 'Community intelligence', icon: Users, premium: true },
    { name: 'Export reports (PDF/CSV)', icon: FileText, premium: true },
    { name: 'Custom privacy profiles', icon: Shield, premium: true },
    { name: 'Priority support', icon: Crown, premium: true },
    { name: 'Basic risk analysis', icon: TrendingUp, premium: false },
    { name: 'Clause identification', icon: Shield, premium: false }
  ];

  if (loading) {
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl bg-gray-900 border-gray-800 text-white">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl bg-gray-900 border-gray-800 text-white">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-center">
            {isPremium ? 'Premium Subscription' : 'Upgrade to Premium'}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Current Status */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold">Current Plan</h3>
                    <Badge className={isPremium ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-500/20 text-gray-400'}>
                      {isPremium ? 'Premium' : isTrialActive ? 'Trial' : 'Free'}
                    </Badge>
                  </div>
                  <p className="text-gray-400">
                    {isPremium 
                      ? `Active until ${new Date(subscription.current_period_end).toLocaleDateString()}`
                      : isTrialActive 
                        ? `Trial ends ${new Date(subscription.trial_end).toLocaleDateString()}`
                        : 'Limited access to features'
                    }
                  </p>
                </div>
                {isPremium && (
                  <Crown className="w-8 h-8 text-yellow-400" />
                )}
              </div>

              {/* Usage Stats */}
              {features && (
                <div className="mt-4 p-4 bg-gray-900/50 rounded-lg">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Monthly Analyses</span>
                    <span className="text-white">
                      {subscription.monthly_analyses_used || 0}
                      {features.unlimited_analyses ? ' (Unlimited)' : ` / ${features.monthly_analyses_limit}`}
                    </span>
                  </div>
                  {!features.unlimited_analyses && (
                    <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ 
                          width: `${Math.min(100, ((subscription.monthly_analyses_used || 0) / features.monthly_analyses_limit) * 100)}%` 
                        }}
                      />
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pricing Plans */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Free Plan */}
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-center">
                  <div className="text-xl font-bold">Free</div>
                  <div className="text-3xl font-bold mt-2">$0<span className="text-sm text-gray-400">/month</span></div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-3">
                  {premiumFeatures.filter(f => !f.premium).map((feature, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <Check className="w-4 h-4 text-green-400" />
                      <span className="text-gray-300">{feature.name}</span>
                    </li>
                  ))}
                  <li className="flex items-center gap-3">
                    <X className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-500">2 analyses per month</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Premium Plan */}
            <Card className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/30 relative">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-1">
                  Most Popular
                </Badge>
              </div>
              <CardHeader>
                <CardTitle className="text-center">
                  <div className="text-xl font-bold">Premium</div>
                  <div className="text-3xl font-bold mt-2">
                    $1.99<span className="text-sm text-gray-400">/month</span>
                  </div>
                  <div className="text-sm text-gray-400 mt-1">Cancel anytime</div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-3">
                  {premiumFeatures.map((feature, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <Check className="w-4 h-4 text-green-400" />
                      <span className={feature.premium ? "text-white" : "text-gray-300"}>
                        {feature.name}
                      </span>
                      {feature.premium && (
                        <Crown className="w-4 h-4 text-yellow-400" />
                      )}
                    </li>
                  ))}
                </ul>

                {!isPremium && (
                  <div className="space-y-3">
                    {/* Payment Method Selection */}
                    <div className="space-y-2">
                      <Label className="text-sm text-gray-400">Choose Payment Method:</Label>
                      <div className="grid grid-cols-2 gap-2">
                        <Button
                          variant={paymentMethod === 'stripe' ? 'default' : 'outline'}
                          onClick={() => setPaymentMethod('stripe')}
                          className="h-12 flex items-center justify-center gap-2"
                          disabled={upgrading}
                        >
                          {/* Stripe icon */}
                          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 2.227 0 4.515.858 6.09 1.631l.89-5.494C18.252.975 15.697 0 12.165 0 9.667 0 7.589.654 6.104 1.872 4.56 3.147 3.757 4.992 3.757 7.218c0 4.039 2.467 5.76 6.476 7.219 2.585.92 3.445 1.574 3.445 2.583 0 .98-.84 1.545-2.354 1.545-1.875 0-4.965-.921-6.99-2.109l-.9 5.555C5.175 22.99 8.385 24 11.714 24c2.641 0 4.843-.624 6.328-1.813 1.664-1.305 2.525-3.236 2.525-5.732 0-4.128-2.524-5.851-6.591-7.305z"/>
                          </svg>
                          Credit Card
                        </Button>
                        <Button
                          variant={paymentMethod === 'paypal' ? 'default' : 'outline'}
                          onClick={() => setPaymentMethod('paypal')}
                          className="h-12 flex items-center justify-center gap-2"
                          disabled={upgrading}
                        >
                          {/* PayPal icon */}
                          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797h-2.19c-.524 0-.968.382-1.05.9l-1.12 7.106zm14.146-14.42a3.35 3.35 0 0 0-.607-.541c-.013.028-.026.056-.054.115a6.997 6.997 0 0 1-5.78 5.506l-.827.051-.81 5.130c-.049.314.195.572.514.572H15.4c.456 0 .84-.334.915-.788l.394-2.497h.782c3.747 0 6.549-1.524 7.389-5.93.394-2.068.156-3.79-.658-5.118z"/>
                          </svg>
                          PayPal
                        </Button>
                      </div>
                    </div>

                    <Button
                      onClick={() => handleUpgrade(paymentMethod)}
                      disabled={upgrading}
                      className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium py-3 rounded-xl mt-6"
                    >
                      {upgrading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Crown className="w-4 h-4 mr-2" />
                          Upgrade with {paymentMethod === 'paypal' ? 'PayPal' : 'Credit Card'}
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Feature Comparison */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-center">Why Upgrade to Premium?</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center"
                >
                  <div className="w-12 h-12 mx-auto mb-4 bg-blue-500/20 rounded-full flex items-center justify-center">
                    <Zap className="w-6 h-6 text-blue-400" />
                  </div>
                  <h4 className="font-semibold mb-2">Unlimited Analysis</h4>
                  <p className="text-sm text-gray-400">
                    Analyze as many privacy policies as you need without monthly limits
                  </p>
                </motion.div>

                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="text-center"
                >
                  <div className="w-12 h-12 mx-auto mb-4 bg-purple-500/20 rounded-full flex items-center justify-center">
                    <Bell className="w-6 h-6 text-purple-400" />
                  </div>
                  <h4 className="font-semibold mb-2">Real-time Monitoring</h4>
                  <p className="text-sm text-gray-400">
                    Get instant alerts when privacy policies change or new risks emerge
                  </p>
                </motion.div>

                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="text-center"
                >
                  <div className="w-12 h-12 mx-auto mb-4 bg-green-500/20 rounded-full flex items-center justify-center">
                    <Users className="w-6 h-6 text-green-400" />
                  </div>
                  <h4 className="font-semibold mb-2">Community Insights</h4>
                  <p className="text-sm text-gray-400">
                    Access collective intelligence and trending privacy risks
                  </p>
                </motion.div>
              </div>
            </CardContent>
          </Card>

          {/* Money Back Guarantee */}
          <div className="text-center text-sm text-gray-400">
            <Shield className="w-4 h-4 inline mr-2" />
            30-day money-back guarantee • Secure payments • Cancel anytime
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
