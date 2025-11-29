import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ActivityIndicator, Alert } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import axios from 'axios';

interface User {
  id: number;
  correo: string;
  username: string;
  nombre: string;
  apellido_paterno: string;
  apellido_materno: string;
  telefono: string;
  direccion: string;
  rol: {
    id: number;
    nombre: string;
    descripcion: string;
  };
  fecha_registro: string;
  estado: string;
  nombre_completo: string;
}

interface ProfileScreenProps {
  token: string;
}

export default function ProfileScreen({ token }: ProfileScreenProps) {
  const [user, setUser] = useState<User | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ username: '', email: '', telefono: '', direccion: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    setLoading(true);
    try {
      const res = await axios.get<User>('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/auth/user/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(res.data);
      setForm({
        username: res.data.username || '',
        email: res.data.correo || '',
        telefono: res.data.telefono || '',
        direccion: res.data.direccion || '',
      });
    } catch (err) {
      Alert.alert('Error', 'No se pudo cargar el perfil');
    }
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.patch('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/auth/user/', form, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEditMode(false);
      fetchUser();
      Alert.alert('Perfil actualizado', 'Tus datos han sido guardados');
    } catch (err) {
      Alert.alert('Error', 'No se pudo guardar el perfil');
    }
    setSaving(false);
  };

  if (loading) {
    return (
      <View style={styles.bg}>
        <ActivityIndicator size="large" color="#27ae60" />
      </View>
    );
  }

  // Vista única editable para todos los roles
  return (
    <View style={styles.bg}>
      <View style={styles.card}>
        <MaterialCommunityIcons name={user?.rol?.id === 5 ? "palette" : "account-circle"} size={48} color="#27ae60" style={{ marginBottom: 10 }} />
        <Text style={styles.title}>{user?.rol?.id === 5 ? "Perfil Diseñador" : "Mi Perfil"}</Text>
        <Text style={styles.desc}>{user?.rol?.id === 5 ? "¡Bienvenido, diseñador! Aquí puedes gestionar tus cartas y creaciones." : "Actualiza tu información personal y contraseña."}</Text>
        {editMode ? (
          <>
            <TextInput
              style={styles.input}
              placeholder="Usuario"
              value={form.username}
              onChangeText={v => setForm(f => ({ ...f, username: v }))}
              placeholderTextColor="#888"
            />
            <TextInput
              style={styles.input}
              placeholder="Correo"
              value={form.email}
              onChangeText={v => setForm(f => ({ ...f, email: v }))}
              placeholderTextColor="#888"
            />
            <TextInput
              style={styles.input}
              placeholder="Teléfono"
              value={form.telefono}
              onChangeText={v => setForm(f => ({ ...f, telefono: v }))}
              placeholderTextColor="#888"
            />
            <TextInput
              style={styles.input}
              placeholder="Dirección"
              value={form.direccion}
              onChangeText={v => setForm(f => ({ ...f, direccion: v }))}
              placeholderTextColor="#888"
            />
            <TouchableOpacity style={styles.btn} onPress={handleSave} disabled={saving}>
              {saving ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Guardar</Text>}
            </TouchableOpacity>
            <TouchableOpacity style={[styles.btn, { backgroundColor: '#555', marginTop: 8 }]} onPress={() => setEditMode(false)}>
              <Text style={styles.btnText}>Cancelar</Text>
            </TouchableOpacity>
          </>
        ) : (
          <>
            <Text style={styles.label}>Usuario: <Text style={styles.value}>{user?.username}</Text></Text>
            <Text style={styles.label}>Correo: <Text style={styles.value}>{user?.correo}</Text></Text>
            <Text style={styles.label}>Teléfono: <Text style={styles.value}>{user?.telefono}</Text></Text>
            <Text style={styles.label}>Dirección: <Text style={styles.value}>{user?.direccion}</Text></Text>
            <TouchableOpacity style={styles.btn} onPress={() => setEditMode(true)}>
              <Text style={styles.btnText}>Editar Perfil</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1, backgroundColor: '#474d54', justifyContent: 'center', alignItems: 'center' },
  card: { backgroundColor: '#222', borderRadius: 18, borderWidth: 2, borderColor: '#27ae60', width: 320, padding: 28, alignItems: 'center', shadowColor: '#27ae60', shadowOpacity: 0.15, shadowRadius: 8, elevation: 4 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginBottom: 8 },
  desc: { fontSize: 15, color: '#bbb', marginBottom: 18, textAlign: 'center' },
  btn: { backgroundColor: '#27ae60', borderRadius: 14, paddingVertical: 8, paddingHorizontal: 28, marginTop: 10 },
  btnText: { color: '#fff', fontWeight: 'bold', fontSize: 17 },
  input: { backgroundColor: '#333', color: '#fff', borderRadius: 10, padding: 10, marginBottom: 10, width: '100%', fontSize: 16, borderWidth: 1, borderColor: '#27ae60' },
  label: { color: '#bbb', fontSize: 16, marginBottom: 4 },
  value: { color: '#fff', fontWeight: 'bold' },
});
