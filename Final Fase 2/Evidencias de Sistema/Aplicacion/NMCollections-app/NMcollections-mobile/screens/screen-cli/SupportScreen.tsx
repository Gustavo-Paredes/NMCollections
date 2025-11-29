import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function SupportScreen() {
  return (
    <View style={styles.bg}>
      <View style={styles.card}>
        <MaterialCommunityIcons name="chat-question" size={48} color="#27ae60" style={{ marginBottom: 10 }} />
        <Text style={styles.title}>Soporte</Text>
        <Text style={styles.desc}>Chatea con soporte y abre tickets.</Text>
        <TouchableOpacity style={styles.btn}>
          <Text style={styles.btnText}>Ir a Soporte</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1, backgroundColor: '#474d54', justifyContent: 'center', alignItems: 'center' },
  card: { backgroundColor: '#222', borderRadius: 18, borderWidth: 2, borderColor: '#27ae60', width: 320, padding: 28, alignItems: 'center', shadowColor: '#27ae60', shadowOpacity: 0.15, shadowRadius: 8, elevation: 4 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginBottom: 8 },
  desc: { fontSize: 15, color: '#bbb', marginBottom: 18, textAlign: 'center' },
  btn: { backgroundColor: '#27ae60', borderRadius: 14, paddingVertical: 8, paddingHorizontal: 28 },
  btnText: { color: '#fff', fontWeight: 'bold', fontSize: 17 },
});
