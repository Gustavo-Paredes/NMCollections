import React, { useState } from 'react';
import { useAuth } from './contexts/AuthContext';
import { useCatalog } from './contexts/CatalogContext';
import { View, TextInput, Text, StyleSheet, TouchableOpacity } from 'react-native';
import axios from 'axios';

interface LoginScreenProps {
  navigation: any;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ navigation }) => {
  const { setToken, setUser } = useAuth();
  const { setProducts } = useCatalog();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  // ...

  const handleLogin = async () => {
    setLoading(true);
    const loginUrl = 'https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/auth/login/';
    const loginPayload = {
      email: username.toLowerCase(),
      password,
    };
    try {
      const response = await axios.post(loginUrl, loginPayload);
      if (response.data && response.data.access) {
        setToken(response.data.access);
        setUser(response.data.user);
        setMessage('Login exitoso');
        try {
          const catalogRes = await axios.get('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/productos/', {
            headers: { Authorization: `Bearer ${response.data.access}` },
          });
          setProducts(catalogRes.data.results || []);
        } catch (err) {
          setProducts([]);
        }
        navigation.replace('Main');
      } else {
        alert('Login fallido: ' + JSON.stringify(response.data));
      }
    } catch (error: any) {
      let errorMsg = 'Login fallido';
      if (error.response && error.response.data) {
        errorMsg += ': ' + (error.response.data.detail || error.response.data.error || JSON.stringify(error.response.data));
      } else {
        errorMsg += ': No se recibió respuesta del servidor.';
      }
      alert(errorMsg);
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>NMCollections</Text>
      <View style={styles.form}>
        <TextInput
          placeholder="Correo electrónico"
          value={username}
          onChangeText={setUsername}
          style={[styles.input, { color: '#000', placeholderTextColor: '#000' }]}
          autoCapitalize="none"
          keyboardType="email-address"
        />
        <TextInput
          placeholder="Contraseña"
          value={password}
          onChangeText={setPassword}
          secureTextEntry={true}
          style={[styles.input, { color: '#000', placeholderTextColor: '#000' }]}
        />
        <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
          <Text style={styles.buttonText}>{loading ? 'Ingresando...' : 'Ingresar'}</Text>
        </TouchableOpacity>
        {/* ...sin debug ni test api... */}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f7f7f7' },
  title: { fontSize: 32, fontWeight: 'bold', color: '#222', marginBottom: 30 },
  form: { width: '90%', maxWidth: 350, backgroundColor: '#fff', borderRadius: 12, padding: 24, shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 4, elevation: 2 },
  input: { borderWidth: 1, borderColor: '#ddd', marginBottom: 16, padding: 12, borderRadius: 8, fontSize: 16 },
  button: { backgroundColor: '#27ae60', paddingVertical: 12, borderRadius: 8, alignItems: 'center', marginTop: 8 },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 18 },
  error: { color: '#e74c3c', marginTop: 12, textAlign: 'center' },
});

export default LoginScreen;
