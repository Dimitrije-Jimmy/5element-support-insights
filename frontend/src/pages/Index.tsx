
import Navbar from "@/components/Layout/Navbar";
import TabLayout from "@/components/Layout/TabLayout";
import ChatPanel from "@/components/Chat/ChatPanel";
import ReportsPanel from "@/components/Reports/ReportsPanel";
import ClassifyForm from "@/components/Classify/ClassifyForm";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col bg-background font-inter">
      <Navbar />
      <main className="flex-1 pb-12">
        <TabLayout
          chatContent={<ChatPanel />}
          reportsContent={<ReportsPanel />}
          classifyContent={<ClassifyForm />}
          defaultValue="chatbot"
        />
      </main>
    </div>
  );
};

export default Index;
