import React from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Filter } from "lucide-react";

export default function HistoryFilters({ filters, onFiltersChange }) {
  return (
    <div className="flex gap-3">
      <Select
        value={filters.riskLevel}
        onValueChange={(value) => onFiltersChange({ ...filters, riskLevel: value })}
      >
        <SelectTrigger className="w-32 bg-gray-900/50 border-gray-800/50 text-white">
          <SelectValue placeholder="Risk Level" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Risks</SelectItem>
          <SelectItem value="high">High Risk</SelectItem>
          <SelectItem value="medium">Medium Risk</SelectItem>
          <SelectItem value="low">Low Risk</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={filters.dateRange}
        onValueChange={(value) => onFiltersChange({ ...filters, dateRange: value })}
      >
        <SelectTrigger className="w-32 bg-gray-900/50 border-gray-800/50 text-white">
          <SelectValue placeholder="Date Range" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Time</SelectItem>
          <SelectItem value="week">This Week</SelectItem>
          <SelectItem value="month">This Month</SelectItem>
          <SelectItem value="quarter">This Quarter</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={filters.sortBy}
        onValueChange={(value) => onFiltersChange({ ...filters, sortBy: value })}
      >
        <SelectTrigger className="w-32 bg-gray-900/50 border-gray-800/50 text-white">
          <SelectValue placeholder="Sort By" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="newest">Newest First</SelectItem>
          <SelectItem value="oldest">Oldest First</SelectItem>
          <SelectItem value="riskHigh">Highest Risk</SelectItem>
          <SelectItem value="riskLow">Lowest Risk</SelectItem>
          <SelectItem value="alphabetical">Alphabetical</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}