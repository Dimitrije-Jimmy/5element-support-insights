import React, { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { api } from "@/services/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface ClassificationResult {
  category: string;
  confidence?: number;
  probabilities?: Record<string, number>;
}

const ClassifyForm: React.FC = () => {
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ClassificationResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      const response = await api.classifyMessage({ message });
      setResult(response);
    } catch (error) {
      console.error("Classification error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const copyResult = () => {
    if (result) {
      navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      toast.success("Results copied to clipboard");
    }
  };

  // Get color for category badge
  const getCategoryColor = (category: string): string => {
    const colorMap: Record<string, string> = {
      Account: "bg-blue-500",
      Deposit: "bg-green-500",
      Withdrawal: "bg-amber-500",
      Technical: "bg-purple-500",
      Security: "bg-red-500",
      Compliance: "bg-indigo-500",
      Other: "bg-gray-500",
    };
    
    return colorMap[category] || "bg-gray-500";
  };

  // Sort probabilities for display
  const sortedProbabilities = () => {
    if (!result?.probabilities) return [];
    
    return Object.entries(result.probabilities)
      .sort((a, b) => b[1] - a[1])
      .map(([category, probability]) => ({
        category,
        probability: probability * 100, // Convert to percentage
      }));
  };

  return (
    <div className="max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Textarea
          placeholder="Paste a message to classify..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="min-h-32"
        />
        <Button
          type="submit"
          disabled={!message.trim() || isLoading}
          className="rounded-full"
        >
          {isLoading ? "Classifying..." : "Classify"}
        </Button>
      </form>

      {result && (
        <Card className="mt-8 rounded-xl">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Classification Results</CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={copyResult}
              className="text-xs"
            >
              Copy JSON
            </Button>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="mb-2 text-sm font-medium">Predicted Category</div>
              <Badge className={cn("text-white", getCategoryColor(result.category))}>
                {result.category}
              </Badge>
              {result.confidence && (
                <div className="mt-2 text-sm text-muted-foreground">
                  Confidence: {(result.confidence * 100).toFixed(1)}%
                </div>
              )}
            </div>

            {result.probabilities && (
              <div>
                <div className="mb-2 text-sm font-medium">Category Probabilities</div>
                <div className="space-y-2">
                  {sortedProbabilities().map(({ category, probability }) => (
                    <div key={category} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>{category}</span>
                        <span>{probability.toFixed(1)}%</span>
                      </div>
                      <Progress value={probability} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ClassifyForm;
