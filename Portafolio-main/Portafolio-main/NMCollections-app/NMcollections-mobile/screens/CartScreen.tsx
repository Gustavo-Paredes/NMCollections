import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { FontAwesome5 } from '@expo/vector-icons';
import { useCart } from '../contexts/CartContext';

export default function CartScreen() {
  const { cart, removeFromCart, clearCart, increment, decrement } = useCart();
  const total = cart.reduce((sum, item) => sum + ((item.product.precio_base || 0) * item.quantity), 0);
  return (
    <ScrollView style={styles.bg}>
      <Text style={styles.title}>Carrito</Text>
      {cart.length === 0 ? (
        <Text style={styles.desc}>El carrito está vacío.</Text>
      ) : (
        <>
          {cart.map((item, idx) => (
            <View key={idx} style={styles.card}>
              <Text style={styles.productName}>{item.product.nombre}</Text>
              <Text style={styles.price}>${item.product.precio_base}</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', marginVertical: 8 }}>
                <TouchableOpacity style={styles.qtyBtn} onPress={() => decrement(item.product.id)}>
                  <Text style={styles.qtyBtnText}>-</Text>
                </TouchableOpacity>
                <Text style={styles.qtyText}>{item.quantity}</Text>
                <TouchableOpacity style={styles.qtyBtn} onPress={() => increment(item.product.id)}>
                  <Text style={styles.qtyBtnText}>+</Text>
                </TouchableOpacity>
              </View>
              <TouchableOpacity style={styles.btn} onPress={() => removeFromCart(item.product.id)}>
                <Text style={styles.btnText}>Eliminar</Text>
              </TouchableOpacity>
            </View>
          ))}
          <View style={styles.totalWrap}>
            <Text style={styles.totalText}>Total: ${total}</Text>
            <TouchableOpacity style={styles.btn} onPress={clearCart}>
              <Text style={styles.btnText}>Vaciar carrito</Text>
            </TouchableOpacity>
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1, backgroundColor: '#474d54', paddingHorizontal: 8 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginTop: 40, marginBottom: 18, textAlign: 'center' },
  desc: { fontSize: 15, color: '#bbb', marginBottom: 18, textAlign: 'center' },
  card: { backgroundColor: '#222', borderRadius: 18, borderWidth: 2, borderColor: '#27ae60', width: '97%', margin: '1.5%', padding: 14, alignItems: 'center', shadowColor: '#27ae60', shadowOpacity: 0.15, shadowRadius: 8, elevation: 4 },
  productName: { fontSize: 16, fontWeight: 'bold', color: '#fff', marginBottom: 2, textAlign: 'center' },
  price: { fontSize: 15, color: '#27ae60', fontWeight: 'bold', marginBottom: 8 },
  btn: { backgroundColor: '#27ae60', borderRadius: 14, paddingVertical: 8, paddingHorizontal: 28, marginTop: 8 },
  btnText: { color: '#fff', fontWeight: 'bold', fontSize: 17 },
  qtyBtn: { backgroundColor: '#27ae60', borderRadius: 8, padding: 6, marginHorizontal: 8 },
  qtyBtnText: { color: '#fff', fontWeight: 'bold', fontSize: 18 },
  qtyText: { color: '#fff', fontWeight: 'bold', fontSize: 16, minWidth: 24, textAlign: 'center' },
  totalWrap: { marginTop: 20, alignItems: 'center' },
  totalText: { fontSize: 18, fontWeight: 'bold', color: '#fff', marginBottom: 10 },
});
