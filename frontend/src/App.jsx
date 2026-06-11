import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Customers from './pages/Customers'
import Segments from './pages/Segments'
import CreateSegment from './pages/CreateSegment'
import Campaigns from './pages/Campaigns'
import CreateCampaign from './pages/CreateCampaign'
import CampaignDetail from './pages/CampaignDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/segments" element={<Segments />} />
          <Route path="/segments/create" element={<CreateSegment />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="/campaigns/create" element={<CreateCampaign />} />
          <Route path="/campaigns/:id" element={<CampaignDetail />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
