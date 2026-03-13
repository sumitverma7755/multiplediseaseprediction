import { LayoutDashboard, UsersRound, History, Stethoscope, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';

const items = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/patients', label: 'Patients', icon: UsersRound },
  { to: '/history', label: 'History', icon: History }
];

export default function Sidebar({ isOpen, setIsOpen }) {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 w-72 transform border-r border-slate-200 bg-white transition duration-200 lg:static lg:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-4">
          <Link to="/" className="flex items-center gap-2 text-slate-900">
            <span className="rounded-lg bg-brand-600 p-2 text-white">
              <Stethoscope className="h-4 w-4" />
            </span>
            <span className="font-semibold">Health AI Studio</span>
          </Link>
          <button className="lg:hidden" onClick={() => setIsOpen(false)}>
            <PanelLeftClose className="h-5 w-5 text-slate-600" />
          </button>
        </div>

        <nav className="flex-1 space-y-2 px-3 py-5">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setIsOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition ${
                    isActive
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        <div className="border-t border-slate-200 p-4 text-xs text-slate-500">
          Production-ready modules with AI explainability and report automation.
        </div>
      </div>
    </aside>
  );
}

export function SidebarToggle({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 lg:hidden"
    >
      <PanelLeftOpen className="h-4 w-4" />
      Menu
    </button>
  );
}
