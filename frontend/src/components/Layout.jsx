import { useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/customers': 'Customers',
  '/segments': 'Segments',
  '/segments/create': 'Create Segment',
  '/campaigns': 'Campaigns',
  '/campaigns/create': 'Create Campaign',
}

export default function Layout({ children }) {
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] ||
    (location.pathname.startsWith('/campaigns/') ? 'Campaign Detail' : 'XenoCRM')

  return (
    <div className="min-h-screen bg-white">
      <Sidebar />
      <div className="ml-60">
        <header className="sticky top-0 z-30 flex h-16 items-center border-b border-gray-200 bg-white px-8">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
        </header>
        <main className="p-8">{children}</main>
      </div>
    </div>
  )
}
