import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Alert, Linking, ScrollView, Text, View } from 'react-native';

import { api, formatWhen } from '../api';
import { billingAvailable, buy, getPackages, managementUrl, periodText, PRIVACY_URL, restore, TERMS_URL } from '../billing';
import { Button, Card, colors, styles } from '../ui';

export default function SubscriptionScreen({ user, onUserChange }) {
  const [packages, setPackages] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const loadPackages = useCallback(async () => {
    if (!billingAvailable()) return setPackages([]);
    try {
      setPackages(await getPackages());
    } catch (e) {
      setError('Could not load plans from the store. Check your connection and try again.');
      setPackages([]);
    }
  }, []);

  useEffect(() => {
    loadPackages();
  }, [loadPackages]);

  // After the store confirms, ask our server to check the purchase with RevenueCat.
  const syncWithServer = async () => {
    const me = await api.syncSubscription();
    onUserChange(me);
    return me;
  };

  const purchase = async (pkg) => {
    setBusy(true);
    setError(null);
    try {
      if (await buy(pkg)) {
        const me = await syncWithServer();
        if (me.subscription_active) Alert.alert('Thank you!', 'Your check-in calls are now on.');
      }
    } catch (e) {
      setError(e.message || 'The purchase did not go through.');
    } finally {
      setBusy(false);
    }
  };

  const restorePurchases = async () => {
    setBusy(true);
    setError(null);
    try {
      await restore();
      const me = await syncWithServer();
      Alert.alert(me.subscription_active ? 'Subscription restored' : 'No active subscription found on this store account');
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const manage = async () => {
    try {
      const url = await managementUrl();
      if (url) Linking.openURL(url);
    } catch (e) {
      setError(e.message);
    }
  };

  if (!billingAvailable()) {
    return (
      <ScrollView contentContainerStyle={styles.screen}>
        <Text style={styles.h1}>Plan</Text>
        <Card>
          <Text style={styles.body}>
            Purchases aren't available in this build. Install a development or store build, and set the RevenueCat keys
            in mobile/.env.
          </Text>
        </Card>
        <StatusCard user={user} />
      </ScrollView>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.h1}>Plan</Text>
      <StatusCard user={user} />

      {user.subscription_active ? (
        <Button title="Manage or cancel subscription" outline onPress={manage} />
      ) : (
        <>
          <Text style={[styles.h2, { marginTop: 8 }]}>Choose a plan</Text>
          <Text style={[styles.body, { marginBottom: 10 }]}>
            Includes scheduled check-in calls, automatic retries, and texts and calls to your contacts if you need help or
            don't answer.
          </Text>
          {packages === null && <ActivityIndicator color={colors.primary} />}
          {packages && packages.length === 0 && !error && <Text style={styles.muted}>No plans are available right now.</Text>}
          {packages &&
            packages.map((pkg) => (
              <Card key={pkg.identifier}>
                <Text style={styles.h2}>{pkg.product.title}</Text>
                <Text style={[styles.body, { marginBottom: 6 }]}>
                  {pkg.product.priceString} {periodText(pkg)}
                </Text>
                {pkg.product.introPrice && (
                  <Text style={[styles.muted, { color: colors.ok }]}>
                    Intro offer: {pkg.product.introPrice.priceString} for {pkg.product.introPrice.periodNumberOfUnits}{' '}
                    {pkg.product.introPrice.periodUnit.toLowerCase()}(s)
                  </Text>
                )}
                <Button title={busy ? 'Please wait…' : 'Subscribe'} onPress={() => purchase(pkg)} disabled={busy} />
              </Card>
            ))}
        </>
      )}

      {error && <Text style={styles.error}>{error}</Text>}
      <Button title="Restore purchases" outline onPress={restorePurchases} disabled={busy} />

      <Text style={[styles.muted, { marginTop: 16, fontSize: 13, lineHeight: 18 }]}>
        Payment is charged to your App Store or Google Play account. The subscription renews automatically unless you turn
        off auto-renew at least 24 hours before the end of the current period. You can manage or cancel it in your store
        account settings. The "I need help" button keeps working without a subscription.
      </Text>
      <View style={[styles.row, { marginTop: 8, gap: 16 }]}>
        {!!TERMS_URL && (
          <Text style={{ color: colors.primary, fontSize: 15 }} onPress={() => Linking.openURL(TERMS_URL)}>
            Terms of Use
          </Text>
        )}
        {!!PRIVACY_URL && (
          <Text style={{ color: colors.primary, fontSize: 15 }} onPress={() => Linking.openURL(PRIVACY_URL)}>
            Privacy Policy
          </Text>
        )}
      </View>
    </ScrollView>
  );
}

function StatusCard({ user }) {
  if (!user.subscription_required && !user.subscription_active) {
    return (
      <Card>
        <Text style={styles.body}>Check-in calls are currently free on this service.</Text>
      </Card>
    );
  }
  return (
    <Card>
      <Text style={styles.muted}>Your plan</Text>
      <Text style={{ fontSize: 24, fontWeight: '800', color: user.subscription_active ? colors.ok : colors.help }}>
        {user.subscription_active ? 'Active' : 'Not subscribed'}
      </Text>
      {user.subscription_active && user.subscription_expires_at && !user.subscription_expires_at.startsWith('9999') && (
        <Text style={styles.muted}>
          {user.subscription_will_renew ? 'Renews' : 'Ends'} {formatWhen(user.subscription_expires_at)}
        </Text>
      )}
    </Card>
  );
}
