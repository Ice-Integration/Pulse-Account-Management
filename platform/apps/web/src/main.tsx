import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const GATEWAY = import.meta.env.VITE_GATEWAY_URL ?? 'http://localhost:4000/graphql';

async function gql(query: string, variables: Record<string, unknown> = {}) {
  const response = await fetch(GATEWAY, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  });
  const result = await response.json();
  if (result.errors) throw new Error(result.errors[0].message);
  return result.data;
}

function App() {
  const [accountId, setAccountId] = useState('');
  const [account, setAccount] = useState<any>(null);
  const [error, setError] = useState('');

  async function load() {
    try {
      setError('');
      const data = await gql(`query($id:ID!){account(id:$id){id account_number full_name phone billing_address status devices{id line_number model financed payoff_amount} plans{id code name monthly_price description}}}`, { id: accountId });
      setAccount(data.account);
    } catch (e: any) { setError(e.message); }
  }

  return <main>
    <header><div><p className="eyebrow">Pulse</p><h1>Account Management</h1></div><span className="badge">Production Platform</span></header>
    <section className="search"><input value={accountId} onChange={e => setAccountId(e.target.value)} placeholder="Enter account UUID"/><button onClick={load}>Open account</button></section>
    {error && <p className="error">{error}</p>}
    {account && <>
      <section className="card hero"><div><p>Customer</p><h2>{account.full_name}</h2><span>{account.account_number}</span></div><strong>{account.status}</strong></section>
      <div className="grid">
        <section className="card"><h3>Profile</h3><p>{account.phone || 'No phone'}</p><p>{account.billing_address || 'No billing address'}</p></section>
        <section className="card"><h3>Plans</h3>{account.plans.map((p:any)=><div className="row" key={p.id}><span>{p.name}</span><b>${p.monthly_price}/mo</b></div>)}</section>
        <section className="card"><h3>Devices</h3>{account.devices.map((d:any)=><div className="row" key={d.id}><span>{d.model}<small>{d.line_number}</small></span><b>{d.financed ? `$${d.payoff_amount} due` : 'Owned'}</b></div>)}</section>
      </div>
    </>}
  </main>;
}

createRoot(document.getElementById('root')!).render(<App/>);
