import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Image } from 'react-native';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';


export default function OrdersScreen() {
  const { token } = useAuth();
  const [pedidos, setPedidos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPedidos = async () => {
      if (!token) {
        setError('No hay token de autenticación');
        setLoading(false);
        return;
      }
      try {
        // Cambia la IP según tu red local o usa una variable de entorno
        const res = await axios.get('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/pedidos/all/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPedidos(res.data.results || res.data || []);
      } catch (err) {
        setError('Error al obtener pedidos');
        setPedidos([]);
      }
      setLoading(false);
    };
    fetchPedidos();
  }, [token]);

  // Agrupar pedidos por estado
  const grouped = pedidos.reduce((acc, p) => {
    acc[p.estado] = acc[p.estado] || [];
    acc[p.estado].push(p);
    return acc;
  }, {});

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Pedidos 📦</Text>
      {loading ? (
        <Text style={styles.text}>Cargando...</Text>
      ) : error ? (
        <Text style={styles.text}>Error: {error}</Text>
      ) : (
        <ScrollView style={{ width: '100%' }}>
          {Object.keys(grouped).map(estado => (
            <View key={estado} style={styles.estadoBlock}>
              <Text style={styles.estadoTitle}>{estado.charAt(0).toUpperCase() + estado.slice(1)}</Text>
              {grouped[estado].map(p => (
                <View key={p.id} style={styles.card}>
                  <View style={styles.cardHeader}>
                    <Text style={styles.pedidoId}>{p.numero_pedido}</Text>
                    <Text style={styles.pedidoUser}>{typeof p.usuario === 'object' ? p.usuario.correo : p.usuario}</Text>
                  </View>
                  <Text style={styles.pedidoTotal}>Total: ${p.total}</Text>
                  <Text style={styles.pedidoFecha}>Fecha: {new Date(p.fecha_pedido).toLocaleString()}</Text>
                  {Array.isArray(p.productos) && p.productos.length > 0 && (
                    <View style={styles.productosContainer}>
                      {p.productos.map(prod => (
                        <View key={prod.id} style={styles.productoRowClean}>
                          <View style={styles.productoInfoBox}>
                            <Text style={styles.productoNombre}>{prod.producto?.nombre}</Text>
                            <Text style={styles.productoCantidad}>x{prod.cantidad}</Text>
                            <Text style={styles.productoPrecio}>${prod.precio_total}</Text>
                          </View>
                          {prod.personalizacion?.imagen && (
                            <Image
                              source={{ uri: `http://192.168.1.44:8000${prod.personalizacion.imagen}` }}
                              style={styles.productoImg}
                              resizeMode="cover"
                            />
                          )}
                        </View>
                      ))}
                    </View>
                  )}
                </View>
              ))}
            </View>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

const estadoColors = ['#00ff88', '#ff4444', '#3498db', '#f1c40f', '#8e44ad', '#e67e22'];
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#23272f', paddingTop: 40, paddingHorizontal: 12 },
  title: { fontSize: 30, fontWeight: 'bold', color: '#27ae60', marginBottom: 22, textAlign: 'center', letterSpacing: 1 },
  loading: { color: '#27ae60', fontSize: 18, textAlign: 'center', marginTop: 40 },
  error: { color: '#e74c3c', fontSize: 18, textAlign: 'center', marginTop: 40 },
  estadoBlock: { marginBottom: 32, backgroundColor: '#222', borderRadius: 16, padding: 16 },
  estadoHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  estadoDot: { width: 16, height: 16, borderRadius: 8, marginRight: 10 },
  estadoTitle: { fontSize: 20, fontWeight: 'bold', color: '#27ae60', marginRight: 10 },
  estadoCount: { color: '#bbb', fontSize: 15, marginLeft: 'auto', fontWeight: 'bold' },
  card: { backgroundColor: '#333', padding: 16, marginVertical: 8, borderRadius: 14 },
  shadow: { shadowColor: '#27ae60', shadowOpacity: 0.12, shadowRadius: 8, elevation: 4 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  pedidoId: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  pedidoUser: { color: '#bbb', fontSize: 14 },
  pedidoTotal: { color: '#fff', fontWeight: 'bold', marginTop: 2 },
  bold: { color: '#27ae60', fontWeight: 'bold' },
  pedidoFecha: { color: '#aaa', fontSize: 13, marginBottom: 6 },
  productosContainer: { marginTop: 8 },
  productoRowClean: { flexDirection: 'row', alignItems: 'center', marginBottom: 8, backgroundColor: '#222', borderRadius: 8, padding: 8 },
  productoInfoBox: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  productoNombre: { color: '#fff', fontWeight: 'bold', fontSize: 15 },
  productoCantidad: { color: '#27ae60', fontWeight: 'bold', fontSize: 15, marginLeft: 8 },
  productoPrecio: { color: '#bbb', fontSize: 14, marginLeft: 8 },
  productoImg: { width: 48, height: 48, borderRadius: 8, marginLeft: 10, backgroundColor: '#222' },
});
