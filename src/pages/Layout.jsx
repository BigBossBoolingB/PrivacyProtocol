
import React, { useState } from "react";
import { Link, useLocation, Outlet } from "react-router-dom";
import { 
  Shield, 
  BarChart3, 
  Search, 
  User, 
  History, 
  Users,
  Menu,
  Bell,
  Brain,
  Crown,
  LogOut,
  Sun,
  Moon
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { NAVIGATION_ITEMS, APP_META } from "@/lib/constants";
import { useAuth } from "@/contexts/AuthContext";
import { useSubscription } from "@/contexts/SubscriptionContext";
import { useTheme } from "@/contexts/ThemeContext";

/**
 * Main Layout component
 * 
 * @returns {JSX.Element} - Rendered component
 */
export default function Layout() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, signOut } = useAuth();
  const { subscription, features, isPremium, usagePercentage, upgradeToPremium, downgradeToFree } = useSubscription();
  const { theme, toggleTheme } = useTheme();

  /**
   * Get user initials for avatar fallback
   * 
   * @returns {string} - User initials
   */
  const getUserInitials = () => {
    if (!user?.name) return "U";
    
    const nameParts = user.name.split(" ");
    if (nameParts.length === 1) return nameParts[0].charAt(0).toUpperCase();
    
    return (nameParts[0].charAt(0) + nameParts[nameParts.length - 1].charAt(0)).toUpperCase();
  };

  /**
   * Navigation content component
   * 
   * @returns {JSX.Element} - Rendered component
   */
  const NavContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo and App Name */}
      <div className="p-6 border-b border-gray-800/50">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">{APP_META.NAME}</h1>
            <p className="text-xs text-gray-400">{APP_META.TAGLINE}</p>
          </div>
        </div>
      </div>
      
      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {NAVIGATION_ITEMS.map((item) => {
          const IconComponent = {
            BarChart3,
            Search,
            User,
            History,
            Users,
            Bell,
            Brain
          }[item.icon];

          return (
            <Link
              key={item.title}
              to={`/${item.path}`}
              onClick={() => setMobileMenuOpen(false)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                location.pathname === `/${item.path}`
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'text-gray-300 hover:bg-gray-800/50 hover:text-white'
              }`}
            >
              {IconComponent && <IconComponent className="w-5 h-5" />}
              <div className="flex-1 min-w-0">
                <div className="font-medium">{item.title}</div>
                <div className="text-xs text-gray-500 group-hover:text-gray-400 transition-colors">
                  {item.description}
                </div>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer Section */}
      <div className="p-4 border-t border-gray-800/50">
        {/* Subscription Status */}
        {subscription && (
          <div className="mb-4 p-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-blue-500/20">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-white">
                {isPremium ? 'Premium Plan' : 'Free Plan'}
              </span>
              {isPremium && (
                <Crown className="w-4 h-4 text-yellow-400" />
              )}
            </div>
            
            {!isPremium ? (
              <>
                <div className="text-xs text-gray-400 mb-1">
                  {subscription.monthly_analyses_used || 0} / {features.monthly_analyses_limit} analyses used
                </div>
                <Progress value={usagePercentage} className="h-1.5 mb-2" />
              </>
            ) : (
              <div className="text-xs text-gray-400 mb-2">
                Unlimited analyses
              </div>
            )}
            
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-1 w-full text-xs bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border-blue-500/50"
              onClick={isPremium ? downgradeToFree : upgradeToPremium}
            >
              {isPremium ? 'Downgrade to Free' : 'Upgrade to Premium ($1.99/month)'}
            </Button>
          </div>
        )}

        {/* User Profile */}
        <div className="bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-xl p-4 border border-blue-500/20">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <Avatar>
                <AvatarImage src={user?.avatar} alt={user?.name || "User"} />
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-indigo-600">
                  {getUserInitials()}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="text-white font-medium text-sm">{user?.name || "Anonymous User"}</p>
                <p className="text-gray-400 text-xs">{user?.role || "User"}</p>
              </div>
            </div>
            
            <div className="flex gap-1">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-8 w-8 text-gray-400 hover:text-white"
                      onClick={toggleTheme}
                    >
                      {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Toggle theme</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-8 w-8 text-gray-400 hover:text-red-400"
                      onClick={signOut}
                    >
                      <LogOut className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Sign out</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
          
          <p className="text-gray-400 text-xs leading-relaxed">
            {APP_META.DESCRIPTION}
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="flex min-h-screen">
        {/* Desktop Sidebar */}
        <div className="hidden lg:flex lg:w-80 lg:flex-col bg-slate-900/95 backdrop-blur-sm border-r border-gray-800/50">
          <NavContent />
        </div>

        {/* Mobile Header */}
        <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-sm border-b border-gray-800/50">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">{APP_META.NAME}</h1>
              </div>
            </div>
            <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="text-gray-300 hover:text-white">
                  <Menu className="w-6 h-6" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-80 bg-slate-900 border-gray-800/50 p-0">
                <NavContent />
              </SheetContent>
            </Sheet>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col lg:ml-0 pt-16 lg:pt-0">
          <main className="flex-1 overflow-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}

