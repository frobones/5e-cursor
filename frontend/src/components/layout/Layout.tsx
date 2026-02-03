import { useState } from 'react';

import { useFileChanges } from '@hooks/useFileChanges';

import Header from './Header';
import styles from './Layout.module.css';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Connect to WebSocket for real-time file change notifications
  useFileChanges();

  return (
    <div className={styles.container}>
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className={styles.main}>
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className={styles.content}>
          {children}
        </main>
      </div>
    </div>
  );
}
