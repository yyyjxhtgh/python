import { useCallback, useEffect, useState } from 'react';
import { Alert, RefreshControl, ScrollView, Text, View } from 'react-native';

import { api, formatWhen } from '../api';
import { Button, Card, colors, ESCALATION, STATUS, styles } from '../ui';

export default function HomeScreen({ user, onUserChange }) {
  const [history, setHistory] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    setRefreshing(true);
    try {
      const [me, checkins] = await Promise.all([api.me(), api.checkins(20)]);
      onUserChange(me);
      setHistory(checkins);
    } catch (e) {
      Alert.alert('Could not refresh', e.message);
    } finally {
      setRefreshing(false);
    }
  }, [onUserChange]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const send = async (status) => {
    setBusy(true);
    try {
      await api.checkIn(status);
      await refresh();
      if (status === 'needs_help') {
        Alert.alert('Help is on the way', 'We are contacting your contacts now. In a life-threatening emergency, call your local emergency number.');
      }
    } catch (e) {
      Alert.alert('Something went wrong', e.message);
    } finally {
      setBusy(false);
    }
  };

  const confirmHelp = () =>
    Alert.alert('Ask for help?', 'Your contacts will get a text and a phone call.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Yes, get help', style: 'destructive', onPress: () => send('needs_help') },
    ]);

  const status = STATUS[user.last_status] || STATUS.unknown;

  return (
    <ScrollView contentContainerStyle={styles.screen} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} />}>
      <Text style={styles.h1}>Hello, {user.name}</Text>

      <Card>
        <Text style={styles.muted}>Current status</Text>
        <Text style={{ fontSize: 30, fontWeight: '800', color: status.color }}>{status.label}</Text>
        {user.last_status_at && <Text style={styles.muted}>Updated {formatWhen(user.last_status_at)}</Text>}
        <Text style={[styles.body, { marginTop: 10 }]}>
          {user.active ? `Next call: ${formatWhen(user.next_checkin_at)}` : 'Calls are paused (see Schedule).'}
        </Text>
      </Card>

      <Button big title="I'm OK" color={colors.ok} onPress={() => send('ok')} disabled={busy} />
      <Button big title="I need help" color={colors.help} onPress={confirmHelp} disabled={busy} />

      <Text style={[styles.h2, { marginTop: 22 }]}>Recent check-ins</Text>
      {history.length === 0 && <Text style={styles.muted}>Nothing yet.</Text>}
      {history.map((c) => {
        const st = STATUS[c.status] || STATUS.unknown;
        return (
          <Card key={c.id} style={{ paddingVertical: 12 }}>
            <View style={[styles.row, { justifyContent: 'space-between' }]}>
              <Text style={[styles.body, { fontWeight: '700', color: st.color }]}>{st.label}</Text>
              <Text style={styles.muted}>{formatWhen(c.completed_at || c.scheduled_for)}</Text>
            </View>
            <Text style={styles.muted}>
              {c.source === 'app' ? 'From the app' : `Phone call · ${c.attempts} attempt${c.attempts === 1 ? '' : 's'}`}
              {c.note ? ` · ${c.note}` : ''}
            </Text>
            {c.escalation_status && (
              <Text style={[styles.muted, { color: colors.help, marginTop: 4 }]}>
                {ESCALATION[c.escalation_status] || c.escalation_status}
                {c.alerts.length > 0 && ': ' + c.alerts.map((a) => `${a.contact_name} (${a.status.replace('_', ' ')})`).join(', ')}
              </Text>
            )}
          </Card>
        );
      })}
    </ScrollView>
  );
}
