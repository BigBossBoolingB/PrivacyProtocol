import React, { useState } from 'react';
import { useApiQuery, useApiMutation } from '@/hooks';
import { policyMonitor } from '@/api/functions';
import { URLAnalyzer } from '@/components/analyzer';

function PolicyMonitoringSetup() {
  const [monitoringUrl, setMonitoringUrl] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [frequency, setFrequency] = useState('weekly');
  const [notifications, setNotifications] = useState(true);

  const { data: activeMonitors, refetch: refreshMonitors } = useApiQuery(
    'activeMonitors',
    () => policyMonitor({ action: 'list' })
  );

  const { mutate: setupMonitoring, loading } = useApiMutation(
    (params) => policyMonitor(params),
    {
      onSuccess: (result) => {
        alert(`Monitoring setup successful! Monitor ID: ${result.monitor_id}`);
        refreshMonitors();
        setMonitoringUrl('');
        setCompanyName('');
      },
      onError: (error) => {
        alert(`Failed to setup monitoring: ${error.message}`);
      }
    }
  );

  const handleSetupMonitoring = () => {
    if (!monitoringUrl || !companyName) {
      alert('Please fill in all required fields');
      return;
    }

    setupMonitoring({
      url: monitoringUrl,
      company_name: companyName,
      frequency,
      notify_changes: notifications
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Policy Monitoring Setup</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Add New Monitor</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Privacy Policy URL *
            </label>
            <input
              type="url"
              value={monitoringUrl}
              onChange={(e) => setMonitoringUrl(e.target.value)}
              className="w-full p-2 border rounded-md"
              placeholder="https://example.com/privacy-policy"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Company Name *
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full p-2 border rounded-md"
              placeholder="Company Name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Check Frequency
            </label>
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              className="w-full p-2 border rounded-md"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="notifications"
              checked={notifications}
              onChange={(e) => setNotifications(e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="notifications" className="text-sm">
              Send notifications when changes are detected
            </label>
          </div>
          
          <button
            onClick={handleSetupMonitoring}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50"
          >
            {loading ? 'Setting up...' : 'Setup Monitoring'}
          </button>
        </div>
      </div>

      {activeMonitors && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Active Monitors</h2>
          {activeMonitors.length === 0 ? (
            <p className="text-gray-600">No active monitors yet.</p>
          ) : (
            <div className="space-y-3">
              {activeMonitors.map((monitor) => (
                <div key={monitor.monitor_id} className="border rounded-md p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{monitor.company_name}</p>
                      <p className="text-sm text-gray-600">{monitor.url}</p>
                      <p className="text-xs text-gray-500">
                        Frequency: {monitor.frequency} | Status: {monitor.status}
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded ${
                      monitor.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {monitor.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PolicyMonitoringSetup;
