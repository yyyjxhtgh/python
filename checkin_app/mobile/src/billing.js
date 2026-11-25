// In-app purchases through RevenueCat (App Store and Google Play).
// Needs a development or store build: Expo Go has no store billing.
import { Platform } from 'react-native';

let Purchases = null;
try {
  Purchases = require('react-native-purchases').default;
} catch {
  Purchases = null;
}

const KEY = Platform.select({
  ios: process.env.EXPO_PUBLIC_RC_IOS_KEY,
  android: process.env.EXPO_PUBLIC_RC_ANDROID_KEY,
});

export const TERMS_URL = process.env.EXPO_PUBLIC_TERMS_URL || '';
export const PRIVACY_URL = process.env.EXPO_PUBLIC_PRIVACY_URL || '';

let configuredFor = null;

export function billingAvailable() {
  return Boolean(Purchases && KEY);
}

/** Connect purchases on this phone to the signed-in user (their random billing id). */
export async function initBilling(billingId) {
  if (!billingAvailable() || !billingId) return false;
  try {
    if (configuredFor === null) {
      Purchases.configure({ apiKey: KEY, appUserID: billingId });
    } else if (configuredFor !== billingId) {
      await Purchases.logIn(billingId);
    }
    configuredFor = billingId;
    return true;
  } catch (e) {
    console.warn('Billing not available', e);
    return false;
  }
}

/** Plans from the "current" offering set up in RevenueCat (e.g. monthly and yearly). */
export async function getPackages() {
  const offerings = await Purchases.getOfferings();
  return offerings.current ? offerings.current.availablePackages : [];
}

/** Opens the store's payment sheet. Returns false if the user cancelled. */
export async function buy(pkg) {
  try {
    await Purchases.purchasePackage(pkg);
    return true;
  } catch (e) {
    if (e.userCancelled) return false;
    throw e;
  }
}

export async function restore() {
  await Purchases.restorePurchases();
}

/** Link to the App Store / Google Play page where the user can cancel or change plan. */
export async function managementUrl() {
  const info = await Purchases.getCustomerInfo();
  return info.managementURL;
}

export async function signOutBilling() {
  if (configuredFor === null) return;
  try {
    await Purchases.logOut();
  } catch {
    // already anonymous
  }
  configuredFor = null;
}

export function periodText(pkg) {
  switch (pkg.packageType) {
    case 'MONTHLY':
      return 'per month';
    case 'ANNUAL':
      return 'per year';
    case 'WEEKLY':
      return 'per week';
    case 'SIX_MONTH':
      return 'every 6 months';
    case 'THREE_MONTH':
      return 'every 3 months';
    case 'LIFETIME':
      return 'one time';
    default:
      return '';
  }
}
