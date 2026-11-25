import { useState } from 'react';
import { KeyboardAvoidingView, Platform, ScrollView, Text } from 'react-native';

import { api, deviceTimezone, saveToken } from '../api';
import { Button, Field, styles } from '../ui';
import { parseTimes } from './ScheduleScreen';

export default function RegisterScreen({ onRegistered }) {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('+');
  const [times, setTimes] = useState('09:00');
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setError(null);
    const checkin_times = parseTimes(times);
    if (!checkin_times) return setError('Times must look like 09:00 or 09:00, 20:00');
    setBusy(true);
    try {
      const res = await api.register({ name: name.trim(), phone: phone.trim(), timezone: deviceTimezone(), checkin_times });
      await saveToken(res.api_token);
      onRegistered(res.user);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.screen} keyboardShouldPersistTaps="handled">
        <Text style={styles.h1}>Daily Check-in</Text>
        <Text style={[styles.body, { marginBottom: 20 }]}>
          We will phone you at the times you choose. Press 1 if you are OK, or 2 if you need help. If you need help or
          don't answer, we contact your family or care team.
        </Text>
        <Field label="Your name" value={name} onChangeText={setName} placeholder="e.g. Mary Chen" />
        <Field
          label="Phone number to call (with country code)"
          value={phone}
          onChangeText={setPhone}
          keyboardType="phone-pad"
          placeholder="+14155550123"
        />
        <Field label="Call times (24-hour, comma separated)" value={times} onChangeText={setTimes} placeholder="09:00, 20:00" />
        <Text style={styles.muted}>Time zone: {deviceTimezone()}</Text>
        {error && <Text style={styles.error}>{error}</Text>}
        <Button title={busy ? 'Signing up…' : 'Sign up'} onPress={submit} disabled={busy || !name.trim()} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
