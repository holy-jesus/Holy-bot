import { Heart, DollarSign, ArrowRight, Construction, Send, Github } from 'lucide-react'

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 z-0 opacity-[0.1] md:opacity-[0.15]"
        style={{
          backgroundImage: `linear-gradient(to right, #334155 1px, transparent 1px), linear-gradient(to bottom, #334155 1px, transparent 1px)`,
          backgroundSize: '32px 32px',
          maskImage: 'radial-gradient(ellipse at center, black, transparent 85%)'
        }}>
      </div>

      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] md:w-[600px] h-[300px] md:h-[600px] bg-brand-500/10 rounded-full blur-[80px] md:blur-[120px] pointer-events-none"></div>

      <div className="absolute top-4 right-4 md:top-6 md:right-6 z-20 flex items-center gap-2">
        <a
          href="https://github.com/holy-jesus/Holy-bot"
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 md:px-4 md:py-2 rounded-full bg-slate-900/50 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 hover:bg-slate-800 transition-all backdrop-blur-sm group flex items-center gap-2"
          title="GitHub Repository"
        >
          <Github size={18} className="group-hover:scale-110 transition-transform" />
          <span className="hidden md:inline text-sm font-medium tracking-wide">GitHub</span>
        </a>
        <a
          href="https://t.me/ho1y_jesus"
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 md:px-4 md:py-2 rounded-full bg-slate-900/50 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 hover:bg-slate-800 transition-all backdrop-blur-sm group flex items-center gap-2"
        >
          <Send size={18} className="text-brand-400 group-hover:scale-110 transition-transform" />
          <span className="hidden md:inline text-sm font-medium tracking-wide">Связаться</span>
        </a>
      </div>

      <main className="max-w-2xl w-full space-y-12 relative z-10 text-center">
        <div className="space-y-6">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-400 to-cyan-500 flex items-center justify-center shadow-2xl shadow-brand-500/20">
              {/* <Bot className="text-white" size={44} /> */}
              <img src="/src/assets/BotAVA512.png" alt="Logo" className="w-16 h-16 rounded-2xl" />
            </div>
          </div>

          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-400 text-xs font-medium">
            <Construction size={14} className="text-brand-400" />
            <span>В разработке</span>
          </div>
        </div>

        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-white leading-tight">
            Грядёт нечто <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-cyan-500">божественное</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-xl mx-auto leading-relaxed">
            В декабре 2025 года, после обновления Twitch, прошлая версия бота перестала работать. Вместо временного решения, я решил наконец-то уделить боту заслуженное внимание.<br />Новая версия с полноценным профилем, кастомными командами и многим другим находится в активной разработке.
          </p>
        </div>

        <div className="bg-slate-900/40 border border-slate-800/50 rounded-2xl p-8 backdrop-blur-md relative group overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-brand-500/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

          <div className="relative space-y-4">
            <div className="inline-flex p-3 bg-slate-800 rounded-xl text-brand-400 border border-slate-700">
              <Heart size={24} />
            </div>
            <h2 className="text-2xl font-bold text-white">Поддержать разработку</h2>
            <p className="text-slate-400 text-sm md:text-base">
              Данный проект делается в свободное время и без финансирования. В нём{' '}
              <span className="relative inline-block font-semibold text-white group/never">
                никогда
                <span className="absolute -bottom-0.5 left-0 w-full h-px bg-gradient-to-r from-brand-400 to-cyan-500 opacity-70 transition-opacity"></span>
              </span>{' '}
              не будет рекламы, отслеживания, платных функций и прочего.<br />Если есть возможность, поддержите разработку.<br />Спасибо!
            </p>
            <div className="pt-4 flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-8 py-3 bg-white text-slate-950 font-semibold rounded-xl hover:bg-slate-100 transition-all flex items-center justify-center gap-2 group/btn shadow-lg shadow-white/5 cursor-pointer" onClick={() => window.location.href = "https://pay.cloudtips.ru/p/04eb86a5"}>
                <DollarSign size={18} />
                Поддержать
                <ArrowRight size={16} className="-translate-x-1 group-hover/btn:translate-x-0 transition-all" />
              </button>
            </div>
          </div>
        </div>

        <div className="pt-12 text-slate-500 text-sm flex items-center justify-center gap-2">
          {/* <Sparkles size={14} className="text-brand-500" /> */}
          <Heart size={14} className="text-red-500 animate-pulse" />
          <span>Сделано <a href="https://t.me/ho1y_jesus" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-brand-400 transition-colors font-medium border-b border-transparent hover:border-brand-400/30">holy_jesus</a> с любовью</span>
        </div>
      </main>
    </div>
  )
}

export default App
