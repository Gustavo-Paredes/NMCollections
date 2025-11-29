import React, { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Dimensions } from 'react-native';
import axios from 'axios';
import { MaterialCommunityIcons, FontAwesome5, Ionicons } from '@expo/vector-icons';

interface Section {
  name: string;
  icon: JSX.Element;
  description: string;
  screen: string;
}

const sections: Section[] = [
  {
    name: 'Catálogo',
    icon: <MaterialCommunityIcons name="package-variant" size={40} color="#27ae60" />,
    description: 'Gestionar catálogo',
    screen: 'Catálogo',
  },
  {
    name: 'Pedidos',
    icon: <MaterialCommunityIcons name="clipboard-list" size={40} color="#27ae60" />,
    description: 'Ver todos los pedidos',
    screen: 'Pedidos',
  },

  {
    name: 'Juegos',
    icon: <Ionicons name="game-controller" size={40} color="#27ae60" />,
    description: 'Historial y logros',
    screen: 'Juegos',
  },
  {
    name: 'Perfil',
    icon: <MaterialCommunityIcons name="account-circle" size={40} color="#27ae60" />,
    description: 'Actualizar información personal',
    screen: 'Perfil',
  },
  {
    name: 'Soporte',
    icon: <MaterialCommunityIcons name="chat-question" size={40} color="#27ae60" />,
    description: 'Chatea con soporte',
    screen: 'Soporte',
  },
  {
    name: 'Notificaciones',
    icon: <Ionicons name="notifications" size={40} color="#27ae60" />,
    description: 'Avisos y promociones',
    screen: 'Notificaciones',
  },
];

interface HomeScreenProps {
  navigation: any;
  token?: string | null;
}

export default function HomeScreen({ navigation }: HomeScreenProps) {
  const { token } = useAuth();
  const [catalogo, setCatalogo] = useState([]);
  const [activeIdx, setActiveIdx] = useState(0);
  useEffect(() => {
    const fetchCatalogo = async () => {
      try {
        const res = await axios.get('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/productos/', {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        setCatalogo(res.data.results || res.data || []);
      } catch {
        setCatalogo([]);
      }
    };
    fetchCatalogo();
  }, [token]);

  const { width } = Dimensions.get('window');

  return (
    <ScrollView style={styles.container}>
      <View style={styles.heroBox}>
        {/* Reemplaza por tu logo real si tienes */}
        <Image source={require('../../assets/icon.png')} style={styles.logo} />
        <Text style={styles.heroTitle}>Bienvenido a NM Collections</Text>
        <Text style={styles.heroDesc}>Descubre nuestras creaciones y colaboraciones exclusivas. Para comprar, visita la web oficial.</Text>
      </View>

      {/* Publicaciones de Instagram */}
      <View style={styles.sectionBox}>
        <Text style={styles.sectionTitle}>Nuestras Creaciones</Text>
        <View style={styles.instagramEmbed}>
          <Text style={styles.igLabel}>Publicación destacada</Text>
          <View style={{ alignItems: 'center', marginBottom: 16 }}>
            <Image source={require('../../assets/instagram/image.png')} style={styles.igImg} />
            <TouchableOpacity style={styles.igBtn} onPress={() => {
              // Abrir Instagram en navegador/app
              import('react-native').then(({ Linking }) => {
                Linking.openURL('https://www.instagram.com/p/DPDAw5GjALd/');
              });
            }}>
              <Text style={styles.igBtnText}>Ver en Instagram</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.igLabel}>Colaboraciones Oficiales</Text>
          <View style={{ alignItems: 'center', marginBottom: 16 }}>
            <Image source={require('../../assets/instagram/image2.png')} style={styles.igImg} />
            <TouchableOpacity style={styles.igBtn} onPress={() => {
              import('react-native').then(({ Linking }) => {
                Linking.openURL('https://www.instagram.com/reel/DOMyK2CjFrg/');
              });
            }}>
              <Text style={styles.igBtnText}>Ver en Instagram</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>

      <View style={styles.sectionBox}>
        <Text style={styles.sectionTitle}>Catálogo Destacado</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.carousel}>
          {catalogo.map((prod, idx) => (
            <TouchableOpacity key={prod.id} style={[styles.card, activeIdx === idx && styles.cardActive]} onPress={() => setActiveIdx(idx)}>
              <Image source={{ uri: `https://zkbc59xz-8000.brs.devtunnels.ms${prod.imagen}` }} style={styles.cardImg} />
              <Text style={styles.cardTitle}>{prod.nombre}</Text>
              <Text style={styles.cardDesc}>{prod.descripcion}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
        <Text style={styles.infoText}>¿Te gustó algo? Compra solo en la web oficial.</Text>
      </View>
      <View style={styles.sectionBox}>
        <Text style={styles.sectionTitle}>Colaboraciones Oficiales</Text>
        <Text style={styles.collabText}>Audax Italiano, Colo Colo, Palestino y más confían en NM Collections para sus productos personalizados.</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#23272f' },
  heroBox: { alignItems: 'center', paddingVertical: 32, backgroundColor: '#222', marginBottom: 18 },
  logo: { width: 90, height: 90, marginBottom: 12, borderRadius: 20 },
  heroTitle: { fontSize: 26, fontWeight: 'bold', color: '#27ae60', marginBottom: 8 },
  heroDesc: { color: '#bbb', fontSize: 16, textAlign: 'center', marginHorizontal: 18 },
  sectionBox: { backgroundColor: '#222', borderRadius: 16, padding: 18, marginBottom: 24 },
  sectionTitle: { color: '#27ae60', fontWeight: 'bold', fontSize: 19, marginBottom: 14, letterSpacing: 0.5 },
  instagramEmbed: { marginBottom: 18, backgroundColor: '#222', borderRadius: 14, padding: 10 },
  igLabel: { color: '#27ae60', fontWeight: 'bold', fontSize: 16, marginBottom: 8, textAlign: 'center' },
  carousel: { flexDirection: 'row', marginBottom: 10 },
  igImg: { width: 320, height: 320, borderRadius: 12, marginBottom: 8, backgroundColor: '#222' },
  igBtn: { backgroundColor: '#27ae60', borderRadius: 10, paddingVertical: 8, paddingHorizontal: 18, marginTop: 4 },
  igBtnText: { color: '#fff', fontWeight: 'bold', fontSize: 15 },
  card: { width: 220, marginRight: 18, backgroundColor: '#333', borderRadius: 14, padding: 12, alignItems: 'center', shadowColor: '#27ae60', shadowOpacity: 0.10, shadowRadius: 8, elevation: 4 },
  cardActive: { borderWidth: 2, borderColor: '#27ae60' },
  cardImg: { width: '100%', height: 120, borderRadius: 10, marginBottom: 10, backgroundColor: '#222' },
  cardTitle: { color: '#fff', fontWeight: 'bold', fontSize: 17, marginBottom: 4 },
  cardDesc: { color: '#bbb', fontSize: 14, textAlign: 'center' },
  infoText: { color: '#e67e22', fontWeight: 'bold', fontSize: 15, textAlign: 'center', marginTop: 10 },
  collabText: { color: '#fff', fontSize: 15, textAlign: 'center' },
});
