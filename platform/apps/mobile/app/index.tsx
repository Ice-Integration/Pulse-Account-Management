import { useState } from 'react';
import { SafeAreaView, ScrollView, Text, TextInput, TouchableOpacity, View } from 'react-native';

const GATEWAY = process.env.EXPO_PUBLIC_GATEWAY_URL ?? 'http://localhost:4000/graphql';

export default function Home() {
  const [accountId, setAccountId] = useState('');
  const [account, setAccount] = useState<any>(null);
  const [error, setError] = useState('');

  async function load() {
    try {
      setError('');
      const response = await fetch(GATEWAY, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ query: `query($id:ID!){account(id:$id){account_number full_name phone billing_address status plans{name monthly_price} devices{model line_number financed payoff_amount}}}`, variables: { id: accountId } }) });
      const result = await response.json();
      if (result.errors) throw new Error(result.errors[0].message);
      setAccount(result.data.account);
    } catch (e: any) { setError(e.message); }
  }

  return <SafeAreaView style={{flex:1,backgroundColor:'#f5f7fb'}}><ScrollView contentContainerStyle={{padding:20,gap:14}}>
    <Text style={{fontSize:14,fontWeight:'800',color:'#4156d8'}}>PULSE</Text>
    <Text style={{fontSize:32,fontWeight:'800',color:'#172033'}}>My Account</Text>
    <TextInput value={accountId} onChangeText={setAccountId} placeholder="Account UUID" style={{backgroundColor:'white',padding:14,borderRadius:12,borderWidth:1,borderColor:'#d9dfeb'}} />
    <TouchableOpacity onPress={load} style={{backgroundColor:'#172033',padding:15,borderRadius:12}}><Text style={{color:'white',fontWeight:'700',textAlign:'center'}}>Open account</Text></TouchableOpacity>
    {!!error && <Text style={{color:'#b42318'}}>{error}</Text>}
    {account && <>
      <View style={{backgroundColor:'white',padding:20,borderRadius:18}}><Text style={{color:'#69758c'}}>Customer</Text><Text style={{fontSize:24,fontWeight:'800'}}>{account.full_name}</Text><Text>{account.account_number}</Text><Text style={{marginTop:10,color:'#207347',fontWeight:'700'}}>{account.status}</Text></View>
      <View style={{backgroundColor:'white',padding:20,borderRadius:18}}><Text style={{fontSize:18,fontWeight:'800',marginBottom:10}}>Plans</Text>{account.plans.map((p:any)=><Text key={p.name} style={{paddingVertical:8}}>{p.name} · ${p.monthly_price}/mo</Text>)}</View>
      <View style={{backgroundColor:'white',padding:20,borderRadius:18}}><Text style={{fontSize:18,fontWeight:'800',marginBottom:10}}>Devices</Text>{account.devices.map((d:any)=><Text key={d.line_number} style={{paddingVertical:8}}>{d.model} · {d.line_number}</Text>)}</View>
    </>}
  </ScrollView></SafeAreaView>;
}
