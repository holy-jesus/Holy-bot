import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { LandingPage } from "@/pages/Landing/Landing";
import { DashboardLayout } from "@/pages/Profile/DashboardLayout";
import { Overview } from "@/pages/Profile/Overview/Overview";
import { Timers } from "@/pages/Profile/Timers/Timers";
import { Moderators } from "@/pages/Profile/Moderators/Moderators";
import { AskAi } from "@/pages/Profile/AI/AskAi";
import { Commands } from "@/pages/Profile/Commands/Commands";
import { Menu, Bell, User as UserIcon, Search, Globe } from "lucide-react";
import { BotStatus } from "@/types";
import { LanguageProvider, useLanguage } from "@/contexts/LanguageContext";

const AppContent: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activePage, setActivePage] = useState("overview");
  const { language, setLanguage } = useLanguage();

  const handleLogout = () => {
    setIsLoggedIn(false);
    setActivePage("overview");
  };

  // Main Dashboard Layout Wrapper

  // Render specific content based on activePage state (Client-side simple routing for demo)
  const renderContent = () => {
    switch (activePage) {
      case "overview":
        return;
      case "commands":
        return <Commands />;
      case "timers":
        return <Timers />;
      case "moderators":
        return <Moderators />;
      case "ai-chat":
        return <AskAi />;
      default:
        return (
          <div className="text-center text-slate-500 mt-20">
            Page not found or under construction.
          </div>
        );
    }
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />}></Route>
      </Routes>
    </BrowserRouter>
  );
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/dashboard",
    element: <DashboardLayout />,
    children: [
      {
        index: true,
        element: <Overview />,
      },
      {
        path: "timers",
        element: <Timers />,
      },
      {
        path: "commands",
        element: <Commands />,
      },
    ],
  },
]);

export default function App() {
  return (
    <LanguageProvider>
      <RouterProvider router={router} />
    </LanguageProvider>
  );
}
