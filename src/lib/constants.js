/**
 * Application-wide constants
 */

// Navigation items for the sidebar
export const NAVIGATION_ITEMS = [
  {
    title: "Dashboard",
    path: "dashboard",
    icon: "BarChart3",
    description: "Privacy overview & analytics"
  },
  {
    title: "Analyzer",
    path: "analyzer",
    icon: "Search",
    description: "Upload & analyze agreements"
  },
  {
    title: "Profile",
    path: "profile",
    icon: "User",
    description: "Privacy preferences"
  },
  {
    title: "History",
    path: "history",
    icon: "History",
    description: "Past analyses"
  },
  {
    title: "Insights",
    path: "insights",
    icon: "Users",
    description: "Community intelligence"
  },
  {
    title: "Policy Tracker",
    path: "policy-tracker",
    icon: "Bell",
    description: "Monitor policy changes"
  },
  {
    title: "Advanced Intel",
    path: "advanced-insights",
    icon: "Brain",
    description: "AI-powered insights"
  }
];

// Risk score thresholds
export const RISK_THRESHOLDS = {
  HIGH: 70,
  MEDIUM: 40,
  LOW: 0
};

// Subscription plans
export const SUBSCRIPTION_PLANS = {
  FREE: 'free',
  PREMIUM: 'premium'
};

// Feature limits
export const FEATURE_LIMITS = {
  FREE_MONTHLY_ANALYSES: 50
};

// App metadata
export const APP_META = {
  NAME: "PrivacyProtocol",
  TAGLINE: "AI-Powered Guardian",
  DESCRIPTION: "Empowering digital sovereignty through transparent privacy protocols"
};