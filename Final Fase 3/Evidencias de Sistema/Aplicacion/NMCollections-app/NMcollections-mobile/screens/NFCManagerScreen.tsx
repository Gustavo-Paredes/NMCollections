import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, FlatList, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import NfcManager, { NfcEvents } from 'react-native-nfc-manager';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';

export default function NFCManagerScreen() {
  const [input, setInput] = useState('');
  const [scanning, setScanning] = useState(false);
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigation = useNavigation();
  const { token } = useAuth();

  // Extrae el código NFC del link o del input directo
  const extractCodigo = (str) => {
    const match = str.match(/NFC\/(NFC-[A-Z0-9]+)/i);
    if (match) return match[1];
    if (/^NFC-[A-Z0-9]+$/i.test(str)) return str;
    return '';
  };

  // Leer NFC manual
  const handleManualScan = () => {
    const codigo = extractCodigo(input.trim());
    if (codigo) {
      navigation.navigate('NFCReader', { codigo_nfc: codigo });
    } else {
      Alert.alert('Error', 'Ingresa un link o código NFC válido');
    }
  };

  // Leer NFC físico
  const handleNFCScan = async () => {
    setScanning(true);
    try {
      await NfcManager.start();
      NfcManager.setEventListener(NfcEvents.DiscoverTag, tag => {
        setScanning(false);
        NfcManager.setEventListener(NfcEvents.DiscoverTag, null);
        NfcManager.unregisterTagEvent().catch(() => {});
        let codigo = '';
        if (tag.ndefMessage && tag.ndefMessage.length > 0) {
          const ndefRecord = tag.ndefMessage[0];
          try {
            const uri = require('react-native-nfc-manager').Ndef.uri.decodePayload(ndefRecord.payload);
            codigo = extractCodigo(uri);
          } catch {
            codigo = '';
          }
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

  // Obtener productos únicos NFC disponibles
  const fetchProductos = async () => {
    setLoading(true);
    try {
      const res = await fetch('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/productos-unicos-nfc/', {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json'
        }
      });
      if (res.status === 403) {
        Alert.alert('Permiso denegado', 'No tienes permisos para ver los productos únicos NFC. Inicia sesión como manager/admin.');
        setProductos([]);
        setLoading(false);
        return;
      }
      const data = await res.json();
      setProductos(Array.isArray(data) ? data : []);
    } catch {
      setProductos([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchProductos();
  }, []);

  // Asignar NFC a producto
  const handleAsignarNFC = (producto) => {
    // Asignar NFC directamente desde aquí
    Alert.alert(
      'Asignar NFC',
      `¿Seguro que quieres asignar NFC a "${producto.nombre}"?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Asignar',
          onPress: async () => {
            try {
              const res = await fetch('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/nfc/crear/', {
                method: 'POST',
                headers: {
                  'Authorization': token ? `Bearer ${token}` : '',
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ producto_id: producto.id })
              });
              const data = await res.json();
              if (res.ok && data.codigo_nfc) {
                if (Platform.OS === 'web') {
                  Alert.alert('NFC asignado', `Código NFC generado: ${data.codigo_nfc}\n\nNo es posible escribir en NFC desde la web. Usa la app móvil para grabar el código en el sticker.`,[{text:'OK',onPress:()=>fetchProductos()}]);
                } else {
                  Alert.alert('NFC asignado', `Código NFC generado: ${data.codigo_nfc}\n\nAcerca el sticker NFC para grabar el código.`, [
                    {
                      text: 'Escribir en NFC',
                      onPress: async () => {
                        try {
                          await NfcManager.start();
                          await NfcManager.requestTechnology('Ndef');
                          const url = `https://zkbc59xz-8000.brs.devtunnels.ms/NFC/${data.codigo_nfc}/`;
                          const ndefMessage = Ndef.encodeMessage([Ndef.uriRecord(url)]);
                          await NfcManager.writeNdefMessage(ndefMessage);
                          await NfcManager.cancelTechnologyRequest();
                          Alert.alert('Éxito', 'El código NFC fue escrito correctamente.', [
                            {
                              text: 'OK',
                              onPress: () => fetchProductos()
                            }
                          ]);
                        } catch {
                          Alert.alert('Error', 'No se pudo escribir en el NFC.');
                        }
                      }
                    }
                  ]);
                }
              } else {
                Alert.alert('Error', data.error || 'No se pudo asignar el NFC.');
              }
            } catch {
              Alert.alert('Error', 'No se pudo conectar al servidor.');
            }
          }
        }
      ]
    );
  };

  return (
    <View style={styles.bg}>
      <View style={styles.card}>
        <MaterialCommunityIcons name="nfc-variant" size={48} color="#27ae60" style={{ alignSelf: 'center', marginBottom: 8 }} />
        <Text style={styles.title}>Gestión de NFC</Text>
        <Text style={styles.subtitle}>Escanea, lee o asigna NFC a cartas únicas</Text>
        {/* Leer NFC manual */}
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
        {/* Asignar NFC a producto */}
        <Text style={styles.subtitle2}>Asignar NFC a carta única</Text>
        {loading ? (
          <ActivityIndicator size="small" color="#27ae60" />
        ) : (
          <FlatList
            data={productos}
            keyExtractor={item => item.id.toString()}
            renderItem={({ item }) => (
              <TouchableOpacity style={styles.productoItem} onPress={() => handleAsignarNFC(item)}>
                <Text style={styles.productoText}>{item.nombre}</Text>
                <MaterialCommunityIcons name="plus-circle" size={22} color="#27ae60" />
              </TouchableOpacity>
            )}
            ListEmptyComponent={<Text style={styles.emptyText}>No hay cartas únicas disponibles para asignar NFC.</Text>}
            style={{ width: '100%', marginTop: 8 }}
          />
        )}
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
  subtitle2: {
    fontSize: 16,
    color: '#27ae60',
    marginTop: 18,
    marginBottom: 8,
    textAlign: 'center',
    fontWeight: 'bold',
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
  productoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#23272f',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    width: '100%',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: '#27ae60',
  },
  productoText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  emptyText: {
    color: '#bbb',
    fontSize: 15,
    textAlign: 'center',
    marginTop: 8,
  },
});
