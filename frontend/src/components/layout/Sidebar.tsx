import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  MapPin,
  Calendar,
  Shield,
  Sword,
  Clock,
  GitBranch,
  BookOpen,
  HelpCircle,
  ChevronLeft,
} from 'lucide-react';
import clsx from 'clsx';
import styles from './Sidebar.module.css';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/npcs', icon: Users, label: 'NPCs' },
  { to: '/locations', icon: MapPin, label: 'Locations' },
  { to: '/sessions', icon: Calendar, label: 'Sessions' },
  { to: '/party', icon: Shield, label: 'Party' },
  { to: '/encounters', icon: Sword, label: 'Encounters' },
  { to: '/timeline', icon: Clock, label: 'Timeline' },
  { to: '/relationships', icon: GitBranch, label: 'Relationships' },
  { to: '/reference', icon: BookOpen, label: 'Reference' },
  { to: '/docs', icon: HelpCircle, label: 'Docs' },
];

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  return (
    <aside className={clsx(styles.sidebar, !isOpen && styles.collapsed)}>
      <div className={styles.header}>
        <span className={styles.logo}>5e</span>
        {isOpen && <span className={styles.logoText}>Campaign</span>}
        <button
          onClick={onToggle}
          className={styles.collapseButton}
          aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          <ChevronLeft className={clsx('h-4 w-4', !isOpen && 'rotate-180')} />
        </button>
      </div>

      <nav className={styles.nav}>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(styles.navItem, isActive && styles.navItemActive)
            }
            title={!isOpen ? label : undefined}
          >
            <Icon className="h-5 w-5 flex-shrink-0" />
            {isOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
