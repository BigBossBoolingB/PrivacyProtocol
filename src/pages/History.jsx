import React, { useState, useEffect } from "react";
import { PrivacyAgreement, User } from "@/api/entities";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  History as HistoryIcon, 
  Search, 
  Filter, 
  ExternalLink, 
  AlertTriangle,
  Shield,
  Calendar,
  Building2,
  FileText,
  Eye
} from "lucide-react";
import { motion } from "framer-motion";
import { format } from "date-fns";

import HistoryFilters from "../components/history/HistoryFilters";
import AgreementCard from "../components/history/AgreementCard";
import AgreementModal from "../components/history/AgreementModal";
import { useVirtualizedList } from "@/hooks/use-virtualized-list"; // Added import

// Define a fixed height for each item in the virtualized list
const ITEM_HEIGHT = 160; // Adjust this based on AgreementCard's typical height + gap

export default function History() {
  const [agreements, setAgreements] = useState([]);
  const [filteredAgreements, setFilteredAgreements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgreement, setSelectedAgreement] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    riskLevel: 'all',
    dateRange: 'all',
    sortBy: 'newest'
  });

  useEffect(() => {
    loadAgreements();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [agreements, searchTerm, filters]);

  const loadAgreements = async () => {
    try {
      const user = await User.me();
      const data = await PrivacyAgreement.filter(
        { created_by: user.email }, 
        '-created_date', 
        100
      );
      setAgreements(data);
    } catch (error) {
      console.error('Error loading agreements:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...agreements];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(agreement => 
        agreement.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agreement.company.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Risk level filter
    if (filters.riskLevel !== 'all') {
      filtered = filtered.filter(agreement => {
        const score = agreement.risk_score || 0;
        switch (filters.riskLevel) {
          case 'low': return score < 40;
          case 'medium': return score >= 40 && score < 70;
          case 'high': return score >= 70;
          default: return true;
        }
      });
    }

    // Date range filter
    if (filters.dateRange !== 'all') {
      const now = new Date();
      const cutoff = new Date();
      
      switch (filters.dateRange) {
        case 'week':
          cutoff.setDate(now.getDate() - 7);
          break;
        case 'month':
          cutoff.setMonth(now.getMonth() - 1);
          break;
        case 'quarter':
          cutoff.setMonth(now.getMonth() - 3);
          break;
      }
      
      filtered = filtered.filter(agreement => 
        new Date(agreement.created_date) >= cutoff
      );
    }

    // Sort
    switch (filters.sortBy) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_date) - new Date(a.created_date));
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_date) - new Date(b.created_date));
        break;
      case 'riskHigh':
        filtered.sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0));
        break;
      case 'riskLow':
        filtered.sort((a, b) => (a.risk_score || 0) - (b.risk_score || 0));
        break;
      case 'alphabetical':
        filtered.sort((a, b) => a.title.localeCompare(b.title));
        break;
    }

    setFilteredAgreements(filtered);
  };

  const getRiskStats = () => {
    const total = agreements.length;
    const high = agreements.filter(a => (a.risk_score || 0) >= 70).length;
    const medium = agreements.filter(a => (a.risk_score || 0) >= 40 && (a.risk_score || 0) < 70).length;
    const low = agreements.filter(a => (a.risk_score || 0) < 40).length;
    
    return { total, high, medium, low };
  };

  const stats = getRiskStats();

  const {
    containerProps,
    totalHeight,
    visibleItems
  } = useVirtualizedList({
    items: filteredAgreements,
    itemHeight: ITEM_HEIGHT,
    overscan: 5 // Render a few more items for smoother scrolling
  });

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
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Analysis History
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Review and manage your privacy agreement analyses
            </p>
          </motion.div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-white">{stats.total}</div>
              <div className="text-sm text-gray-400">Total Analyses</div>
            </CardContent>
          </Card>
          <Card className="bg-red-500/10 border-red-500/30 backdrop-blur-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-red-400">{stats.high}</div>
              <div className="text-sm text-red-400">High Risk</div>
            </CardContent>
          </Card>
          <Card className="bg-yellow-500/10 border-yellow-500/30 backdrop-blur-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-yellow-400">{stats.medium}</div>
              <div className="text-sm text-yellow-400">Medium Risk</div>
            </CardContent>
          </Card>
          <Card className="bg-green-500/10 border-green-500/30 backdrop-blur-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-green-400">{stats.low}</div>
              <div className="text-sm text-green-400">Low Risk</div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Search agreements..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-gray-900/50 border-gray-800/50 text-white placeholder-gray-400"
            />
          </div>
          <HistoryFilters 
            filters={filters}
            onFiltersChange={setFilters}
          />
        </div>

        {/* Results */}
        {/* Ensure this container has a defined height for virtualization to work */}
        <div className="space-y-6 h-[600px] overflow-y-auto" {...containerProps}>
          {loading ? (
            <div className="text-center py-12 flex flex-col items-center justify-center h-full">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4">
                <HistoryIcon className="w-8 h-8 text-white animate-pulse" />
              </div>
              <p className="text-gray-400">Loading your analysis history...</p>
            </div>
          ) : filteredAgreements.length === 0 ? (
            <div className="text-center py-12 flex flex-col items-center justify-center h-full">
              <div className="w-16 h-16 mx-auto bg-gray-700 rounded-full flex items-center justify-center mb-4">
                <Search className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-gray-400">
                {searchTerm || filters.riskLevel !== 'all' || filters.dateRange !== 'all' 
                  ? 'No agreements match your search criteria' 
                  : 'No privacy agreements analyzed yet'}
              </p>
            </div>
          ) : (
            // This inner div acts as a sizer for the scrollbar
            <div style={{ height: totalHeight }}>
              {visibleItems.map(({ item: agreement, style, index }) => (
                <div key={agreement.id || index} style={style}>
                  <div className="p-2"> {/* Adding some padding for gap effect */}
                    <AgreementCard
                      agreement={agreement}
                      onView={() => setSelectedAgreement(agreement)}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Agreement Modal */}
        {selectedAgreement && (
          <AgreementModal
            agreement={selectedAgreement}
            onClose={() => setSelectedAgreement(null)}
          />
        )}
      </div>
    </div>
  );
}