
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";

interface ChartData {
  daily_counts: Array<{
    date: string;
    count: number;
    categories?: Record<string, number>;
  }>;
}

interface ChartsProps {
  data?: ChartData;
  isLoading: boolean;
}

const Charts: React.FC<ChartsProps> = ({ data, isLoading }) => {
  // Prepare data for the stacked bar chart
  const stackedBarData = React.useMemo(() => {
    if (!data?.daily_counts) return [];

    return data.daily_counts.map((item) => {
      const categories = item.categories || {};
      return {
        date: item.date,
        ...categories,
      };
    });
  }, [data]);

  // Get unique category names for the stacked bar chart
  const categoryNames = React.useMemo(() => {
    if (!data?.daily_counts) return [];

    const names = new Set<string>();
    data.daily_counts.forEach((item) => {
      if (item.categories) {
        Object.keys(item.categories).forEach((category) => names.add(category));
      }
    });
    return Array.from(names);
  }, [data]);

  // Generate colors for each category
  const categoryColors = React.useMemo(() => {
    const colors = [
      "#2563EB", // Primary blue
      "#10B981", // Green
      "#F59E0B", // Amber
      "#8B5CF6", // Purple
      "#EC4899", // Pink
      "#06B6D4", // Cyan
      "#F97316", // Orange
    ];

    return categoryNames.reduce((acc, category, index) => {
      acc[category] = colors[index % colors.length];
      return acc;
    }, {} as Record<string, string>);
  }, [categoryNames]);

  return (
    <div className="space-y-6">
      <Card className={cn("rounded-xl overflow-hidden")}>
        <CardHeader>
          <CardTitle>Daily Message Count</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="w-full h-64 bg-muted animate-pulse rounded" />
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <LineChart
                data={data?.daily_counts || []}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#2563EB"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {categoryNames.length > 0 && (
        <Card className="rounded-xl overflow-hidden">
          <CardHeader>
            <CardTitle>Messages by Category</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="w-full h-64 bg-muted animate-pulse rounded" />
            ) : (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart
                  data={stackedBarData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {categoryNames.map((category) => (
                    <Bar
                      key={category}
                      dataKey={category}
                      stackId="a"
                      fill={categoryColors[category]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Charts;
