import { useCallback, useEffect, useState } from 'react';
import { Pressable, SafeAreaView, StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';

import { api, clearToken, getToken } from './src/api';
import { initBilling, signOutBilling } from './src/billing';
import { colors, Loading } from './src/ui';
import RegisterScreen from './src/screens/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';
import ContactsScreen from './src/screens/ContactsScreen';
import ScheduleScreen from './src/screens/ScheduleScreen';
import SubscriptionScreen from './src/screens/SubscriptionScreen';

const TABS = [
  { key: 'home', label: 'Today' },
  { key: 'contacts', label: 'Contacts' },
  { key: 'schedule', label: 'Schedule' },
  { key: 'plan', label: 'Plan' },
];

export default function App() {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [tab, setTab] = useState('home');

  const loadUser = useCallback(async () => {
    try {
      if (!(await getToken())) return setUser(null);
      setUser(await api.me());
    } catch (e) {
      if (e.status === 401) {
        await clearToken();
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // Link store purchases on this phone to the signed-in user.
  const billingId = user ? user.billing_id : null;
  useEffect(() => {
    if (billingId) initBilling(billingId);
  }, [billingId]);

  const signOut = async () => {
    await signOutBilling();
    await clearToken();
    setUser(null);
    setTab('home');
  };

  let content;
  if (loading) content = <Loading />;
  else if (!user) content = <RegisterScreen onRegistered={setUser} />;
  else if (tab === 'home') content = <HomeScreen user={user} onUserChange={setUser} onOpenPlan={() => setTab('plan')} />;
  else if (tab === 'contacts') content = <ContactsScreen />;
  else if (tab === 'plan') content = <SubscriptionScreen user={user} onUserChange={setUser} />;
  else content = <ScheduleScreen user={user} onUserChange={setUser} onSignOut={signOut} />;

  return (
    <SafeAreaView style={s.safe}>
      <StatusBar style="dark" />
      <View style={{ flex: 1 }}>{content}</View>
      {user && (
        <View style={s.tabBar}>
          {TABS.map((t) => (
            <Pressable key={t.key} onPress={() => setTab(t.key)} style={s.tab} accessibilityRole="tab">
              <Text style={[s.tabText, tab === t.key && s.tabActive]}>{t.label}</Text>
            </Pressable>
          ))}
        </View>
      )}
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  tabBar: { flexDirection: 'row', borderTopWidth: 1, borderColor: colors.border, backgroundColor: colors.card },
  tab: { flex: 1, paddingVertical: 16, alignItems: 'center' },
  tabText: { fontSize: 17, color: colors.muted, fontWeight: '600' },
  tabActive: { color: colors.primary },
});
