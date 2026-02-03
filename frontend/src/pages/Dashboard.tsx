import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Users,
  MapPin,
  Calendar,
  Shield,
  Sword,
  Clock,
  GitBranch,
  BookOpen,
  HelpCircle,
} from 'lucide-react';
import {
  getCampaign,
  getSessions,
  getRelationships,
  getReferenceIndex,
  getDocs,
} from '@services/api';
import styles from './Dashboard.module.css';

export default function Dashboard() {
  const { data: campaign, isLoading, error } = useQuery({
    queryKey: ['campaign'],
    queryFn: getCampaign,
  });

  const { data: sessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: getSessions,
  });

  const { data: relationships } = useQuery({
    queryKey: ['relationships'],
    queryFn: getRelationships,
  });

  const { data: referenceIndex } = useQuery({
    queryKey: ['referenceIndex'],
    queryFn: getReferenceIndex,
  });

  const { data: docs } = useQuery({
    queryKey: ['docs'],
    queryFn: getDocs,
  });

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <p>Loading campaign...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.error}>
        <h2>No Campaign Found</h2>
        <p>Initialize a campaign to get started:</p>
        <pre>python scripts/campaign/init_campaign.py "Your Campaign"</pre>
      </div>
    );
  }

  const recentSessions = sessions?.slice(0, 5) || [];

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>{campaign?.name}</h1>
        {campaign?.setting &&
          campaign.setting !== '[Your setting here]' && (
            <p className={styles.setting}>{campaign.setting}</p>
          )}
      </header>

      {/* Unified Campaign Navigation Grid */}
      <section className={styles.statsSection}>
        <h2>Campaign</h2>
        <div className={styles.statsGrid}>
          <Link to="/npcs" className={styles.stat}>
            <Users className="h-8 w-8 text-green-600" />
            <div>
              <p className={styles.statValue}>{campaign?.stats.npcs || 0}</p>
              <p className={styles.statLabel}>NPCs</p>
            </div>
          </Link>
          <Link to="/locations" className={styles.stat}>
            <MapPin className="h-8 w-8 text-blue-600" />
            <div>
              <p className={styles.statValue}>{campaign?.stats.locations || 0}</p>
              <p className={styles.statLabel}>Locations</p>
            </div>
          </Link>
          <Link to="/sessions" className={styles.stat}>
            <Calendar className="h-8 w-8 text-purple-600" />
            <div>
              <p className={styles.statValue}>{campaign?.stats.sessions || 0}</p>
              <p className={styles.statLabel}>Sessions</p>
            </div>
          </Link>
          <Link to="/party" className={styles.stat}>
            <Shield className="h-8 w-8 text-amber-600" />
            <div>
              <p className={styles.statValue}>{campaign?.stats.party_size || 0}</p>
              <p className={styles.statLabel}>Party</p>
            </div>
          </Link>
          <Link to="/encounters" className={styles.stat}>
            <Sword className="h-8 w-8 text-red-600" />
            <div>
              <p className={styles.statValue}>{campaign?.stats.encounters || 0}</p>
              <p className={styles.statLabel}>Encounters</p>
            </div>
          </Link>
          <Link to="/timeline" className={styles.stat}>
            <Clock className="h-8 w-8 text-cyan-600" />
            <div>
              <p className={styles.statValue}>Day {campaign?.current_session || 1}</p>
              <p className={styles.statLabel}>Timeline</p>
            </div>
          </Link>
          <Link to="/relationships" className={styles.stat}>
            <GitBranch className="h-8 w-8 text-pink-600" />
            <div>
              <p className={styles.statValue}>{relationships?.edges?.length ?? 0}</p>
              <p className={styles.statLabel}>Relationships</p>
            </div>
          </Link>
          <Link to="/reference" className={styles.stat}>
            <BookOpen className="h-8 w-8 text-indigo-600" />
            <div>
              <p className={styles.statValue}>{referenceIndex?.total_entries?.toLocaleString() ?? 0}</p>
              <p className={styles.statLabel}>Reference</p>
            </div>
          </Link>
          <Link to="/docs" className={styles.stat}>
            <HelpCircle className="h-8 w-8 text-parchment-600" />
            <div>
              <p className={styles.statValue}>{docs?.length ?? 0}</p>
              <p className={styles.statLabel}>Docs</p>
            </div>
          </Link>
        </div>
      </section>

      {/* Recent Sessions */}
      {recentSessions.length > 0 && (
        <section className={styles.sessionsSection}>
          <h2>Recent Sessions</h2>
          <div className={styles.sessionsList}>
            {recentSessions.map((session) => (
              <Link
                key={session.number}
                to={`/sessions/${session.number}`}
                className={styles.sessionCard}
              >
                <div className={styles.sessionNumber}>
                  Session {session.number}
                </div>
                <div className={styles.sessionTitle}>{session.title}</div>
                <div className={styles.sessionMeta}>
                  <span>{session.date}</span>
                  {session.in_game_date && (
                    <span className={styles.inGameDate}>
                      {session.in_game_date}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
