import { useState, useEffect, createContext, useContext } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Wallet, 
  CreditCard, 
  QrCode, 
  User, 
  Camera, 
  Upload, 
  CheckCircle, 
  XCircle, 
  Clock,
  ArrowUpRight,
  ArrowDownLeft,
  Smartphone,
  Building2
} from 'lucide-react'
import './App.css'

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api'

// Auth Context
const AuthContext = createContext()

function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      // For demo users, bypass API call and directly set user data if token indicates demo
      if (token.startsWith('demo_token_')) {
        const demoUser = {
          user_id: 'demo_user',
          email: 'demo@solwallet.com',
          full_name: 'Demo User',
          kyc_status: 'APPROVED',
          passport_number: 'DEMO123456',
          phone_number: '+1234567890'
        }
        setUser(demoUser)
        setLoading(false)
      } else {
        fetchUserProfile()
      }
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUserProfile = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        logout()
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = (token, userData) => {
    localStorage.setItem('token', token)
    setToken(token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading, fetchUserProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

// Login Component
function LoginScreen() {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    passport_number: '',
    full_name: '',
    phone_number: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useContext(AuthContext)

  const handleDemoLogin = () => {
    setLoading(true)
    setError('')
    
    // Simulate demo login with mock data
    setTimeout(() => {
      const demoToken = 'demo_token_' + Date.now()
      const demoUser = {
        user_id: 'demo_user',
        email: 'demo@solwallet.com',
        full_name: 'Demo User',
        kyc_status: 'APPROVED',
        passport_number: 'DEMO123456',
        phone_number: '+1234567890'
      }
      
      login(demoToken, demoUser)
      setLoading(false)
    }, 1000)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register'
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (response.ok) {
        login(data.access_token, {
          user_id: data.user_id,
          kyc_status: data.kyc_status
        })
      } else {
        setError(data.error || 'Authentication failed')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-blue-600">Sol Wallet</CardTitle>
          <CardDescription>Digital wallet for tourists in Indonesia</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={isLogin ? 'login' : 'register'} onValueChange={(value) => setIsLogin(value === 'login')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="register">Register</TabsTrigger>
            </TabsList>
            
            <TabsContent value="login">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
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
                
                {/* Demo Mode Button */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">
                      Or try demo
                    </span>
                  </div>
                </div>
                
                <Button 
                  type="button" 
                  variant="outline" 
                  className="w-full bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 hover:from-green-100 hover:to-emerald-100 text-green-700"
                  onClick={handleDemoLogin}
                  disabled={loading}
                >
                  <User className="w-4 h-4 mr-2" />
                  Demo Mode - Try Sol Wallet
                </Button>
              </form>
            </TabsContent>
            
            <TabsContent value="register">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="passport_number">Passport Number</Label>
                  <Input
                    id="passport_number"
                    value={formData.passport_number}
                    onChange={(e) => setFormData({...formData, passport_number: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input
                    id="full_name"
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="phone_number">Phone Number</Label>
                  <Input
                    id="phone_number"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    required
                  />
                </div>
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Creating account...' : 'Create Account'}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

// KYC Verification Component
function KYCScreen() {
  const [step, setStep] = useState(1)
  const [passportImage, setPassportImage] = useState(null)
  const [selfieImage, setSelfieImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { token, fetchUserProfile } = useContext(AuthContext)

  const handleImageUpload = (file, type) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      if (type === 'passport') {
        setPassportImage(e.target.result)
      } else {
        setSelfieImage(e.target.result)
      }
    }
    reader.readAsDataURL(file)
  }

  const submitKYC = async () => {
    if (!passportImage || !selfieImage) {
      setError('Please upload both passport and selfie images')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/privy/kyc/initiate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          passport_image: passportImage,
          selfie_image: selfieImage
        })
      })

      const data = await response.json()

      if (response.ok) {
        setStep(3)
        setTimeout(() => {
          fetchUserProfile()
        }, 2000)
      } else {
        setError(data.error || 'KYC verification failed')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-green-600">KYC Verification</CardTitle>
          <CardDescription>Verify your identity to use Sol Wallet</CardDescription>
        </CardHeader>
        <CardContent>
          {step === 1 && (
            <div className="space-y-4">
              <div className="text-center">
                <Camera className="mx-auto h-16 w-16 text-green-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Upload Passport Photo</h3>
                <p className="text-sm text-gray-600 mb-4">Take a clear photo of your passport's main page</p>
              </div>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageUpload(e.target.files[0], 'passport')}
                  className="hidden"
                  id="passport-upload"
                />
                <label htmlFor="passport-upload" className="cursor-pointer">
                  <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">Click to upload passport photo</p>
                </label>
              </div>
              {passportImage && (
                <div className="text-center">
                  <img src={passportImage} alt="Passport" className="mx-auto h-32 w-auto rounded border" />
                  <Button onClick={() => setStep(2)} className="mt-4 w-full">
                    Next: Take Selfie
                  </Button>
                </div>
              )}
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="text-center">
                <User className="mx-auto h-16 w-16 text-green-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Take a Selfie</h3>
                <p className="text-sm text-gray-600 mb-4">Take a clear selfie for identity verification</p>
              </div>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageUpload(e.target.files[0], 'selfie')}
                  className="hidden"
                  id="selfie-upload"
                />
                <label htmlFor="selfie-upload" className="cursor-pointer">
                  <Camera className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">Click to take selfie</p>
                </label>
              </div>
              {selfieImage && (
                <div className="text-center">
                  <img src={selfieImage} alt="Selfie" className="mx-auto h-32 w-auto rounded border" />
                </div>
              )}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="flex space-x-2">
                <Button variant="outline" onClick={() => setStep(1)} className="flex-1">
                  Back
                </Button>
                <Button onClick={submitKYC} disabled={loading || !selfieImage} className="flex-1">
                  {loading ? 'Verifying...' : 'Submit KYC'}
                </Button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="text-center space-y-4">
              <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
              <h3 className="text-lg font-semibold">Verification Submitted</h3>
              <p className="text-sm text-gray-600">Your documents are being reviewed. This usually takes a few minutes.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// Main Wallet Dashboard
function WalletDashboard() {
  const [balance, setBalance] = useState(0)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const { user, token, logout } = useContext(AuthContext)

  useEffect(() => {
    // Set demo data for demo users
    if (user?.user_id === 'demo_user') {
      setBalance(2500000) // IDR 2,500,000 demo balance
      setTransactions([
        {
          id: 'demo_1',
          type: 'TOPUP',
          amount: 1000000,
          status: 'SUCCESS',
          created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          description: 'Top-up via Credit Card'
        },
        {
          id: 'demo_2',
          type: 'QRIS_PAYMENT',
          amount: -150000,
          status: 'SUCCESS',
          created_at: new Date(Date.now() - 43200000).toISOString(), // 12 hours ago
          description: 'Payment to Warung Makan Sari'
        },
        {
          id: 'demo_3',
          type: 'TOPUP',
          amount: 1500000,
          status: 'SUCCESS',
          created_at: new Date(Date.now() - 21600000).toISOString(), // 6 hours ago
          description: 'Top-up via Virtual Account'
        },
        {
          id: 'demo_4',
          type: 'QRIS_PAYMENT',
          amount: -75000,
          status: 'SUCCESS',
          created_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
          description: 'Payment to Starbucks Bali'
        }
      ])
      setLoading(false)
      return
    }
    
    fetchWalletData()
  }, [])

  const fetchWalletData = async () => {
    try {
      const [balanceRes, transactionsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/wallet/balance`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/wallet/transactions`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (balanceRes.ok) {
        const balanceData = await balanceRes.json()
        setBalance(balanceData.balance)
      }

      if (transactionsRes.ok) {
        const transactionsData = await transactionsRes.json()
        setTransactions(transactionsData.transactions || [])
      }
    } catch (error) {
      console.error('Failed to fetch wallet data:', error)
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

  const getTransactionIcon = (type) => {
    return type === 'TOPUP' ? <ArrowDownLeft className="h-4 w-4 text-green-500" /> : 
           type === 'QRIS_PAYMENT' ? <ArrowUpRight className="h-4 w-4 text-red-500" /> :
           <Wallet className="h-4 w-4 text-blue-500" />
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Clock className="mx-auto h-8 w-8 animate-spin text-blue-500 mb-2" />
          <p>Loading wallet...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold">Sol Wallet</h1>
            <p className="text-blue-100 text-sm">
              {user?.user_id === 'demo_user' ? 'Demo Mode - Try all features!' : 'Welcome back!'}
            </p>
            {user?.user_id === 'demo_user' && (
              <Badge variant="secondary" className="mt-1 bg-green-100 text-green-800 border-green-200">
                <User className="w-3 h-3 mr-1" />
                Demo Account
              </Badge>
            )}
          </div>
          <Button variant="ghost" size="sm" onClick={logout} className="text-white hover:bg-blue-700">
            <User className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      {/* Balance Card */}
      <div className="p-4">
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Total Balance</p>
              <p className="text-3xl font-bold text-blue-600">
                IDR {balance.toLocaleString('id-ID')}
              </p>
              <div className="flex space-x-2 mt-4">
                <Button className="flex-1" onClick={() => window.location.hash = '#topup'}>
                  <CreditCard className="h-4 w-4 mr-2" />
                  Top Up
                </Button>
                <Button variant="outline" className="flex-1" onClick={() => window.location.hash = '#qris'}>
                  <QrCode className="h-4 w-4 mr-2" />
                  Pay with QRIS
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            {transactions.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No transactions yet</p>
            ) : (
              <div className="space-y-3">
                {transactions.slice(0, 10).map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getTransactionIcon(transaction.type)}
                      <div>
                        <p className="font-medium">{transaction.description}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(transaction.created_at).toLocaleDateString('id-ID')}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-medium ${transaction.type === 'TOPUP' ? 'text-green-600' : 'text-red-600'}`}>
                        {transaction.type === 'TOPUP' ? '+' : '-'}IDR {transaction.amount.toLocaleString('id-ID')}
                      </p>
                      {getStatusBadge(transaction.status)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// Top Up Screen
function TopUpScreen({ user, fetchUserProfile }) {
  const [amount, setAmount] = useState('')
  const [paymentMethod, setPaymentMethod] = useState('BCA_VA')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const { token } = useContext(AuthContext)

  const handleTopUp = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      setError("Please enter a valid amount")
      return
    }

    setLoading(true)
    setError("")

    if (user?.user_id === "demo_user") {
      // Simulate successful top-up for demo user
      setTimeout(() => {
        setResult({ va_number: "DEMOVA123456", bank_code: "DEMO_BANK" })
        setLoading(false)
      }, 1000)
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/wallet/topup`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          payment_method: paymentMethod,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setResult(data)
      } else {
        setError(data.error || "Top-up failed")
      }
    } catch (error) {
      setError("Network error. Please try again.")
    } finally {
      setLoading(false)
    }
  }
  if (result) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="text-center text-green-600">Top-up Initiated</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
              <p className="text-lg font-semibold">IDR {parseFloat(amount).toLocaleString('id-ID')}</p>
            </div>
            
            {result.va_number && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="font-medium text-blue-800">Virtual Account Number:</p>
                <p className="text-xl font-mono text-blue-600">{result.va_number}</p>
                <p className="text-sm text-blue-600 mt-2">Bank: {result.bank_code}</p>
              </div>
            )}
            
            {result.payment_url && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="font-medium text-blue-800">Payment Link:</p>
                <a href={result.payment_url} target="_blank" rel="noopener noreferrer" 
                   className="text-blue-600 underline break-all">
                  Complete Payment
                </a>
              </div>
            )}
            
            <Button onClick={() => window.location.hash = '#dashboard'} className="w-full">
              Back to Wallet
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Top Up Wallet</CardTitle>
          <CardDescription>Add money to your Sol Wallet</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="amount">Amount (IDR)</Label>
            <Input
              id="amount"
              type="number"
              placeholder="Enter amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </div>
          
          <div>
            <Label>Payment Method</Label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {[
                { value: 'BCA_VA', label: 'BCA VA', icon: Building2 },
                { value: 'BNI_VA', label: 'BNI VA', icon: Building2 },
                { value: 'CREDIT_CARD', label: 'Credit Card', icon: CreditCard },
                { value: 'OVO', label: 'OVO', icon: Smartphone },
                { value: 'PAYPAL', label: 'PayPal', icon: CreditCard } // Added PayPal
              ].map((method) => (
                <Button
                  key={method.value}
                  variant={paymentMethod === method.value ? 'default' : 'outline'}
                  onClick={() => setPaymentMethod(method.value)}
                  className="h-auto p-3"
                >
                  <div className="text-center">
                    <method.icon className="h-6 w-6 mx-auto mb-1" />
                    <p className="text-xs">{method.label}</p>
                  </div>
                </Button>
              ))}
            </div>
          </div>
          
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => window.location.hash = '#dashboard'} className="flex-1">
              Cancel
            </Button>
            <Button onClick={handleTopUp} disabled={loading} className="flex-1">
              {loading ? 'Processing...' : 'Top Up'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// QRIS Payment Screen
function QRISScreen({ user, fetchUserProfile }) {
  const [qrisCode, setQrisCode] = useState('')
  const [amount, setAmount] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const { token } = useContext(AuthContext)

  const handlePayment = async () => {
    if (!qrisCode || !amount || parseFloat(amount) <= 0) {
      setError("Please enter QRIS code and valid amount")
      return
    }

    setLoading(true)
    setError("")
    if (user?.user_id === "demo_user") {
      // Simulate successful QRIS payment for demo user
      setTimeout(() => {
        setResult({ remaining_balance: 2000000 }) // Simulate remaining balance after payment
        setLoading(false)
      }, 1000)
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/wallet/qris-pay`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          merchant_qris_code: qrisCode,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setResult(data)
      } else {
        setError(data.error || "Payment failed")
      }
    } catch (error) {
      setError("Network error. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const emulateQRScan = () => {
    setQrisCode('DEMO_QRIS_MERCHANT_XYZ')
  }

  if (result) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="text-center text-green-600">Payment Successful</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
              <p className="text-lg font-semibold">IDR {parseFloat(amount).toLocaleString('id-ID')}</p>
              <p className="text-sm text-gray-600">Payment completed successfully</p>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="font-medium text-green-800">Remaining Balance:</p>
              <p className="text-xl font-semibold text-green-600">
                IDR {result.remaining_balance.toLocaleString('id-ID')}
              </p>
            </div>
            
            <Button onClick={() => window.location.hash = '#dashboard'} className="w-full">
              Back to Wallet
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>QRIS Payment</CardTitle>
          <CardDescription>Scan or enter QRIS code to pay</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="qris">QRIS Code</Label>
            <Input
              id="qris"
              placeholder="Enter or scan QRIS code"
              value={qrisCode}
              onChange={(e) => setQrisCode(e.target.value)}
            />
          </div>
          
          <Button onClick={emulateQRScan} className="w-full" variant="outline">
            <QrCode className="h-4 w-4 mr-2" /> Emulate QR Scan
          </Button>
          
          <div>
            <Label htmlFor="amount">Amount (IDR)</Label>
            <Input
              id="amount"
              type="number"
              placeholder="Enter amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </div>
          
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => window.location.hash = '#dashboard'} className="flex-1">
              Cancel
            </Button>
            <Button onClick={handlePayment} disabled={loading} className="flex-1">
              {loading ? 'Processing...' : 'Pay Now'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Main App Component
function App() {
  const [currentScreen, setCurrentScreen] = useState('dashboard')

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1) || 'dashboard'
      setCurrentScreen(hash)
    }

    window.addEventListener('hashchange', handleHashChange)
    handleHashChange()

    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  return (
    <AuthProvider>
      <AuthContext.Consumer>
        {({ user, loading, fetchUserProfile }) => {
          if (loading) {
            return (
              <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                  <Clock className="mx-auto h-8 w-8 animate-spin text-blue-500 mb-2" />
                  <p>Loading...</p>
                </div>
              </div>
            )
          }

          if (!user) {
            return <LoginScreen />
          }

          if (user.kyc_status !== 'APPROVED') {
            return <KYCScreen />
          }

          switch (currentScreen) {
            case 'topup':
              return <TopUpScreen user={user} fetchUserProfile={fetchUserProfile} />
            case 'qris':
              return <QRISScreen user={user} fetchUserProfile={fetchUserProfile} />
            default:
              return <WalletDashboard />
          }
        }}
      </AuthContext.Consumer>
    </AuthProvider>
  )
}

export default App

