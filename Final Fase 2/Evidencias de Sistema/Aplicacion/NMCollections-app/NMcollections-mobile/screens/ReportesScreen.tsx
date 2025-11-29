import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Dimensions } from 'react-native';
import PieChart from 'react-native-pie-chart';
import axios from 'axios';

export default function ReportesScreen() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReportes = async () => {
      try {
        const res = await axios.get('https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/pedidos/reportes/api/');
        setData(res.data);
      } catch (err) {
        setError('Error al obtener reportes');
      }
      setLoading(false);
    };
    fetchReportes();
  }, []);

  if (loading) return <ActivityIndicator size="large" color="#27ae60" style={{ marginTop: 40 }} />;
  if (error) return <Text style={styles.error}>{error}</Text>;
  if (!data) return null;

  const screenWidth = Dimensions.get('window').width;
  const isSmall = screenWidth < 500;
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Reportes 📊</Text>
      <View style={[styles.metricsRow, isSmall && { flexDirection: 'column', gap: 16 }] }>
        <View style={[styles.metricCard, styles.shadow, isSmall && { width: '100%', marginBottom: 12 }] }>
          <Text style={styles.metricLabel}>Ventas Totales</Text>
          <Text style={styles.metricValue}>${data.metrics.total_ventas.toLocaleString()}</Text>
        </View>
        <View style={[styles.metricCard, styles.shadow, isSmall && { width: '100%', marginBottom: 12 }] }>
          <Text style={styles.metricLabel}>Pedidos Totales</Text>
          <Text style={styles.metricValue}>{data.metrics.total_pedidos}</Text>
        </View>
        <View style={[styles.metricCard, styles.shadow, isSmall && { width: '100%', marginBottom: 0 }] }>
          <Text style={styles.metricLabel}>Pedidos Confirmados</Text>
          <Text style={styles.metricValue}>{data.metrics.pedidos_confirmados}</Text>
        </View>
      </View>

      <View style={styles.sectionBox}>
        <Text style={styles.sectionTitle}>Ventas por Mes</Text>
        <View style={{ alignItems: 'center', marginBottom: 16 }}>
          <PieChart
            widthAndHeight={220}
            series={data.ventas_por_mes.map((value, i) => ({ value, color: pieColors[i % pieColors.length] }))}
            cover={{ radius: 0.6, color: '#23272f' }}
            padAngle={0.01}
          />
        </View>
        <View style={styles.chartBox}>
          {data.labels_ventas_mes.map((label, i) => (
            <View key={label} style={styles.chartRow}>
              <View style={[styles.pieDot, { backgroundColor: pieColors[i % pieColors.length] }]} />
              <Text style={[styles.chartLabel, isSmall && { width: 70, fontSize: 13 }]}>{label}</Text>
              <Text style={[styles.chartValue, isSmall && { width: 60, fontSize: 13 } ]}>${data.ventas_por_mes[i].toLocaleString()}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.sectionBox}>
        <Text style={styles.sectionTitle}>Pedidos por Estado</Text>
        <View style={styles.pieBox}>
          {data.pedidos_estado_labels.map((label, i) => (
            <View key={label} style={styles.pieRow}>
              <View style={[styles.pieDot, { backgroundColor: pieColors[i % pieColors.length] }]} />
              <Text style={styles.pieLabel}>{label}</Text>
              <Text style={styles.pieValue}>{data.pedidos_estado_values[i]}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.sectionBox}>
        <Text style={styles.sectionTitle}>Ventas por Método de Pago</Text>
        <View style={styles.pieBox}>
          {data.ventas_metodo_labels.map((label, i) => (
            <View key={label} style={styles.pieRow}>
              <View style={[styles.pieDot, { backgroundColor: pieColors[i % pieColors.length] }]} />
              <Text style={styles.pieLabel}>{label}</Text>
              <Text style={styles.pieValue}>${data.ventas_metodo_values[i].toLocaleString()}</Text>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

const pieColors = ['#00ff88', '#ff4444', '#3498db', '#f1c40f', '#8e44ad', '#e67e22'];
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#23272f', padding: 18 },
  title: { fontSize: 30, fontWeight: 'bold', color: '#27ae60', marginBottom: 22, textAlign: 'center', letterSpacing: 1 },
  metricsRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 32 },
  metricCard: { backgroundColor: '#222', borderRadius: 16, padding: 20, alignItems: 'center', width: '32%' },
  metricLabel: { color: '#bbb', fontSize: 15, marginBottom: 8 },
  metricValue: { color: '#fff', fontWeight: 'bold', fontSize: 26 },
  shadow: { shadowColor: '#27ae60', shadowOpacity: 0.12, shadowRadius: 8, elevation: 4 },
  sectionBox: { backgroundColor: '#222', borderRadius: 16, padding: 18, marginBottom: 24 },
  sectionTitle: { color: '#27ae60', fontWeight: 'bold', fontSize: 19, marginBottom: 14, letterSpacing: 0.5 },
  chartBox: { marginBottom: 8 },
  chartRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  chartLabel: { color: '#bbb', fontSize: 14, width: 80 },
  barBg: { backgroundColor: '#333', borderRadius: 8, height: 16, width: 180, marginHorizontal: 8, overflow: 'hidden' },
  bar: { backgroundColor: '#27ae60', height: 16, borderRadius: 8 },
  chartValue: { color: '#fff', fontWeight: 'bold', fontSize: 15, marginLeft: 8, width: 80, textAlign: 'right' },
  pieBox: { marginTop: 8 },
  pieRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  pieDot: { width: 16, height: 16, borderRadius: 8, marginRight: 10 },
  pieLabel: { color: '#bbb', fontSize: 15, flex: 1 },
  pieValue: { color: '#fff', fontWeight: 'bold', fontSize: 15, marginLeft: 8 },
  error: { color: '#e74c3c', fontSize: 18, textAlign: 'center', marginTop: 40 },
});
