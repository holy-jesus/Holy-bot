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
import { LanguageProvider } from "@/contexts/LanguageContext";

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
      {
        path: "moderators",
        element: <Moderators />,
      },
      {
        path: "ai",
        element: <AskAi />,
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
