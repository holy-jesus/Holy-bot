import React from "react";
import { Shield, Plus, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/Button";
import { Moderator } from "@/types";
import { useLanguage } from "@/contexts/LanguageContext";

export const Moderators: React.FC = () => {
  const { t } = useLanguage();
  const mods: Moderator[] = [
    {
      id: "1",
      username: "Nightbot",
      addedAt: "2023-01-15",
      permissions: ["All"],
    },
    {
      id: "2",
      username: "LoyalFan99",
      addedAt: "2023-03-22",
      permissions: ["Ban", "Timeout"],
    },
    {
      id: "3",
      username: "StreamCop",
      addedAt: "2023-06-10",
      permissions: ["All"],
    },
    {
      id: "4",
      username: "PixelArtist",
      addedAt: "2023-08-05",
      permissions: ["Timeout"],
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {t("moderators.title")}
          </h1>
          <p className="text-slate-400">{t("moderators.desc")}</p>
        </div>
        <Button icon={<Plus size={16} />}>{t("moderators.add")}</Button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm text-slate-400">
          <thead className="bg-slate-800/50 text-slate-200 uppercase text-xs font-semibold">
            <tr>
              <th className="px-6 py-4">{t("moderators.tableUser")}</th>
              <th className="px-6 py-4">{t("moderators.tableRole")}</th>
              <th className="px-6 py-4">{t("moderators.tablePerms")}</th>
              <th className="px-6 py-4 text-right">
                {t("moderators.tableActions")}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {mods.map((mod) => (
              <tr
                key={mod.id}
                className="hover:bg-slate-800/30 transition-colors"
              >
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                      <Shield size={16} />
                    </div>
                    <span className="font-medium text-white">
                      {mod.username}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">{mod.addedAt}</td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    {mod.permissions.map((perm) => (
                      <span
                        key={perm}
                        className="px-2 py-1 rounded-md bg-slate-800 border border-slate-700 text-xs"
                      >
                        {perm}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="text-slate-400 hover:text-white p-1 hover:bg-slate-800 rounded">
                    <MoreHorizontal size={20} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
