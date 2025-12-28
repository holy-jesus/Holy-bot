import React, { useState } from 'react';
import { Timer as TimerIcon, Plus, Trash2, Clock, Edit2 } from 'lucide-react';
import { Button } from './Button';
import { Timer } from '../types';
import { useLanguage } from '../contexts/LanguageContext';

export const Timers: React.FC = () => {
  const { t } = useLanguage();
  const [timers, setTimers] = useState<Timer[]>([
    { id: '1', name: 'Follow Reminder', interval: 15, message: 'Don\'t forget to follow the channel if you are enjoying the stream!', active: true },
    { id: '2', name: 'Discord Link', interval: 30, message: 'Join our community discord: discord.gg/holybot', active: true },
    { id: '3', name: 'Prime Sub', interval: 60, message: 'Use your Twitch Prime to sub for free!', active: false },
  ]);

  const toggleTimer = (id: string) => {
    setTimers(timers.map(t => t.id === id ? { ...t, active: !t.active } : t));
  };

  const deleteTimer = (id: string) => {
    setTimers(timers.filter(t => t.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">{t('timers.title')}</h1>
          <p className="text-slate-400">{t('timers.desc')}</p>
        </div>
        <Button icon={<Plus size={16} />}>{t('timers.create')}</Button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="grid grid-cols-1 divide-y divide-slate-800">
          {timers.map(timer => (
            <div key={timer.id} className="p-4 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-800/30 transition-colors">
              <div className="flex items-start space-x-4">
                <div className={`mt-1 p-2 rounded-lg ${timer.active ? 'bg-brand-500/10 text-brand-400' : 'bg-slate-800 text-slate-500'}`}>
                  <TimerIcon size={24} />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-medium text-white">{timer.name}</h3>
                    <span className="flex items-center text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full border border-slate-700">
                      <Clock size={12} className="mr-1" />
                      {t('timers.every')} {timer.interval}{t('timers.minutes')}
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm mt-1">{timer.message}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 sm:ml-auto">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    className="sr-only peer" 
                    checked={timer.active}
                    onChange={() => toggleTimer(timer.id)}
                  />
                  <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-brand-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-600"></div>
                </label>
                <div className="h-6 w-px bg-slate-700 mx-2"></div>
                <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
                  <Edit2 size={18} />
                </button>
                <button 
                  onClick={() => deleteTimer(timer.id)}
                  className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};