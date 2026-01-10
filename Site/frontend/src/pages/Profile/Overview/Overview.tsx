import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { MessageSquare, Users, Zap, TrendingUp, Activity } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const dataActivity = [
  { name: "10:00", messages: 400 },
  { name: "11:00", messages: 300 },
  { name: "12:00", messages: 550 },
  { name: "13:00", messages: 800 },
  { name: "14:00", messages: 600 },
  { name: "15:00", messages: 950 },
  { name: "16:00", messages: 1200 },
];

const dataCommands = [
  { name: "!discord", usage: 120 },
  { name: "!lurk", usage: 98 },
  { name: "!prime", usage: 86 },
  { name: "!follow", usage: 65 },
  { name: "!uptime", usage: 45 },
];

export const Overview: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          {t("dashboard.overviewTitle")}
        </h1>
        <p className="text-slate-400">{t("dashboard.overviewDesc")}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title={t("dashboard.totalMessages")}
          value="14.2k"
          change="+12%"
          icon={<MessageSquare className="text-brand-400" size={24} />}
        />
        <StatsCard
          title={t("dashboard.activeChatters")}
          value="1,234"
          change="+5%"
          icon={<Users className="text-blue-400" size={24} />}
        />
        <StatsCard
          title={t("dashboard.commandsUsed")}
          value="856"
          change="-2%"
          isNegative
          icon={<Zap className="text-amber-400" size={24} />}
        />
        <StatsCard
          title={t("dashboard.uptime")}
          value="4h 12m"
          icon={<Activity className="text-emerald-400" size={24} />}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <TrendingUp className="mr-2 text-brand-400" size={20} />
              {t("dashboard.chatActivity")}
            </h3>
            <select className="bg-slate-800 border-none text-xs rounded-md text-slate-300 focus:ring-1 focus:ring-brand-500">
              <option>Last 6 Hours</option>
              <option>Last 24 Hours</option>
              <option>Last 7 Days</option>
            </select>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dataActivity}>
                <defs>
                  <linearGradient
                    id="colorMessages"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1e293b"
                  vertical={false}
                />
                <XAxis
                  dataKey="name"
                  stroke="#64748b"
                  tick={{ fontSize: 12 }}
                />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    color: "#f8fafc",
                  }}
                  itemStyle={{ color: "#a78bfa" }}
                />
                <Area
                  type="monotone"
                  dataKey="messages"
                  stroke="#8b5cf6"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#colorMessages)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Commands */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">
            {t("dashboard.topCommands")}
          </h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={dataCommands}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1e293b"
                  horizontal={false}
                />
                <XAxis type="number" stroke="#64748b" hide />
                <YAxis
                  dataKey="name"
                  type="category"
                  stroke="#94a3b8"
                  width={70}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  cursor={{ fill: "#1e293b" }}
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    color: "#f8fafc",
                  }}
                />
                <Bar
                  dataKey="usage"
                  fill="#a78bfa"
                  radius={[0, 4, 4, 0]}
                  barSize={20}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

interface StatsCardProps {
  title: string;
  value: string;
  change?: string;
  isNegative?: boolean;
  icon: React.ReactNode;
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  isNegative,
  icon,
}) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
    <div className="flex justify-between items-start mb-4">
      <div className="p-2 bg-slate-800/50 rounded-lg">{icon}</div>
      {change && (
        <span
          className={`text-xs font-medium px-2 py-1 rounded-full ${isNegative ? "bg-red-500/10 text-red-400" : "bg-emerald-500/10 text-emerald-400"}`}
        >
          {change}
        </span>
      )}
    </div>
    <p className="text-slate-400 text-sm">{title}</p>
    <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
  </div>
);
