import { useState, useEffect, createContext, useContext } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { 
  Users, 
  CreditCard, 
  TrendingUp, 
  Shield, 
  LogOut,
  Eye,
  RefreshCw,
  DollarSign,
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import './App.css'

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api'

// Auth Context
const AuthContext = createContext()

function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('admin_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      // In a real implementation, verify admin token
      setAdmin({ username: 'admin', role: 'admin' })
    }
    setLoading(false)
  }, [token])

  const login = (token, adminData) => {
    localStorage.setItem('admin_token', token)
    setToken(token)
    setAdmin(adminData)
  }

  const logout = () => {
    localStorage.removeItem('admin_token')
    setToken(null)
    setAdmin(null)
  }

  return (
    <AuthContext.Provider value={{ admin, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

// Admin Login Component
function AdminLogin() {
  const [credentials, setCredentials] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useContext(AuthContext)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/admin/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      })

      const data = await response.json()

      if (response.ok) {
        login(data.access_token, {
          username: credentials.username,
          role: 'admin'
        })
      } else {
        setError(data.error || 'Login failed')
      }
    } catch (error) {
      // For demo purposes, allow admin/admin login
      if (credentials.username === 'admin' && credentials.password === 'admin') {
        login('mock-admin-token', {
          username: 'admin',
          role: 'admin'
        })
      } else {
        setError('Invalid credentials. Use admin/admin for demo.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-700 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-slate-800">Sol Admin Dashboard</CardTitle>
          <CardDescription>Administrator access only</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                value={credentials.username}
                onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                required
              />
            </div>
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
          <div className="mt-4 text-center text-sm text-gray-600">
            Demo credentials: admin / admin
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Dashboard Overview Component
function DashboardOverview() {
  const [stats, setStats] = useState({
    totalUsers: 1247,
    activeUsers: 892,
    pendingKYC: 45,
    approvedKYC: 847,
    totalTransactions: 5634,
    totalVolume: 2847392000,
    successfulTransactions: 5521,
    failedTransactions: 113
  })

  const [chartData] = useState([
    { name: 'Jan', transactions: 400, volume: 240000000 },
    { name: 'Feb', transactions: 300, volume: 180000000 },
    { name: 'Mar', transactions: 500, volume: 320000000 },
    { name: 'Apr', transactions: 780, volume: 450000000 },
    { name: 'May', transactions: 890, volume: 520000000 },
    { name: 'Jun', transactions: 1200, volume: 680000000 }
  ])

  const [kycData] = useState([
    { name: 'Approved', value: 847, color: '#10b981' },
    { name: 'Pending', value: 45, color: '#f59e0b' },
    { name: 'Rejected', value: 23, color: '#ef4444' }
  ])

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Users</p>
                <p className="text-2xl font-bold">{stats.totalUsers.toLocaleString()}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Users</p>
                <p className="text-2xl font-bold">{stats.activeUsers.toLocaleString()}</p>
              </div>
              <Activity className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Volume</p>
                <p className="text-2xl font-bold">IDR {(stats.totalVolume / 1000000).toFixed(1)}M</p>
              </div>
              <DollarSign className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold">{((stats.successfulTransactions / stats.totalTransactions) * 100).toFixed(1)}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-emerald-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Transaction Volume Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value, name) => [
                  name === 'volume' ? `IDR ${(value / 1000000).toFixed(1)}M` : value,
                  name === 'volume' ? 'Volume' : 'Transactions'
                ]} />
                <Line type="monotone" dataKey="transactions" stroke="#3b82f6" strokeWidth={2} />
                <Line type="monotone" dataKey="volume" stroke="#10b981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>KYC Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={kycData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {kycData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// Users Management Component
function UsersManagement() {
  const [users, setUsers] = useState([
    {
      id: 1,
      full_name: 'John Smith',
      email: 'john.smith@example.com',
      passport_number: 'A12345678',
      kyc_status: 'APPROVED',
      wallet_balance: 500000,
      created_at: '2024-01-15T10:30:00Z',
      last_login: '2024-01-20T14:22:00Z'
    },
    {
      id: 2,
      full_name: 'Sarah Johnson',
      email: 'sarah.j@example.com',
      passport_number: 'B98765432',
      kyc_status: 'PENDING',
      wallet_balance: 0,
      created_at: '2024-01-18T09:15:00Z',
      last_login: '2024-01-18T09:20:00Z'
    },
    {
      id: 3,
      full_name: 'Mike Chen',
      email: 'mike.chen@example.com',
      passport_number: 'C11223344',
      kyc_status: 'REJECTED',
      wallet_balance: 0,
      created_at: '2024-01-16T16:45:00Z',
      last_login: '2024-01-17T11:30:00Z'
    }
  ])

  const [loading, setLoading] = useState(false)
  const { token } = useContext(AuthContext)

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data.users || [])
      }
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  const getKYCBadge = (status) => {
    const variants = {
      APPROVED: { variant: 'default', icon: CheckCircle, color: 'text-green-600' },
      PENDING: { variant: 'secondary', icon: Clock, color: 'text-yellow-600' },
      REJECTED: { variant: 'destructive', icon: XCircle, color: 'text-red-600' }
    }
    
    const config = variants[status] || variants.PENDING
    const Icon = config.icon
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {status}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Users Management</h2>
        <Button onClick={fetchUsers} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
          <CardDescription>Manage user accounts and KYC status</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Passport</TableHead>
                <TableHead>KYC Status</TableHead>
                <TableHead>Balance</TableHead>
                <TableHead>Registered</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.full_name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.passport_number}</TableCell>
                  <TableCell>{getKYCBadge(user.kyc_status)}</TableCell>
                  <TableCell>IDR {user.wallet_balance.toLocaleString()}</TableCell>
                  <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

// Transactions Management Component
function TransactionsManagement() {
  const [transactions, setTransactions] = useState([
    {
      id: 'tx_001',
      user_name: 'John Smith',
      type: 'TOPUP',
      amount: 100000,
      status: 'SUCCESS',
      payment_method: 'BCA_VA',
      created_at: '2024-01-20T14:30:00Z',
      xendit_id: 'pr-12345'
    },
    {
      id: 'tx_002',
      user_name: 'Sarah Johnson',
      type: 'QRIS_PAYMENT',
      amount: 25000,
      status: 'SUCCESS',
      payment_method: 'QRIS',
      created_at: '2024-01-20T13:15:00Z',
      xendit_id: 'pr-12346'
    },
    {
      id: 'tx_003',
      user_name: 'Mike Chen',
      type: 'TOPUP',
      amount: 50000,
      status: 'FAILED',
      payment_method: 'CREDIT_CARD',
      created_at: '2024-01-20T12:00:00Z',
      xendit_id: 'pr-12347'
    }
  ])

  const [loading, setLoading] = useState(false)
  const { token } = useContext(AuthContext)

  const fetchTransactions = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/admin/transactions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTransactions(data.transactions || [])
      }
    } catch (error) {
      console.error('Failed to fetch transactions:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      SUCCESS: 'default',
      PENDING: 'secondary',
      FAILED: 'destructive'
    }
    return <Badge variant={variants[status] || 'secondary'}>{status}</Badge>
  }

  const getTypeIcon = (type) => {
    return type === 'TOPUP' ? 
      <div className="flex items-center text-green-600">
        <TrendingUp className="h-4 w-4 mr-1" />
        Top-up
      </div> :
      <div className="flex items-center text-blue-600">
        <CreditCard className="h-4 w-4 mr-1" />
        Payment
      </div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Transactions</h2>
        <Button onClick={fetchTransactions} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Transactions</CardTitle>
          <CardDescription>Monitor all payment transactions and top-ups</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Transaction ID</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell className="font-mono text-sm">{transaction.id}</TableCell>
                  <TableCell>{transaction.user_name}</TableCell>
                  <TableCell>{getTypeIcon(transaction.type)}</TableCell>
                  <TableCell className="font-medium">
                    IDR {transaction.amount.toLocaleString()}
                  </TableCell>
                  <TableCell>{transaction.payment_method}</TableCell>
                  <TableCell>{getStatusBadge(transaction.status)}</TableCell>
                  <TableCell>{new Date(transaction.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-1" />
                      Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

// Main Admin Dashboard Component
function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const { admin, logout } = useContext(AuthContext)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Sol Admin Dashboard</h1>
            <p className="text-gray-600">Welcome back, {admin?.username}</p>
          </div>
          <Button variant="outline" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="transactions">Transactions</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <DashboardOverview />
          </TabsContent>

          <TabsContent value="users">
            <UsersManagement />
          </TabsContent>

          <TabsContent value="transactions">
            <TransactionsManagement />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

// Main App Component
function App() {
  return (
    <AuthProvider>
      <AuthContext.Consumer>
        {({ admin, loading }) => {
          if (loading) {
            return (
              <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                  <RefreshCw className="mx-auto h-8 w-8 animate-spin text-blue-500 mb-2" />
                  <p>Loading...</p>
                </div>
              </div>
            )
          }

          if (!admin) {
            return <AdminLogin />
          }

          return <AdminDashboard />
        }}
      </AuthContext.Consumer>
    </AuthProvider>
  )
}

export default App

