import React, { useState } from "react";
import FilterPanel, { FiltersState } from "./FilterPanel";
import MetricsCards from "./MetricsCards";
import Charts from "./Charts";
import { api } from "@/services/api";

const initialMetricsData = {
  totalMessages: 0,
  uniqueUsers: 0,
  spikeAlerts: [],
  daily_counts: []
};

const ReportsPanel: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [metricsData, setMetricsData] = useState(initialMetricsData);

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
        totalMessages: response.total_messages || 0,
        uniqueUsers: response.unique_users || 0,
        spikeAlerts: response.spike_alerts || [],
        daily_counts: response.daily_counts || [],
      });
    } catch (error) {
      console.error("Error fetching metrics:", error);
      setMetricsData(initialMetricsData);
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
