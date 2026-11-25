import { useCallback, useEffect, useState } from 'react';
import { Alert, Pressable, ScrollView, Switch, Text, View } from 'react-native';

import { api } from '../api';
import { Button, Card, colors, Field, styles } from '../ui';

const RELATIONS = ['family', 'friend', 'caregiver', 'doctor', 'hospital', 'neighbor', 'other'];
const EMPTY = { name: '', phone: '+', relation: 'family', priority: '1', notify_sms: true, notify_call: true };

export default function ContactsScreen() {
  const [contacts, setContacts] = useState([]);
  const [form, setForm] = useState(null); // null = list view, otherwise the contact being edited
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setContacts(await api.contacts());
    } catch (e) {
      Alert.alert('Could not load contacts', e.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const save = async () => {
    setError(null);
    const body = {
      name: form.name.trim(),
      phone: form.phone.trim(),
      relation: form.relation,
      priority: parseInt(form.priority, 10) || 1,
      notify_sms: form.notify_sms,
      notify_call: form.notify_call,
    };
    try {
      if (form.id) await api.updateContact(form.id, body);
      else await api.addContact(body);
      setForm(null);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const remove = (c) =>
    Alert.alert(`Remove ${c.name}?`, undefined, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Remove',
        style: 'destructive',
        onPress: async () => {
          await api.deleteContact(c.id);
          load();
        },
      },
    ]);

  if (form) {
    const set = (k) => (v) => setForm({ ...form, [k]: v });
    return (
      <ScrollView contentContainerStyle={styles.screen} keyboardShouldPersistTaps="handled">
        <Text style={styles.h1}>{form.id ? 'Edit contact' : 'Add contact'}</Text>
        <Field label="Name" value={form.name} onChangeText={set('name')} placeholder="e.g. Daughter, City Hospital" />
        <Field label="Phone (with country code)" value={form.phone} onChangeText={set('phone')} keyboardType="phone-pad" />
        <Text style={styles.label}>Who is this?</Text>
        <View style={[styles.row, { flexWrap: 'wrap', marginBottom: 14 }]}>
          {RELATIONS.map((r) => (
            <Pressable
              key={r}
              onPress={() => set('relation')(r)}
              style={{
                paddingVertical: 8,
                paddingHorizontal: 12,
                borderRadius: 20,
                borderWidth: 1,
                borderColor: form.relation === r ? colors.primary : colors.border,
                backgroundColor: form.relation === r ? colors.primary : colors.card,
              }}
            >
              <Text style={{ fontSize: 15, color: form.relation === r ? '#fff' : colors.text }}>{r}</Text>
            </Pressable>
          ))}
        </View>
        <Field label="Call order (1 is called first)" value={String(form.priority)} onChangeText={set('priority')} keyboardType="number-pad" />
        <View style={[styles.row, { justifyContent: 'space-between', marginBottom: 10 }]}>
          <Text style={styles.body}>Send a text message</Text>
          <Switch value={form.notify_sms} onValueChange={set('notify_sms')} />
        </View>
        <View style={[styles.row, { justifyContent: 'space-between', marginBottom: 10 }]}>
          <Text style={styles.body}>Phone them</Text>
          <Switch value={form.notify_call} onValueChange={set('notify_call')} />
        </View>
        {form.relation === 'hospital' && (
          <Text style={[styles.muted, { marginBottom: 10 }]}>
            Use a clinic or care-team number that has agreed to receive automated alerts, not an emergency number like 911.
          </Text>
        )}
        {error && <Text style={styles.error}>{error}</Text>}
        <Button title="Save" onPress={save} />
        <Button title="Cancel" outline onPress={() => setForm(null)} />
      </ScrollView>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.h1}>Contacts</Text>
      <Text style={[styles.body, { marginBottom: 14 }]}>
        If you need help or miss your calls, everyone below gets a text, then we phone them in order until one presses 1
        to confirm they will check on you.
      </Text>
      {contacts.length === 0 && (
        <Card>
          <Text style={[styles.body, { color: colors.help }]}>No contacts yet. Add at least one so someone is alerted.</Text>
        </Card>
      )}
      {contacts.map((c) => (
        <Card key={c.id}>
          <Text style={styles.h2}>
            {c.priority}. {c.name}
          </Text>
          <Text style={styles.muted}>
            {c.relation} · {c.phone} · {[c.notify_sms && 'text', c.notify_call && 'call'].filter(Boolean).join(' + ') || 'no alerts'}
          </Text>
          <View style={[styles.row, { marginTop: 8 }]}>
            <View style={{ flex: 1 }}>
              <Button title="Edit" outline onPress={() => setForm({ ...c, priority: String(c.priority) })} />
            </View>
            <View style={{ flex: 1 }}>
              <Button title="Remove" outline color={colors.danger} onPress={() => remove(c)} />
            </View>
          </View>
        </Card>
      ))}
      <Button title="Add contact" onPress={() => setForm({ ...EMPTY, priority: String(contacts.length + 1) })} />
    </ScrollView>
  );
}
