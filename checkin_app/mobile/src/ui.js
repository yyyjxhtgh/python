import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

export const colors = {
  bg: '#f6f7f9',
  card: '#ffffff',
  text: '#1d2430',
  muted: '#5b6472',
  border: '#d9dde3',
  primary: '#2563eb',
  ok: '#15803d',
  help: '#c2410c',
  danger: '#b91c1c',
};

export const STATUS = {
  ok: { label: 'OK', color: colors.ok },
  needs_help: { label: 'Needs help', color: colors.help },
  missed: { label: 'Missed', color: colors.danger },
  pending: { label: 'Waiting to call', color: colors.muted },
  calling: { label: 'Calling now', color: colors.primary },
  unknown: { label: 'No check-in yet', color: colors.muted },
};

export const ESCALATION = {
  in_progress: 'Contacting your contacts',
  acknowledged: 'A contact is handling it',
  exhausted: 'No contact confirmed',
  cancelled: 'Contacts told you are OK',
  no_contacts: 'No contacts to alert',
};

export function Button({ title, onPress, color = colors.primary, big, disabled, outline }) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      accessibilityRole="button"
      style={({ pressed }) => [
        styles.button,
        big && styles.bigButton,
        outline ? { borderColor: color, borderWidth: 2, backgroundColor: 'transparent' } : { backgroundColor: color },
        (pressed || disabled) && { opacity: 0.6 },
      ]}
    >
      <Text style={[styles.buttonText, big && styles.bigButtonText, outline && { color }]}>{title}</Text>
    </Pressable>
  );
}

export function Field({ label, ...props }) {
  return (
    <View style={{ marginBottom: 14 }}>
      <Text style={styles.label}>{label}</Text>
      <TextInput style={styles.input} placeholderTextColor="#98a0ab" {...props} />
    </View>
  );
}

export function Card({ children, style }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Loading() {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );
}

export const styles = StyleSheet.create({
  screen: { padding: 16, paddingBottom: 40 },
  h1: { fontSize: 28, fontWeight: '700', color: colors.text, marginBottom: 8 },
  h2: { fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 8 },
  body: { fontSize: 17, color: colors.text, lineHeight: 24 },
  muted: { fontSize: 15, color: colors.muted },
  label: { fontSize: 16, fontWeight: '600', color: colors.text, marginBottom: 6 },
  input: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 18,
    color: colors.text,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: 14,
    padding: 16,
    marginBottom: 14,
    borderColor: colors.border,
    borderWidth: 1,
  },
  button: { borderRadius: 12, paddingVertical: 14, paddingHorizontal: 18, alignItems: 'center', marginVertical: 6 },
  bigButton: { paddingVertical: 26, borderRadius: 18 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  bigButtonText: { fontSize: 26 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  error: { color: colors.danger, fontSize: 16, marginVertical: 8 },
});
