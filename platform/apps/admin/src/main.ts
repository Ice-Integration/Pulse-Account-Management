import { createApp, ref } from 'vue';

const App = {
  setup() {
    const accountId = ref('');
    const account = ref<any>(null);
    const error = ref('');
    const email = ref('');
    const password = ref('');
    const token = ref(localStorage.getItem('pulse_admin_access_token') ?? '');
    const gateway = import.meta.env.VITE_GATEWAY_URL ?? 'http://localhost:4000/graphql';
    const identity = import.meta.env.VITE_IDENTITY_URL ?? 'http://localhost:4001';

    async function login() {
      try {
        error.value = '';
        const response = await fetch(`${identity}/auth/login`, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ email: email.value, password: password.value }),
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error ?? 'login_failed');
        token.value = result.accessToken;
        localStorage.setItem('pulse_admin_access_token', result.accessToken);
      } catch (e: any) {
        error.value = e.message;
      }
    }

    function logout() {
      token.value = '';
      account.value = null;
      localStorage.removeItem('pulse_admin_access_token');
    }

    async function load() {
      try {
        error.value = '';
        const response = await fetch(gateway, {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
            authorization: `Bearer ${token.value}`,
          },
          body: JSON.stringify({
            query: `query($id:ID!){account(id:$id){account_number full_name status phone billing_address plans{name monthly_price} devices{model line_number financed payoff_amount}}}`,
            variables: { id: accountId.value },
          }),
        });
        const result = await response.json();
        if (result.errors) throw new Error(result.errors[0].message);
        account.value = result.data.account;
      } catch (e: any) {
        error.value = e.message;
      }
    }

    return { accountId, account, error, email, password, token, login, logout, load };
  },
  template: `
    <main style="font-family:Inter,system-ui;max-width:1100px;margin:auto;padding:28px;color:#172033">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:16px">
        <div><p style="font-weight:800;color:#4156d8;letter-spacing:.12em">PULSE ADMIN</p><h1>Operations Console</h1></div>
        <button v-if="token" @click="logout" style="padding:10px 14px;border:1px solid #d9dfeb;border-radius:10px;background:white;font-weight:700">Sign out</button>
      </div>

      <section v-if="!token" style="padding:22px;border:1px solid #e5e9f1;border-radius:16px;background:white">
        <h2>Support sign in</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr auto;gap:10px">
          <input v-model="email" placeholder="Email" style="padding:12px;border:1px solid #d9dfeb;border-radius:10px"/>
          <input v-model="password" type="password" placeholder="Password" style="padding:12px;border:1px solid #d9dfeb;border-radius:10px"/>
          <button @click="login" :disabled="!email || !password" style="padding:12px 18px;border:0;border-radius:10px;background:#172033;color:white;font-weight:700">Sign in</button>
        </div>
      </section>

      <template v-else>
        <div style="display:flex;gap:10px"><input v-model="accountId" placeholder="Account UUID" style="flex:1;padding:12px;border:1px solid #d9dfeb;border-radius:10px"/><button @click="load" :disabled="!accountId" style="padding:12px 18px;border:0;border-radius:10px;background:#172033;color:white;font-weight:700">Search</button></div>
        <section v-if="account" style="margin-top:20px;padding:22px;border:1px solid #e5e9f1;border-radius:16px;background:white">
          <h2>{{ account.full_name }}</h2><p>{{ account.account_number }} · {{ account.status }}</p>
          <h3>Plans</h3><p v-for="p in account.plans" :key="p.name">{{ p.name }} · {{ p.monthly_price }} USD/mo</p>
          <h3>Devices</h3><p v-for="d in account.devices" :key="d.line_number">{{ d.model }} · {{ d.line_number }}</p>
        </section>
      </template>
      <p v-if="error" style="color:#b42318">{{ error }}</p>
    </main>`
};

createApp(App).mount('#app');
