
import React, { useState } from "react";
import FilterPanel, { FiltersState } from "./FilterPanel";
import MetricsCards from "./MetricsCards";
import Charts from "./Charts";
import { api } from "@/services/api";

const ReportsPanel: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [metricsData, setMetricsData] = useState<any>(null);

  const handleApplyFilters = async (filters: FiltersState) => {
    setIsLoading(true);
    
    try {
      const response = await api.getMessagesMetrics({
        category: filters.categories,
        source: filters.source === "any" ? undefined : filters.source,
        start: filters.dateRange.start,
        end: filters.dateRange.end,
      });
      
      setMetricsData({
        totalMessages: response.total_messages,
        uniqueUsers: response.unique_users,
        spikeAlerts: response.spike_alerts,
        daily_counts: response.daily_counts,
      });
    } catch (error) {
      console.error("Error fetching metrics:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-6">
      <div className="w-full md:w-64 shrink-0">
        <FilterPanel onApplyFilters={handleApplyFilters} isLoading={isLoading} />
      </div>
      
      <div className="flex-1">
        <MetricsCards
          data={metricsData}
          isLoading={isLoading}
        />
        <Charts
          data={metricsData}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
};

export default ReportsPanel;
