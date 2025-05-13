
import { toast } from "sonner";

const BASE_URL = "/api/v1";

interface ChatRequest {
  message: string;
  history: Array<{
    role: "user" | "assistant";
    content: string;
  }>;
}

interface MetricsRequest {
  category?: string[];
  source?: string;
  start: string;
  end: string;
}

interface ClassifyRequest {
  message: string;
}

interface ChatResponse {
  response: string;
  context?: string;
}

interface MetricsResponse {
  total_messages: number;
  unique_users: number;
  spike_alerts: Array<{
    date: string;
    message: string;
  }>;
  daily_counts: Array<{
    date: string;
    count: number;
    categories?: Record<string, number>;
  }>;
}

interface ClassifyResponse {
  category: string;
  confidence?: number;
  probabilities?: Record<string, number>;
}

const handleError = (error: Error) => {
  console.error("API Error:", error);
  toast.error("Unable to reach backend");
  throw error;
};

export const api = {
  // Chat endpoint
  sendChatMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    try {
      const response = await fetch(`${BASE_URL}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      return handleError(error as Error);
    }
  },
  
  // Stream chat response
  streamChatMessage: async (request: ChatRequest): Promise<ReadableStream> => {
    try {
      const response = await fetch(`${BASE_URL}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "text/event-stream",
        },
        body: JSON.stringify(request),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return response.body!;
    } catch (error) {
      handleError(error as Error);
      throw error;
    }
  },

  // Messages metrics endpoint
  getMessagesMetrics: async (params: MetricsRequest): Promise<MetricsResponse> => {
    try {
      const queryParams = new URLSearchParams();
      
      if (params.category && params.category.length > 0) {
        queryParams.set("category", params.category.join(","));
      }
      
      if (params.source) {
        queryParams.set("source", params.source);
      }
      
      queryParams.set("start", params.start);
      queryParams.set("end", params.end);
      
      const response = await fetch(
        `${BASE_URL}/messages/metrics?${queryParams.toString()}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      return handleError(error as Error);
    }
  },

  // Classify endpoint
  classifyMessage: async (request: ClassifyRequest): Promise<ClassifyResponse> => {
    try {
      const response = await fetch(`${BASE_URL}/messages/classify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      return handleError(error as Error);
    }
  },
};
