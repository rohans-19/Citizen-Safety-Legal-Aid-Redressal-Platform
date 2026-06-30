import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './app/App.jsx'
import DashboardApp from './dashboard/App.jsx'
import './index.css'

const Root = window.location.pathname.startsWith('/dashboard') ? DashboardApp : App
document.title = window.location.pathname.startsWith('/dashboard')
  ? 'CIVIC-SHIELD Dashboard'
  : 'Rasoi - Recipe App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
)
