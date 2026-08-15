import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const GATEWAY = import.meta.env.VITE_GATEWAY_URL ?? 'http://localhost:4000/graphql';
const IDENTITY = import.meta.env.VITE_IDENTITY_URL ?? 'http://localhost:4001';

function storedToken() {
  return localStorage.getItem('pulse_access_token') ?? '';
}

async function gql(query: string, variables: Record<string, unknown> = {}) {
  const token = storedToken();
  const response = await fetch(GATEWAY, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      ...(token ? { authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ query, variables }),
  });
  const result = await response.json();
  if (result.errors) throw new Error(result.errors[0].message);
  return result.data;
}

function App() {
  const [token, setToken] = useState(storedToken());
  const [email, setEmail] = useState('customer@pulse.local');
  const [password, setPassword] = useState('PulsePass123!');
  const [accountId, setAccountId] = useState('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa');
  const [account, setAccount] = useState<any>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function login() {
    try {
      setBusy(true);
      setError('');
      const response = await fetch(`${IDENTITY}/auth/login`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error ?? 'login_failed');
      localStorage.setItem('pulse_access_token', payload.accessToken);
      setToken(payload.accessToken);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    localStorage.removeItem('pulse_access_token');
    setToken('');
    setAccount(null);
  }

  async function load() {
    try {
      setBusy(true);
      setError('');
      const data = await gql(`query($id:ID!){account(id:$id){id account_number full_name phone billing_address status devices{id line_number model financed payoff_amount} plans{id code name monthly_price description}}}`, { id: accountId });
      setAccount(data.account);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return <main>
    <header>
      <div><p className="eyebrow">Pulse</p><h1>Account Management</h1></div>
      <div className="headerActions"><span className="badge">Production Platform</span>{token && <button className="ghost" onClick={logout}>Sign out</button>}</div>
    </header>

    {!token ? <section className="card auth">
      <div><p className="eyebrow">Secure access</p><h2>Customer sign in</h2><p>Authenticate through the Identity service before accessing customer data.</p></div>
      <div className="authFields">
        <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email"/>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password"/>
        <button onClick={login} disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
      </div>
    </section> : <>
      <section className="search">
        <input value={accountId} onChange={e => setAccountId(e.target.value)} placeholder="Enter account UUID"/>
        <button onClick={load} disabled={busy}>{busy ? 'Loading…' : 'Open account'}</button>
      </section>
      {account && <>
        <section className="card hero"><div><p>Customer</p><h2>{account.full_name}</h2><span>{account.account_number}</span></div><strong>{account.status}</strong></section>
        <div className="grid">
          <section className="card"><h3>Profile</h3><p>{account.phone || 'No phone'}</p><p>{account.billing_address || 'No billing address'}</p></section>
          <section className="card"><h3>Plans</h3>{account.plans.map((p:any)=><div className="row" key={p.id}><span>{p.name}</span><b>${p.monthly_price}/mo</b></div>)}</section>
          <section className="card"><h3>Devices</h3>{account.devices.map((d:any)=><div className="row" key={d.id}><span>{d.model}<small>{d.line_number}</small></span><b>{d.financed ? `$${d.payoff_amount} due` : 'Owned'}</b></div>)}</section>
        </div>
      </>}
    </>}
    {error && <p className="error">{error}</p>}
  </main>;
}

createRoot(document.getElementById('root')!).render(<App/>);
