import React, { useState, useEffect } from "react";
import { UserPrivacyProfile, User } from "@/api/entities";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import {
  Shield,
  User as UserIcon,
  Bell,
  BarChart3,
  ChevronRight,
  Save,
  Loader2,
  AlertCircle,
  Target // Added missing icon import
} from "lucide-react";
import { motion } from "framer-motion";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const userData = await User.me();
      setUser(userData);

      const profiles = await UserPrivacyProfile.filter({ created_by: userData.email }, '-created_date', 1);

      if (profiles.length > 0) {
        setProfile(profiles[0]);
      } else {
        // Create default profile if none exists
        const defaultProfileData = {
          privacy_tolerance: 'moderate',
          data_sensitivity: {
            personal_info: 3,
            tracking: 4,
            advertising: 3,
            third_party_sharing: 4,
            data_selling: 5,
            location: 4,
            biometric: 5,
            financial: 5,
            health: 5
          },
          notification_preferences: {
            policy_changes: true,
            high_risk_alerts: true,
            weekly_digest: false
          },
          analysis_history_count: 0,
          total_risk_score: 0
        };
        const newProfile = await UserPrivacyProfile.create({
          ...defaultProfileData,
          created_by: userData.email
        });
        setProfile(newProfile);
      }
    } catch (err) {
      setError("Failed to load your privacy profile. Please try again later.");
      console.error('Error loading profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      if (profile && profile.id) {
        await UserPrivacyProfile.update(profile.id, profile);
        setError('Profile saved successfully!');
      } else {
        setError('Profile not found or not initialized for saving.');
        console.error('Attempted to save profile without an ID or profile object.');
      }
    } catch (err) {
      setError("Failed to save your profile. Please check your connection and try again.");
      console.error('Error saving profile:', err);
    } finally {
      setSaving(false);
    }
  };

  const updateProfile = (updates) => {
    setProfile(prev => ({ ...prev, ...updates }));
  };

  const handleSensitivityChange = (category, value) => {
    setProfile(prev => ({
      ...prev,
      data_sensitivity: {
        ...prev.data_sensitivity,
        [category]: value
      }
    }));
  };

  const handleNotificationChange = (key, value) => {
    setProfile(prev => ({
      ...prev,
      notification_preferences: {
        ...prev.notification_preferences,
        [key]: value
      }
    }));
  };

  const getToleranceDescription = (tolerance) => {
    switch (tolerance) {
      case 'strict':
        return 'Maximum privacy protection. Flag most data usage practices.';
      case 'moderate':
        return 'Balanced approach. Alert on concerning practices only.';
      case 'relaxed':
        return 'Minimal alerts. Focus on critical privacy violations only.';
      default:
        return '';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8 flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-blue-400 animate-spin" />
      </div>
    );
  }

  if (error && error !== 'Profile saved successfully!') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8 flex items-center justify-center">
        <Alert className="max-w-lg border-red-500/50 bg-red-500/10">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <AlertDescription className="text-red-400">{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-2"
          >
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Privacy Profile
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Customize your privacy preferences to get personalized analysis and recommendations
            </p>
          </motion.div>
        </div>

        {/* Save Message (using error state for success too) */}
        {error && error === 'Profile saved successfully!' && (
          <Alert className={`border-green-500/50 bg-green-500/10`}>
            <AlertCircle className={`h-4 w-4 text-green-400`} />
            <AlertDescription className={`text-green-400`}>
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Profile Settings */}
        {profile && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid lg:grid-cols-3 gap-8">
            {/* Left Column - Main Settings */}
            <div className="lg:col-span-2 space-y-6">
              {/* Privacy Tolerance */}
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Target className="w-5 h-5 text-blue-400" />
                    Privacy Tolerance Level
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <RadioGroup
                    value={profile?.privacy_tolerance || 'moderate'}
                    onValueChange={(value) => updateProfile({ privacy_tolerance: value })}
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="strict" id="strict" />
                      <Label htmlFor="strict" className="text-white">Strict</Label>
                      <Badge variant="outline" className="border-red-500/50 text-red-400">Maximum Protection</Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="moderate" id="moderate" />
                      <Label htmlFor="moderate" className="text-white">Moderate</Label>
                      <Badge variant="outline" className="border-yellow-500/50 text-yellow-400">Balanced</Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="relaxed" id="relaxed" />
                      <Label htmlFor="relaxed" className="text-white">Relaxed</Label>
                      <Badge variant="outline" className="border-green-500/50 text-green-400">Minimal Alerts</Badge>
                    </div>
                  </RadioGroup>
                  <p className="text-sm text-gray-400">
                    {getToleranceDescription(profile?.privacy_tolerance)}
                  </p>
                </CardContent>
              </Card>

              {/* Data Sensitivity */}
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Shield className="w-5 h-5 text-blue-400" />
                    Data Sensitivity Preferences
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid md:grid-cols-2 gap-x-8 gap-y-6">
                  {Object.entries(profile.data_sensitivity).map(([key, value]) => (
                    <div key={key}>
                      <Label className="capitalize text-gray-300">{key.replace(/_/g, " ")}</Label>
                      <div className="flex items-center gap-4 mt-2">
                        <Slider
                          value={[value]}
                          onValueChange={([val]) => handleSensitivityChange(key, val)}
                          min={1}
                          max={5}
                          step={1}
                          className="w-full"
                        />
                        <Badge variant="outline" className="border-gray-700 w-24 justify-center">
                          {['Very Low', 'Low', 'Medium', 'High', 'Very High'][value - 1]}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Profile Summary & Notifications */}
            <div className="space-y-6">
              {/* Profile Summary */}
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <UserIcon className="w-5 h-5 text-blue-400" />
                    Profile Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold">
                        {user?.full_name?.[0] || 'U'}
                      </span>
                    </div>
                    <div>
                      <p className="text-white font-medium">{user?.full_name || 'User'}</p>
                      <p className="text-sm text-gray-400">{user?.email}</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Privacy Stance</span>
                      <span className="text-white capitalize">{profile?.privacy_tolerance || 'Moderate'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Analyses Done</span>
                      <span className="text-white">{profile?.analysis_history_count || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Notification Preferences */}
              <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Bell className="w-5 h-5 text-blue-400" />
                    Notifications
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {Object.entries(profile.notification_preferences).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                      <Label htmlFor={key} className="text-gray-300 capitalize">
                        {key.replace(/_/g, " ")}
                      </Label>
                      <Switch
                        id={key}
                        checked={value}
                        onCheckedChange={(checked) => handleNotificationChange(key, checked)}
                      />
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Save Button */}
              <div className="flex justify-end">
                <Button
                  onClick={handleSave}
                  disabled={saving}
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium px-8 py-3 rounded-xl shadow-lg"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" /> Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5 mr-2" /> Save Changes
                    </>
                  )}
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}