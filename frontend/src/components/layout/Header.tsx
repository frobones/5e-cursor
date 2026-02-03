import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Menu, Search, Sun, Moon } from 'lucide-react';
import { getCampaign } from '@services/api';
import SearchModal from '../SearchModal';
import styles from './Header.module.css';

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [searchOpen, setSearchOpen] = useState(false);
  
  const { data: campaign } = useQuery({
    queryKey: ['campaign'],
    queryFn: getCampaign,
  });

  useEffect(() => {
    // Check for saved theme or system preference
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setTheme('dark');
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Cmd+K keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark');
  };

  const openSearch = useCallback(() => setSearchOpen(true), []);
  const closeSearch = useCallback(() => setSearchOpen(false), []);

  return (
    <>
      <header className={styles.header}>
        <div className={styles.left}>
          <button
            onClick={onMenuClick}
            className={styles.menuButton}
            aria-label="Toggle sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>
          <h1 className={styles.title}>
            {campaign?.name || 'Campaign'}
          </h1>
        </div>
        
        <div className={styles.right}>
          <button
            onClick={openSearch}
            className={styles.searchButton}
            aria-label="Search"
          >
            <Search className="h-5 w-5" />
            <span className={styles.searchText}>Search</span>
            <kbd className={styles.searchKbd}>⌘K</kbd>
          </button>
          
          <button
            onClick={toggleTheme}
            className={styles.themeButton}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>
        </div>
      </header>

      <SearchModal isOpen={searchOpen} onClose={closeSearch} />
    </>
  );
}
