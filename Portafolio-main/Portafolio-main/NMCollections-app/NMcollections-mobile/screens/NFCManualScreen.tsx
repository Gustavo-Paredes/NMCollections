import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import NfcManager, {NfcEvents} from 'react-native-nfc-manager';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function NFCManualScreen() {
  const [input, setInput] = useState('');
  const [scanning, setScanning] = useState(false);
  const navigation = useNavigation();

  // Extrae el código NFC del link o del input directo
  const extractCodigo = (str) => {
    const match = str.match(/NFC\/(NFC-[A-Z0-9]+)/i);
    if (match) return match[1];
    if (/^NFC-[A-Z0-9]+$/i.test(str)) return str;
    return '';
  };

  const handleManualScan = () => {
    const codigo = extractCodigo(input.trim());
    if (codigo) {
      navigation.navigate('NFCReader', { codigo_nfc: codigo });
    } else {
      Alert.alert('Error', 'Ingresa un link o código NFC válido');
    }
  };

  const handleNFCScan = async () => {
    setScanning(true);
    try {
      await NfcManager.start();
      NfcManager.setEventListener(NfcEvents.DiscoverTag, tag => {
        setScanning(false);
        NfcManager.setEventListener(NfcEvents.DiscoverTag, null);
        NfcManager.unregisterTagEvent().catch(() => {});
        // Intenta extraer el link/código del tag
        let codigo = '';
        if (tag.ndefMessage && tag.ndefMessage.length > 0) {
          const payload = tag.ndefMessage[0].payload;
          // El payload puede tener un prefijo, lo convertimos a string
          let text = '';
          try {
            text = String.fromCharCode.apply(null, payload.slice(3));
          } catch {
            text = '';
          }
          codigo = extractCodigo(text);
        }
        if (codigo) {
          navigation.navigate('NFCReader', { codigo_nfc: codigo });
        } else {
          Alert.alert('Error', 'No se pudo leer un código NFC válido');
        }
      });
      await NfcManager.registerTagEvent();
    } catch (e) {
      setScanning(false);
      Alert.alert('Error', 'No se pudo iniciar el escaneo NFC');
    }
  };

  return (
    <View style={styles.bg}>
      <View style={styles.card}>
        <MaterialCommunityIcons name="nfc-variant" size={48} color="#27ae60" style={{ alignSelf: 'center', marginBottom: 8 }} />
        <Text style={styles.title}>Escanea tu carta NFC</Text>
        <Text style={styles.subtitle}>Acerca el sticker NFC o ingresa el código manualmente</Text>
        <TextInput
          style={styles.input}
          placeholder="Pega el link o el código NFC"
          value={input}
          onChangeText={setInput}
          autoCapitalize="characters"
          autoCorrect={false}
        />
        <TouchableOpacity style={styles.buttonManual} onPress={handleManualScan}>
          <MaterialCommunityIcons name="magnify" size={22} color="#fff" />
          <Text style={styles.buttonText}>Ver carta manual</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.buttonScan, scanning && styles.buttonScanDisabled]} onPress={handleNFCScan} disabled={scanning}>
          <MaterialCommunityIcons name="qrcode-scan" size={22} color="#fff" />
          <Text style={styles.buttonText}>{scanning ? "Esperando NFC..." : "Escanear NFC"}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  bg: {
    flex: 1,
    backgroundColor: '#23272f',
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    width: '95%',
    maxWidth: 400,
    backgroundColor: '#222',
    borderRadius: 18,
    padding: 28,
    shadowColor: '#27ae60',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 4,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#27ae60',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 15,
    color: '#bbb',
    marginBottom: 18,
    textAlign: 'center',
  },
  input: {
    width: '100%',
    borderWidth: 1,
    borderColor: '#27ae60',
    borderRadius: 10,
    padding: 12,
    marginBottom: 18,
    fontSize: 16,
    backgroundColor: '#23272f',
    color: '#fff',
  },
  buttonManual: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#27ae60',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 8,
    marginBottom: 14,
    width: '100%',
    justifyContent: 'center',
    shadowColor: '#27ae60',
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 2,
  },
  buttonScan: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2980b9',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 8,
    width: '100%',
    justifyContent: 'center',
    shadowColor: '#2980b9',
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 2,
  },
  buttonScanDisabled: {
    backgroundColor: '#b2bec3',
  },
  buttonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});
