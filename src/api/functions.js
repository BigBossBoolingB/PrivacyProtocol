/**
 * Base44 API Functions
 * 
 * This module contains all business logic functions that interact with the Base44 API.
 * Each function is documented with JSDoc annotations for automatic documentation generation.
 */

import { base44 } from './apiClient';
import { apiRequest } from './apiClient';

/**
 * Monitor privacy policy changes over time
 * 
 * @param {Object} params - Monitoring parameters
 * @param {string} params.url - URL of the privacy policy to monitor
 * @param {string} params.company_name - Name of the company
 * @param {string} [params.frequency='weekly'] - Monitoring frequency ('daily', 'weekly', 'monthly')
 * @param {boolean} [params.notify_changes=true] - Whether to send notifications on changes
 * @returns {Promise<PolicyMonitorResult>} Monitoring setup result with tracking ID
 * 
 * @example
 * const result = await policyMonitor({
 *   url: 'https://example.com/privacy',
 *   company_name: 'Example Corp',
 *   frequency: 'weekly'
 * });
 */
export const policyMonitor = base44.functions.policyMonitor;
/**
 * Fetch community analytics and privacy benchmarking data
 * 
 * @param {Object} params - Community insights parameters
 * @param {string} [params.timeframe='30d'] - Time period for analytics ('7d', '30d', '90d', '1y')
 * @param {string} [params.industry] - Filter by specific industry
 * @param {string} [params.region] - Filter by geographic region
 * @param {boolean} [params.include_trends=true] - Include trending privacy risks
 * @returns {Promise<CommunityInsightsResult>} Aggregated community privacy statistics and trends
 * 
 * @example
 * const insights = await communityInsights({
 *   timeframe: '30d',
 *   industry: 'technology',
 *   include_trends: true
 * });
 */
export const communityInsights = base44.functions.communityInsights;
/**
 * Calculate privacy risk score for a given policy
 * 
 * @param {Object} params - Risk calculation parameters
 * @param {string} params.content - Privacy policy content text
 * @param {string} [params.url] - Optional URL of the policy
 * @param {string} params.company_name - Name of the company
 * @param {Object} [params.user_profile] - User privacy preferences for personalized scoring
 * @returns {Promise<RiskScoreResult>} Risk assessment with score, flagged clauses, and recommendations
 * 
 * @example
 * const riskResult = await riskScoreCalculator({
 *   content: policyText,
 *   company_name: 'Example Corp',
 *   user_profile: { privacy_tolerance: 'strict' }
 * });
 */
export const riskScoreCalculator = base44.functions.riskScoreCalculator;
/**
 * Manage user notifications and communication preferences
 * 
 * @param {Object} params - Notification management parameters
 * @param {string} params.action - Action to perform ('send', 'schedule', 'update_preferences', 'get_history')
 * @param {string} [params.type] - Notification type ('policy_change', 'risk_alert', 'subscription')
 * @param {Object} [params.content] - Notification content and metadata
 * @param {Object} [params.preferences] - User notification preferences
 * @returns {Promise<NotificationResult>} Notification status and delivery information
 * 
 * @example
 * // Update notification preferences
 * await notificationEngine({
 *   action: 'update_preferences',
 *   preferences: {
 *     policy_changes: true,
 *     risk_alerts: true,
 *     email_frequency: 'weekly'
 *   }
 * });
 */
export const notificationEngine = base44.functions.notificationEngine;
/**
 * Manage user subscription lifecycle and feature access
 * 
 * @param {Object} params - Subscription management parameters
 * @param {string} params.action - Action to perform ('create', 'update', 'cancel', 'check_limits')
 * @param {string} [params.plan_id] - Subscription plan ID for create/update actions
 * @param {Object} [params.payment_method] - Payment method details for billing
 * @returns {Promise<SubscriptionResult>} Subscription status and feature access information
 * 
 * @example
 * // Check current subscription limits
 * const limits = await subscriptionManager({
 *   action: 'check_limits'
 * });
 * 
 * // Upgrade to premium plan
 * const upgrade = await subscriptionManager({
 *   action: 'update',
 *   plan_id: 'premium_monthly'
 * });
 */
export const subscriptionManager = base44.functions.subscriptionManager;
/**
 * Handle PayPal payment processing for subscriptions
 * 
 * @param {Object} params - PayPal payment parameters
 * @param {string} params.action - Payment action ('create_order', 'capture_payment', 'cancel_subscription')
 * @param {string} [params.plan_id] - Subscription plan ID
 * @param {number} [params.amount] - Payment amount for one-time payments
 * @param {string} [params.currency='USD'] - Payment currency
 * @param {Object} [params.metadata] - Additional payment metadata
 * @returns {Promise<PayPalResult>} Payment processing result with transaction details
 * 
 * @example
 * // Create PayPal subscription order
 * const order = await paypalManager({
 *   action: 'create_order',
 *   plan_id: 'premium_monthly',
 *   currency: 'USD'
 * });
 */
export const paypalManager = base44.functions.paypalManager;

