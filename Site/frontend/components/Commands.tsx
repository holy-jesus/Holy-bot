import React, { useState, useCallback } from 'react';
import { Plus, Edit2, Trash2, Zap, GitMerge, Save, X, Sparkles, Bot } from 'lucide-react';
import { Button } from './Button';
import { Command, CommandMode } from '../types';
import { useLanguage } from '../contexts/LanguageContext';
import { VisualEditor } from './commands/VisualEditor';
import { generateCommandConfig } from '../services/geminiService';

export const Commands: React.FC = () => {
  const { t } = useLanguage();
  const [commands, setCommands] = useState<Command[]>([
    { id: '1', name: 'Welcome', mode: 'basic', trigger: '!hi', response: 'Welcome to the stream!', active: true, cooldown: 10 },
    { id: '2', name: 'Smart Ban', mode: 'advanced', active: true, cooldown: 0, flowData: null },
  ]);

  const [isEditing, setIsEditing] = useState(false);
  const [currentCommand, setCurrentCommand] = useState<Partial<Command>>({});
  
  // AI Generator State
  const [showAiGen, setShowAiGen] = useState(false);
  const [aiGenPrompt, setAiGenPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleCreate = () => {
    setCurrentCommand({ mode: 'basic', active: true, cooldown: 5 });
    setIsEditing(true);
  };

  const handleEdit = (cmd: Command) => {
    setCurrentCommand({ ...cmd });
    setIsEditing(true);
  };

  const handleDelete = (id: string) => {
    setCommands(commands.filter(c => c.id !== id));
  };

  const handleSave = () => {
    if (!currentCommand.name) return;

    if (currentCommand.id) {
      setCommands(commands.map(c => c.id === currentCommand.id ? { ...c, ...currentCommand } as Command : c));
    } else {
      const newCmd = { ...currentCommand, id: Date.now().toString() } as Command;
      setCommands([...commands, newCmd]);
    }
    setIsEditing(false);
    setCurrentCommand({});
  };

  const handleAiGenerate = async () => {
    if(!aiGenPrompt) return;
    setIsGenerating(true);
    const config = await generateCommandConfig(aiGenPrompt);
    setIsGenerating(false);
    
    if (config) {
        setCurrentCommand({
            ...currentCommand,
            name: config.name,
            trigger: config.trigger,
            mode: config.mode as CommandMode,
            response: config.response,
            aiPrompt: config.aiPrompt,
            cooldown: config.cooldown,
            active: true
        });
        setShowAiGen(false);
        setIsEditing(true);
        setAiGenPrompt('');
    }
  };

  // Memoized update handler for VisualEditor to ensure stability
  const handleFlowUpdate = useCallback((nodes: any[], edges: any[]) => {
    setCurrentCommand(prev => ({ ...prev, flowData: { nodes, edges } }));
  }, []);

  // Basic Editor Component
  const BasicEditor = () => (
    <div className="space-y-4 animate-in fade-in duration-300">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">{t('commands.basicTrigger')}</label>
          <input 
            type="text" 
            value={currentCommand.trigger || ''} 
            onChange={e => setCurrentCommand({ ...currentCommand, trigger: e.target.value })}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white focus:ring-1 focus:ring-brand-500 outline-none"
            placeholder="!example"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">{t('commands.cooldown')}</label>
          <input 
            type="number" 
            value={currentCommand.cooldown || 0} 
            onChange={e => setCurrentCommand({ ...currentCommand, cooldown: parseInt(e.target.value) })}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white focus:ring-1 focus:ring-brand-500 outline-none"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-400 mb-1">{t('commands.basicResponse')}</label>
        <textarea 
          value={currentCommand.response || ''} 
          onChange={e => setCurrentCommand({ ...currentCommand, response: e.target.value })}
          className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white focus:ring-1 focus:ring-brand-500 outline-none h-32 resize-none"
          placeholder="Type your response here..."
        />
      </div>
    </div>
  );

  // AI Editor Component
  const AiEditor = () => (
     <div className="space-y-4 animate-in fade-in duration-300">
        <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg flex items-start gap-3">
             <Bot className="text-purple-400 flex-shrink-0 mt-1" size={20} />
             <div>
                 <h4 className="text-sm font-semibold text-purple-200">AI Powered Command</h4>
                 <p className="text-xs text-purple-300/70 mt-1">
                     This command will use Gemini AI to generate a unique response every time it is triggered, based on your instructions.
                 </p>
             </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">{t('commands.basicTrigger')}</label>
            <input 
                type="text" 
                value={currentCommand.trigger || ''} 
                onChange={e => setCurrentCommand({ ...currentCommand, trigger: e.target.value })}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white focus:ring-1 focus:ring-purple-500 outline-none"
                placeholder="!ask"
            />
            </div>
            <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">{t('commands.cooldown')}</label>
            <input 
                type="number" 
                value={currentCommand.cooldown || 0} 
                onChange={e => setCurrentCommand({ ...currentCommand, cooldown: parseInt(e.target.value) })}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white focus:ring-1 focus:ring-purple-500 outline-none"
            />
            </div>
        </div>

        <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">{t('commands.aiPromptLabel')}</label>
            <textarea 
            value={currentCommand.aiPrompt || ''} 
            onChange={e => setCurrentCommand({ ...currentCommand, aiPrompt: e.target.value })}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white focus:ring-1 focus:ring-purple-500 outline-none h-32 resize-none"
            placeholder={t('commands.aiPromptPlaceholder')}
            />
        </div>
     </div>
  );

  return (
    <div className="space-y-6 relative">
      {/* Header */}
      {!isEditing && (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">{t('commands.title')}</h1>
            <p className="text-slate-400">{t('commands.desc')}</p>
          </div>
          <div className="flex gap-2 w-full sm:w-auto">
             <Button onClick={() => setShowAiGen(true)} variant="secondary" className="flex-1 sm:flex-none border-brand-500/50 text-brand-300 hover:text-white hover:bg-brand-500/20" icon={<Sparkles size={16} />}>
                {t('commands.generateAi')}
             </Button>
             <Button onClick={handleCreate} className="flex-1 sm:flex-none" icon={<Plus size={16} />}>{t('commands.create')}</Button>
          </div>
        </div>
      )}

      {/* AI Generator Modal Overlay */}
      {showAiGen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
                <div className="p-6 bg-gradient-to-br from-brand-900/50 to-slate-900 border-b border-slate-800 flex justify-between items-start">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-brand-500/20 rounded-lg text-brand-400">
                            <Sparkles size={20} />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-white">{t('commands.generateAi')}</h3>
                            <p className="text-xs text-slate-400">{t('commands.generateAiDesc')}</p>
                        </div>
                    </div>
                    <button onClick={() => setShowAiGen(false)} className="text-slate-500 hover:text-white"><X size={20} /></button>
                </div>
                <div className="p-6">
                    <textarea 
                        className="w-full bg-slate-950 border border-slate-700 rounded-lg p-4 text-white focus:ring-2 focus:ring-brand-500 outline-none resize-none h-32"
                        placeholder={t('commands.generatePlaceholder')}
                        value={aiGenPrompt}
                        onChange={(e) => setAiGenPrompt(e.target.value)}
                    ></textarea>
                </div>
                <div className="p-4 bg-slate-950 border-t border-slate-800 flex justify-end gap-3">
                    <Button variant="ghost" onClick={() => setShowAiGen(false)}>{t('commands.cancel')}</Button>
                    <Button 
                        disabled={!aiGenPrompt || isGenerating} 
                        onClick={handleAiGenerate}
                        icon={isGenerating ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div> : <Sparkles size={16} />}
                    >
                        {isGenerating ? t('commands.generating') : t('commands.apply')}
                    </Button>
                </div>
            </div>
        </div>
      )}

      {/* Editor Mode */}
      {isEditing ? (
        <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-2xl animate-in slide-in-from-bottom-5 duration-300">
          <div className="p-6 border-b border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900">
            <input 
              type="text" 
              value={currentCommand.name || ''} 
              onChange={e => setCurrentCommand({ ...currentCommand, name: e.target.value })}
              className="bg-transparent text-xl font-bold text-white outline-none placeholder-slate-500 w-full md:w-auto"
              placeholder="Command Name"
            />
            <div className="flex gap-1 bg-slate-800 p-1 rounded-lg border border-slate-700 w-full md:w-auto">
              <button 
                onClick={() => setCurrentCommand({ ...currentCommand, mode: 'basic' })}
                className={`flex-1 md:flex-none px-4 py-1.5 text-xs font-medium rounded-md transition-colors ${currentCommand.mode === 'basic' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}
              >
                {t('commands.modeBasic')}
              </button>
              <button 
                onClick={() => setCurrentCommand({ ...currentCommand, mode: 'ai' })}
                className={`flex-1 md:flex-none px-4 py-1.5 text-xs font-medium rounded-md transition-colors ${currentCommand.mode === 'ai' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}
              >
                {t('commands.modeAi')}
              </button>
              <button 
                onClick={() => setCurrentCommand({ ...currentCommand, mode: 'advanced' })}
                className={`flex-1 md:flex-none px-4 py-1.5 text-xs font-medium rounded-md transition-colors ${currentCommand.mode === 'advanced' ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}
              >
                {t('commands.modeAdvanced')}
              </button>
            </div>
          </div>

          <div className="p-6">
            {currentCommand.mode === 'basic' && <BasicEditor />}
            {currentCommand.mode === 'ai' && <AiEditor />}
            {currentCommand.mode === 'advanced' && (
              <div className="space-y-4 animate-in fade-in duration-300">
                 <div className="flex items-center gap-4 mb-2">
                    <label className="text-sm font-medium text-slate-400">{t('commands.cooldown')}:</label>
                    <input 
                        type="number" 
                        value={currentCommand.cooldown || 0} 
                        onChange={e => setCurrentCommand({ ...currentCommand, cooldown: parseInt(e.target.value) })}
                        className="w-24 bg-slate-900 border border-slate-800 rounded px-2 py-1 text-white text-sm outline-none focus:border-emerald-500 transition-colors"
                    />
                 </div>
                 <VisualEditor 
                    initialNodes={currentCommand.flowData?.nodes} 
                    initialEdges={currentCommand.flowData?.edges}
                    onChange={handleFlowUpdate}
                 />
              </div>
            )}
          </div>

          <div className="p-4 border-t border-slate-800 bg-slate-900 flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setIsEditing(false)}>{t('commands.cancel')}</Button>
            <Button onClick={handleSave} icon={<Save size={16} />}>{t('commands.save')}</Button>
          </div>
        </div>
      ) : (
        /* List Mode */
        <div className="grid gap-4">
          {commands.map(cmd => (
            <div key={cmd.id} className="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center justify-between hover:border-slate-700 transition-colors">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center 
                    ${cmd.mode === 'basic' ? 'bg-brand-500/10 text-brand-400' : 
                      cmd.mode === 'ai' ? 'bg-purple-500/10 text-purple-400' : 
                      'bg-emerald-500/10 text-emerald-400'}`}>
                  {cmd.mode === 'basic' ? <Zap size={24} /> : cmd.mode === 'ai' ? <Bot size={24} /> : <GitMerge size={24} />}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">{cmd.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded border 
                        ${cmd.mode === 'basic' ? 'border-brand-500/30 text-brand-400 bg-brand-500/5' : 
                          cmd.mode === 'ai' ? 'border-purple-500/30 text-purple-400 bg-purple-500/5' : 
                          'border-emerald-500/30 text-emerald-400 bg-emerald-500/5'}`}>
                        {cmd.mode === 'basic' ? t('commands.modeBasic') : cmd.mode === 'ai' ? t('commands.modeAi') : t('commands.modeAdvanced')}
                    </span>
                    {cmd.mode !== 'advanced' && <span className="text-xs text-slate-500">{cmd.trigger}</span>}
                    <span className="text-xs text-slate-500">{cmd.cooldown}s cooldown</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => handleEdit(cmd)}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <Edit2 size={18} />
                </button>
                <button 
                  onClick={() => handleDelete(cmd.id)}
                  className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};