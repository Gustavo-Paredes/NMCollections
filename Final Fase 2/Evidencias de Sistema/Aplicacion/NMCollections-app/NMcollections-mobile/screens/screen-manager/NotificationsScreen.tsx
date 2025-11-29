import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function NotificationsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Notificaciones Manager</Text>
      <Text style={styles.text}>Vista de notificaciones para manager.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#222' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#27ae60', marginBottom: 18 },
  text: { fontSize: 18, color: '#fff' },
});
