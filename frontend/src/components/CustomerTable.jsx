import { formatCurrency, formatDate } from '../lib/utils'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'

function SkeletonRow() {
  return (
    <TableRow>
      {[...Array(6)].map((_, i) => (
        <TableCell key={i}>
          <div className="h-4 animate-pulse rounded bg-gray-200" />
        </TableCell>
      ))}
    </TableRow>
  )
}

export default function CustomerTable({ customers, loading }) {
  if (loading) {
    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>City</TableHead>
            <TableHead>Orders</TableHead>
            <TableHead>Total Spent</TableHead>
            <TableHead>Last Order</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[...Array(5)].map((_, i) => <SkeletonRow key={i} />)}
        </TableBody>
      </Table>
    )
  }

  if (!customers?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-gray-400">
        <p className="text-lg font-medium">No customers found</p>
        <p className="text-sm mt-1">Upload a CSV or run the seed script to get started</p>
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>City</TableHead>
          <TableHead>Orders</TableHead>
          <TableHead>Total Spent</TableHead>
          <TableHead>Last Order</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {customers.map((c) => (
          <TableRow key={c.id}>
            <TableCell className="font-medium text-gray-900">{c.name}</TableCell>
            <TableCell>{c.email}</TableCell>
            <TableCell>{c.city || '—'}</TableCell>
            <TableCell>{c.total_orders}</TableCell>
            <TableCell>{formatCurrency(c.total_spent)}</TableCell>
            <TableCell>{formatDate(c.last_order_date)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
