import { useState } from 'react';
import { Alert, ScrollView, Switch, Text, View } from 'react-native';

import { api, deviceTimezone } from '../api';
import { Button, Card, colors, Field, styles } from '../ui';

/** "9:00, 20:30" -> ["09:00", "20:30"], or null if anything is invalid. */
export function parseTimes(text) {
  const parts = text.split(/[,\s]+/).filter(Boolean);
  if (parts.length === 0) return null;
  const out = [];
  for (const p of parts) {
    const m = /^(\d{1,2}):(\d{2})$/.exec(p);
    if (!m || +m[1] > 23 || +m[2] > 59) return null;
    out.push(`${m[1].padStart(2, '0')}:${m[2]}`);
  }
  return out;
}

export default function ScheduleScreen({ user, onUserChange, onSignOut }) {
  const [times, setTimes] = useState(user.checkin_times.join(', '));
  const [attempts, setAttempts] = useState(String(user.max_attempts));
  const [retry, setRetry] = useState(String(user.retry_minutes));
  const [active, setActive] = useState(user.active);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);

  const save = async () => {
    setError(null);
    setSaved(false);
    const checkin_times = parseTimes(times);
    if (!checkin_times) return setError('Times must look like 09:00 or 09:00, 20:00');
    try {
      const me = await api.updateMe({
        checkin_times,
        max_attempts: parseInt(attempts, 10) || 3,
        retry_minutes: parseInt(retry, 10) || 10,
        active,
        timezone: deviceTimezone(),
      });
      onUserChange(me);
      setTimes(me.checkin_times.join(', '));
      setSaved(true);
    } catch (e) {
      setError(e.message);
    }
  };

  const deleteAccount = () =>
    Alert.alert('Delete account?', 'This removes your schedule, contacts and history.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          await api.deleteMe();
          onSignOut();
        },
      },
    ]);

  return (
    <ScrollView contentContainerStyle={styles.screen} keyboardShouldPersistTaps="handled">
      <Text style={styles.h1}>Schedule</Text>
      <Card>
        <View style={[styles.row, { justifyContent: 'space-between' }]}>
          <Text style={styles.body}>Check-in calls on</Text>
          <Switch value={active} onValueChange={setActive} />
        </View>
        <Text style={styles.muted}>Turn off while travelling or in hospital.</Text>
      </Card>
      <Field label="Call times (24-hour, comma separated)" value={times} onChangeText={setTimes} placeholder="09:00, 20:00" />
      <Field label="How many times to try calling" value={attempts} onChangeText={setAttempts} keyboardType="number-pad" />
      <Field label="Minutes between tries" value={retry} onChangeText={setRetry} keyboardType="number-pad" />
      <Text style={styles.muted}>Time zone: {deviceTimezone()} · Phone: {user.phone}</Text>
      {error && <Text style={styles.error}>{error}</Text>}
      {saved && <Text style={[styles.body, { color: colors.ok, marginTop: 8 }]}>Saved.</Text>}
      <Button title="Save" onPress={save} />
      <View style={{ height: 30 }} />
      <Button title="Sign out of this phone" outline onPress={onSignOut} />
      <Button title="Delete account" outline color={colors.danger} onPress={deleteAccount} />
    </ScrollView>
  );
}
