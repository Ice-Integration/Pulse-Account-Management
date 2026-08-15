import { createApp, ref } from 'vue';

const App = {
  setup() {
    const accountId = ref('');
    const account = ref<any>(null);
    const error = ref('');
    const gateway = import.meta.env.VITE_GATEWAY_URL ?? 'http://localhost:4000/graphql';

    async function load() {
      try {
        error.value = '';
        const response = await fetch(gateway, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ query: `query($id:ID!){account(id:$id){account_number full_name status phone billing_address plans{name monthly_price} devices{model line_number financed payoff_amount}}}`, variables: { id: accountId.value } }),
        });
        const result = await response.json();
        if (result.errors) throw new Error(result.errors[0].message);
        account.value = result.data.account;
      } catch (e: any) { error.value = e.message; }
    }

    return { accountId, account, error, load };
  },
  template: `
    <main style="font-family:Inter,system-ui;max-width:1100px;margin:auto;padding:28px;color:#172033">
      <p style="font-weight:800;color:#4156d8;letter-spacing:.12em">PULSE ADMIN</p>
      <h1>Operations Console</h1>
      <div style="display:flex;gap:10px"><input v-model="accountId" placeholder="Account UUID" style="flex:1;padding:12px;border:1px solid #d9dfeb;border-radius:10px"/><button @click="load" style="padding:12px 18px;border:0;border-radius:10px;background:#172033;color:white;font-weight:700">Search</button></div>
      <p v-if="error" style="color:#b42318">{{ error }}</p>
      <section v-if="account" style="margin-top:20px;padding:22px;border:1px solid #e5e9f1;border-radius:16px">
        <h2>{{ account.full_name }}</h2><p>{{ account.account_number }} · {{ account.status }}</p>
        <h3>Plans</h3><p v-for="p in account.plans" :key="p.name">{{ p.name }} · ${{ p.monthly_price }}/mo</p>
        <h3>Devices</h3><p v-for="d in account.devices" :key="d.line_number">{{ d.model }} · {{ d.line_number }}</p>
      </section>
    </main>`
};

createApp(App).mount('#app');
