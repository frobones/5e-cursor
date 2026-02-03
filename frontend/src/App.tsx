import { Routes, Route } from 'react-router-dom';

import Layout from '@components/layout/Layout';
import Dashboard from '@pages/Dashboard';
import NPCs from '@pages/NPCs';
import NPCDetail from '@pages/NPCDetail';
import Locations from '@pages/Locations';
import LocationDetail from '@pages/LocationDetail';
import Sessions from '@pages/Sessions';
import SessionDetail from '@pages/SessionDetail';
import Party from '@pages/Party';
import CharacterDetail from '@pages/CharacterDetail';
import Encounters from '@pages/Encounters';
import EncounterDetail from '@pages/EncounterDetail';
import EncounterBuilder from '@pages/EncounterBuilder';
import EncounterRunner from '@pages/EncounterRunner';
import Timeline from '@pages/Timeline';
import Relationships from '@pages/Relationships';
import Reference from '@pages/Reference';
import ReferenceDetail from '@pages/ReferenceDetail';
import Docs from '@pages/Docs';
import DocDetail from '@pages/DocDetail';
import NotFound from '@pages/NotFound';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        
        {/* Entity routes */}
        <Route path="/npcs" element={<NPCs />} />
        <Route path="/npcs/:slug" element={<NPCDetail />} />
        <Route path="/locations" element={<Locations />} />
        <Route path="/locations/:slug" element={<LocationDetail />} />
        <Route path="/sessions" element={<Sessions />} />
        <Route path="/sessions/:number" element={<SessionDetail />} />
        <Route path="/party" element={<Party />} />
        <Route path="/party/characters/:slug" element={<CharacterDetail />} />
        <Route path="/encounters" element={<Encounters />} />
        <Route path="/encounters/new" element={<EncounterBuilder />} />
        <Route path="/encounters/:slug" element={<EncounterDetail />} />
        <Route path="/encounters/:slug/edit" element={<EncounterBuilder />} />
        <Route path="/encounters/:slug/combat" element={<EncounterRunner />} />
        
        {/* Visualization routes */}
        <Route path="/timeline" element={<Timeline />} />
        <Route path="/relationships" element={<Relationships />} />
        
        {/* Reference routes */}
        <Route path="/reference" element={<Reference />} />
        <Route path="/reference/:type" element={<Reference />} />
        <Route path="/reference/:type/*" element={<ReferenceDetail />} />

        {/* Docs routes */}
        <Route path="/docs" element={<Docs />} />
        <Route path="/docs/:slug" element={<DocDetail />} />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}

export default App;
