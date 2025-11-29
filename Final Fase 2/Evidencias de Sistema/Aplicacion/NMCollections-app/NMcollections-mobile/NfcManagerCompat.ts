import { Platform } from 'react-native';

let NfcManager: any, NfcTech: any, isExpoGo = false;

try {
  isExpoGo = !!global.Expo;
} catch { isExpoGo = false; }

if (Platform.OS === 'web' || isExpoGo) {
  // Mock para Expo Go y web
  NfcManager = {
    start: async () => {},
    isSupported: async () => false,
    requestTechnology: async () => {},
    getTag: async () => ({}),
    cancelTechnologyRequest: async () => {},
  };
  NfcTech = {};
} else {
  // Importación dinámica solo en build nativo
  let nfc;
  try {
    nfc = require('react-native-nfc-manager');
    NfcManager = nfc.default;
    NfcTech = nfc.NfcTech;
  } catch {
    NfcManager = {
      start: async () => { throw new Error('NFC no disponible'); },
      isSupported: async () => false,
      requestTechnology: async () => {},
      getTag: async () => ({}),
      cancelTechnologyRequest: async () => {},
    };
    NfcTech = {};
  }
}

export { NfcManager, NfcTech, isExpoGo };
