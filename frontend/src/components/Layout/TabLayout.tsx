
import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface TabLayoutProps {
  chatContent: React.ReactNode;
  reportsContent: React.ReactNode;
  classifyContent: React.ReactNode;
  defaultValue?: string;
}

const TabLayout: React.FC<TabLayoutProps> = ({
  chatContent,
  reportsContent,
  classifyContent,
  defaultValue = "chatbot",
}) => {
  return (
    <div className="container mx-auto px-4 py-6">
      <Tabs defaultValue={defaultValue} className="fade-in">
        <div className="mb-6">
          <TabsList className="w-full sm:w-auto">
            <TabsTrigger value="chatbot" className="flex-1 sm:flex-none">Chatbot</TabsTrigger>
            <TabsTrigger value="reports" className="flex-1 sm:flex-none">Reports</TabsTrigger>
            <TabsTrigger value="classify" className="flex-1 sm:flex-none">Classify</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="chatbot" className="mt-2">
          {chatContent}
        </TabsContent>

        <TabsContent value="reports" className="mt-2">
          {reportsContent}
        </TabsContent>

        <TabsContent value="classify" className="mt-2">
          {classifyContent}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TabLayout;
