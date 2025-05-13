
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface MetricsData {
  totalMessages: number;
  uniqueUsers: number;
  spikeAlerts: Array<{
    date: string;
    message: string;
  }>;
}

interface MetricsCardsProps {
  data?: MetricsData;
  isLoading: boolean;
}

const MetricsCards: React.FC<MetricsCardsProps> = ({ data, isLoading }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <Card className="rounded-xl">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Total Messages
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-8 w-16 bg-muted animate-pulse rounded" />
          ) : (
            <p className="text-2xl font-bold">
              {data ? data.totalMessages.toLocaleString() : "0"}
            </p>
          )}
        </CardContent>
      </Card>

      <Card className="rounded-xl">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Unique Users
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-8 w-16 bg-muted animate-pulse rounded" />
          ) : (
            <p className="text-2xl font-bold">
              {data ? data.uniqueUsers.toLocaleString() : "0"}
            </p>
          )}
        </CardContent>
      </Card>

      <Card className="rounded-xl">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Spike Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <div className="h-6 w-full bg-muted animate-pulse rounded" />
            </div>
          ) : data?.spikeAlerts && data.spikeAlerts.length > 0 ? (
            <div className="space-y-2">
              {data.spikeAlerts.map((alert, index) => (
                <div key={index} className="flex items-start gap-2">
                  <Badge variant="destructive" className="shrink-0">
                    {alert.date}
                  </Badge>
                  <p className="text-sm">{alert.message}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No alerts detected</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MetricsCards;
