
import React from "react";

const Navbar: React.FC = () => {
  return (
    <header className="border-b shadow-sm">
      <div className="container mx-auto px-4 h-16 flex items-center">
        <div className="flex-1">
          <h1 className="text-xl font-bold text-primary">Support Insights</h1>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
