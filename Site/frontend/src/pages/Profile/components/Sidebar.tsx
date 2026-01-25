import React from "react";
import {
  LayoutDashboard,
  Command,
  Timer,
  Shield,
  Settings,
  LogOut,
  Bot,
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { logout } from "@/services/auth";

export const Sidebar: React.FC = ({ }) => {
  const { t } = useLanguage();

  const menuItems = [
    {
      id: "overview",
      label: t("sidebar.overview"),
      icon: <LayoutDashboard size={20} />,
    },
    {
      id: "commands",
      label: t("sidebar.commands"),
      icon: <Command size={20} />,
    },
    { id: "timers", label: t("sidebar.timers"), icon: <Timer size={20} /> },
    {
      id: "moderators",
      label: t("sidebar.moderators"),
      icon: <Shield size={20} />,
    },
    { id: "ai-chat", label: t("sidebar.askAi"), icon: <Bot size={20} /> },
    {
      id: "settings",
      label: t("sidebar.settings"),
      icon: <Settings size={20} />,
    },
  ];

  return (
    <aside
      className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 transform transition-transform duration-300 ease-in-out
        ${true ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 lg:static lg:block
      `}
    >
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center px-6 h-16 border-b border-slate-800">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center mr-3 shadow-lg shadow-brand-500/20">
            <Bot className="text-white" size={20} />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            Holy-bot
          </span>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {menuItems.map((item) => (
            <button
              key={item.id}
              className={`
                w-full flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200
                ${true
                  ? "bg-brand-500/10 text-brand-400 border border-brand-500/20 shadow-sm"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800"
                }
              `}
            >
              <span
                className={`mr-3 ${true ? "text-brand-400" : "text-slate-500 group-hover:text-slate-300"}`}
              >
                {item.icon}
              </span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* User / Logout */}
        <div className="p-4 border-t border-slate-800">
          <button className="w-full flex items-center px-3 py-2.5 text-sm font-medium text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors" onClick={logout}>
            <LogOut size={20} className="mr-3" />
            {t("sidebar.signOut")}
          </button>
        </div>
      </div>
    </aside>
  );
};
