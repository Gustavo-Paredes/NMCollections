import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import axios from 'axios';

interface PedidoProducto {
  id: number;
  cantidad: number;
  producto: { nombre: string };
}

interface Pedido {
  id: number;
  numero_pedido: string;
  estado: string;
  fecha_pedido: string;
  metodo_pago: string;
  total: string;
  productos: PedidoProducto[];
}

interface OrdersScreenProps {
  token: string | null;
}

const OrdersScreen: React.FC<OrdersScreenProps> = ({ token }) => {
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPedidos = async () => {
      try {
        const res = await axios.get('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/pedidos/', {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        setPedidos(res.data.results || []);
      } catch {
        setPedidos([]);
      }
      setLoading(false);
    };
    fetchPedidos();
  }, [token]);

  if (loading) return <Text style={styles.loading}>Cargando pedidos...</Text>;
  if (!pedidos.length) return (
    <View style={styles.emptyCard}>
      <Text style={styles.emptyIcon}>ℹ️</Text>
      <Text style={styles.emptyTitle}>No tienes pedidos aún</Text>
      <Text style={styles.emptyText}>Explora el catálogo y realiza tu primera compra</Text>
    </View>
  );

  return (
    <FlatList
      data={pedidos}
      keyExtractor={p => p.id.toString()}
      contentContainerStyle={styles.listContainer}
      renderItem={({ item }) => {
        const productosMostrados = item.productos.slice(0, 3);
        const productosRestantes = item.productos.length - 3;
        return (
          <View style={styles.card}>
            <View style={styles.head}>
              <Text style={styles.num}>#{item.numero_pedido}</Text>
              <Text style={[styles.badgeEstado, estadoBadge(item.estado)]}>{estadoTexto(item.estado)}</Text>
            </View>
            <View style={styles.meta}>
              <Text style={styles.metaItem}><Text style={styles.metaLabel}>Fecha:</Text> {formateaFecha(item.fecha_pedido)}</Text>
              <Text style={styles.metaItem}><Text style={styles.metaLabel}>Método:</Text> {item.metodo_pago?.toUpperCase()}</Text>
              <Text style={styles.metaItem}><Text style={styles.metaLabel}>Total:</Text> ${parseInt(item.total).toLocaleString()}</Text>
              <Text style={styles.metaItem}><Text style={styles.metaLabel}>Ítems:</Text> {item.productos.length}</Text>
            </View>
            <View style={styles.items}>
              <Text style={styles.itemsTitle}>Productos</Text>
              {productosMostrados.map(prod => (
                <Text key={prod.id} style={styles.itemRow}>📦 {prod.cantidad}x {prod.producto.nombre}</Text>
              ))}
              {productosRestantes > 0 && (
                <Text style={styles.itemRow}>y {productosRestantes} más...</Text>
              )}
            </View>
            <View style={styles.actions}>
              <TouchableOpacity style={styles.btn}><Text style={styles.btnText}>Ver Detalle</Text></TouchableOpacity>
              {item.estado === 'pendiente' && (
                <TouchableOpacity style={styles.btnDanger}><Text style={styles.btnText}>Cancelar</Text></TouchableOpacity>
              )}
            </View>
          </View>
        );
      }}
    />
  );
};

function estadoBadge(estado: string) {
  switch (estado) {
    case 'pendiente': return styles.badgePendiente;
    case 'confirmado': return styles.badgeConfirmado;
    case 'enviado': return styles.badgeEnviado;
    case 'entregado': return styles.badgeEntregado;
    case 'cancelado': return styles.badgeCancelado;
    default: return styles.badgePendiente;
  }
}
function estadoTexto(estado: string) {
  switch (estado) {
    case 'pendiente': return 'Pendiente';
    case 'confirmado': return 'Confirmado';
    case 'enviado': return 'Enviado';
    case 'entregado': return 'Entregado';
    case 'cancelado': return 'Cancelado';
    default: return estado;
  }
}
function formateaFecha(fecha: string) {
  const d = new Date(fecha);
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString().slice(0,5);
}


const styles = StyleSheet.create({
  listContainer: { padding: 16 },
  card: {
    backgroundColor: '#232b2b',
    borderRadius: 12,
    marginBottom: 18,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
    color: '#f3f3f3',
  },
  head: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  num: { fontWeight: '700', fontSize: 16, color: '#f3f3f3' },
  badgeEstado: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    fontWeight: '700',
    fontSize: 12,
    overflow: 'hidden',
    marginLeft: 8,
  },
  badgePendiente: { backgroundColor: '#ffc107', color: '#1a1a1a' },
  badgeConfirmado: { backgroundColor: '#00d17a', color: '#0d0d0d' },
  badgeEnviado: { backgroundColor: '#4dabf7', color: '#0d0d0d' },
  badgeEntregado: { backgroundColor: '#6ea8fe', color: '#0d0d0d' },
  badgeCancelado: { backgroundColor: '#ff4d4f', color: '#fff' },
  meta: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginTop: 8,
    marginBottom: 4,
  },
  metaItem: { color: '#bcbcbc', fontSize: 13, marginRight: 16, marginBottom: 2 },
  metaLabel: { color: '#f3f3f3', fontWeight: 'bold' },
  items: { borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.06)', paddingTop: 10, marginTop: 8 },
  itemsTitle: { color: '#bcbcbc', fontWeight: 'bold', marginBottom: 4 },
  itemRow: { color: '#bcbcbc', fontSize: 13, marginBottom: 2 },
  actions: { flexDirection: 'row', gap: 8, marginTop: 10 },
  btn: {
    backgroundColor: '#00ff88',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 16,
    marginRight: 8,
  },
  btnDanger: {
    backgroundColor: '#ff4d4f',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  btnText: { color: '#111', fontWeight: 'bold', fontSize: 13 },
  loading: { textAlign: 'center', marginTop: 40, fontSize: 18, color: '#888' },
  emptyCard: {
    backgroundColor: '#232b2b',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
    marginTop: 40,
  },
  emptyIcon: { fontSize: 32, marginBottom: 12, color: '#bcbcbc' },
  emptyTitle: { fontSize: 18, fontWeight: 'bold', color: '#f3f3f3', marginBottom: 8 },
  emptyText: { color: '#bcbcbc', fontSize: 14 },
});

export default OrdersScreen;
