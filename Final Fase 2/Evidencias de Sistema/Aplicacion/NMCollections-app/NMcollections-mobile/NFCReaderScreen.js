import React, { useEffect, useState } from 'react';
import { View, Text, Image, Button, ActivityIndicator, StyleSheet, TextInput, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
// import Constants from 'expo-constants';
// const isExpoGo = Constants.appOwnership === 'expo';
// Eliminado NFCManager, solo simulación y deep linking
import { useAuth } from './contexts/AuthContext';

export default function NFCReaderScreen({ route }) {
  const [card, setCard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [inputUrl, setInputUrl] = useState('');
  const { token } = useAuth();

  // Si viene por deep link, usa el código del parámetro
  const codigo_nfc = route?.params?.codigo_nfc;

  // Eliminada función readNFC, solo simulación manual

  async function fetchCard(nfcCode) {
    setLoading(true);
    try {
      const response = await fetch(`https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/nfc/${nfcCode}/`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setCard(data);
    } catch {
      setCard(null);
    }
    setLoading(false);
  }

  function extractNfcCodeFromUrl(url) {
    // Extrae el código NFC de la URL tipo https://zkbc59xz-8000.brs.devtunnels.ms/NFC/NFC-AF9GS2VB/
    const match = url.match(/\/NFC\/([A-Za-z0-9-]+)\/?$/);
    return match ? match[1] : '';
  }

  useEffect(() => {
    if (codigo_nfc) {
      fetchCard(codigo_nfc);
    }
    // No escaneo automático en Expo Go
  }, []);

    if (loading) return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#27ae60" />
      </View>
    );
    if (!card) return (
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={80}
      >
        <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
          {Platform.OS === 'web' && (
            <Text style={{ color: 'red', marginBottom: 10 }}>
              NFC no disponible en Expo Go/web. Usa la simulación.
            </Text>
          )}
          <Text style={styles.info}>Ingresa la URL NFC para simular el escaneo:</Text>
          <TextInput
            style={styles.input}
            placeholder="https://zkbc59xz-8000.brs.devtunnels.ms/NFC/NFC-XXXXXXX/"
            value={inputUrl}
            onChangeText={setInputUrl}
            autoCapitalize="none"
            placeholderTextColor="#888"
          />
          <Button
            title="Simular escaneo NFC"
            onPress={() => {
              const code = extractNfcCodeFromUrl(inputUrl);
              if (code) fetchCard(code);
              else alert('URL inválida');
            }}
            color="#007bff"
          />
        </ScrollView>
      </KeyboardAvoidingView>
    );

  return (
    <View style={styles.bg}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.cardBox}>
          <Text style={styles.title}>{card.producto?.nombre || 'Sin nombre'}</Text>
          {card.imagen ? (
            <Image source={{ uri: `https://zkbc59xz-8000.brs.devtunnels.ms${card.imagen}` }} style={styles.image} />
          ) : (
            <Text style={styles.noimg}>Sin imagen disponible</Text>
          )}
          <View style={styles.details}>
            <Text style={styles.label}><Text style={styles.bold}>Código NFC:</Text> <Text style={styles.nfcCode}>{card.codigo_nfc}</Text></Text>
            <Text style={styles.label}><Text style={styles.bold}>Estado:</Text> <Text style={styles.estado}>{card.estado}</Text></Text>
            <Text style={styles.label}><Text style={styles.bold}>Dueño:</Text> <Text style={styles.dueno}>{card.usuario?.username || 'Sin dueño'}</Text></Text>
            <Text style={styles.label}><Text style={styles.bold}>Descripción:</Text> <Text style={styles.descripcion}>{card.producto?.descripcion || 'Sin descripción'}</Text></Text>
          </View>
          {String(card.es_dueno).toLowerCase().trim() === "true" && (
            <View style={styles.buttonBox}>
              <Button
                title="Transferir carta"
                onPress={async () => {
                  try {
                    const res = await fetch(`https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/nfc/${card.codigo_nfc}/transferir/`, {
                      method: 'POST',
                      headers: {
                        'Authorization': token ? `Bearer ${token}` : '',
                        'Content-Type': 'application/json'
                      }
                    });
                    const result = await res.json();
                    if (res.ok) {
                      alert('La carta está lista para transferirse al próximo usuario que escanee.');
                    } else if (result && result.error === 'Solo el dueño puede transferir la carta.') {
                      alert('Solo el dueño puede transferir la carta. Verifica que estés logueado correctamente.');
                    } else {
                      alert('No se pudo transferir la carta.');
                    }
                  } catch {
                    alert('Error de conexión.');
                  }
                }}
                color="#27ae60"
              />
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  );
}

// Eliminada función extractCode, solo simulación manual

const styles = StyleSheet.create({
  bg: {
    flex: 1,
    backgroundColor: '#23272f',
  },
  container: { padding: 20, alignItems: 'center', flex: 1, justifyContent: 'center' },
  scrollContainer: { flexGrow: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  cardBox: {
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
    backgroundColor: '#222',
    borderRadius: 18,
    padding: 22,
    marginBottom: 24,
    elevation: 4,
    shadowColor: '#27ae60',
    shadowOpacity: 0.12,
    shadowRadius: 8,
  },
  buttonBox: {
    width: '100%',
    marginTop: 16,
    marginBottom: 16,
    alignItems: 'center',
  },
  title: {
    fontWeight: 'bold',
    fontSize: 26,
    marginBottom: 16,
    textAlign: 'center',
    color: '#27ae60',
    letterSpacing: 1,
  },
  image: {
    width: 300,
    height: 400,
    borderRadius: 14,
    marginBottom: 16,
    backgroundColor: '#23272f',
    borderWidth: 2,
    borderColor: '#27ae60',
  },
  noimg: {
    fontSize: 16,
    color: '#888',
    marginBottom: 16,
    fontStyle: 'italic',
  },
  details: {
    width: '100%',
    marginBottom: 16,
    backgroundColor: '#23272f',
    borderRadius: 10,
    padding: 12,
  },
  label: {
    fontSize: 16,
    marginBottom: 8,
    color: '#fff',
  },
  bold: {
    color: '#27ae60',
    fontWeight: 'bold',
  },
  nfcCode: {
    color: '#27ae60',
    fontWeight: 'bold',
    fontSize: 16,
  },
  estado: {
    color: '#f1c40f',
    fontWeight: 'bold',
    fontSize: 16,
  },
  dueno: {
    color: '#3498db',
    fontWeight: 'bold',
    fontSize: 16,
  },
  descripcion: {
    color: '#bbb',
    fontSize: 15,
    fontStyle: 'italic',
  },
  info: { textAlign: 'center', marginTop: 40, fontSize: 18 },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 10, width: '100%', marginBottom: 16, fontSize: 16 }
});
