import { Search, Bell, ChevronDown } from 'lucide-react';
import { useMemo, useState } from 'react';

export default function TopNav({ onSearch }) {
  const [query, setQuery] = useState('');
  const [showProfile, setShowProfile] = useState(false);

  const notifications = useMemo(
    () => [
      '2 new high-risk prediction alerts',
      'One report export completed',
      'Patient profile updated'
    ],
    []
  );

  const handleSearch = (event) => {
    event.preventDefault();
    onSearch?.(query.trim());
  };

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur sm:px-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <form onSubmit={handleSearch} className="relative min-w-[220px] flex-1 max-w-xl">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search patients, predictions, reports..."
            className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none ring-brand-300 focus:ring"
          />
        </form>

        <div className="flex items-center gap-3">
          <button className="relative rounded-lg border border-slate-200 bg-white p-2 text-slate-600 hover:bg-slate-100">
            <Bell className="h-5 w-5" />
            <span className="absolute -right-1 -top-1 rounded-full bg-rose-500 px-1.5 text-[10px] font-semibold text-white">
              {notifications.length}
            </span>
          </button>

          <div className="relative">
            <button
              onClick={() => setShowProfile((current) => !current)}
              className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
            >
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                HS
              </span>
              <span className="hidden sm:block">Health Admin</span>
              <ChevronDown className="h-4 w-4" />
            </button>

            {showProfile ? (
              <div className="absolute right-0 mt-2 w-52 rounded-xl border border-slate-200 bg-white p-2 shadow-panel">
                <button className="w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-slate-50">Profile Settings</button>
                <button className="w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-slate-50">Notifications</button>
                <button className="w-full rounded-lg px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50">Logout</button>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </header>
  );
}
