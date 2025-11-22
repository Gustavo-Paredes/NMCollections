const ManagerNFCStack = createNativeStackNavigator();

function ManagerNFCStackScreen() {
  return (
    <ManagerNFCStack.Navigator id={undefined}>
      <ManagerNFCStack.Screen name="NFCManager" component={require('./screens/NFCManagerScreen').default} options={{ title: 'Gestión NFC' }} />
      <ManagerNFCStack.Screen name="NFCReader" component={NFCReaderScreen} options={{ title: 'Detalle Carta NFC' }} />
    </ManagerNFCStack.Navigator>
  );
}
import React from 'react';
// Si necesitas NFC, importa desde NfcManagerCompat.ts en la pantalla correspondiente
import { CatalogProvider } from './contexts/CatalogContext';
import { CartProvider } from './contexts/CartContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NavigationContainer } from '@react-navigation/native';

const linking = {
  prefixes: ['nmcollections://', 'https://zkbc59xz-8000.brs.devtunnels.ms/NFC/'],
  config: {
    screens: {
      Login: 'login',
      Main: {
        screens: {
          Inicio: {
            screens: {
              NFCReader: 'NFC/:codigo_nfc'
            }
          }
        }
      }
    }
  }
};
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import LoginScreen from './LoginScreen';
import CliHomeScreen from './screens/screen-cli/HomeScreen';
// importaciones eliminadas: Catálogo y Carrito
import CliOrdersScreen from './screens/screen-cli/OrdersScreen';
import CliSupportScreen from './screens/screen-cli/SupportScreen';
import ManagerHomeScreen from './screens/screen-manager/HomeScreen';
import ManagerOrdersScreen from './screens/screen-manager/OrdersScreen';
import ManagerGamesScreen from './screens/screen-manager/GamesScreen';
import ManagerProfileScreen from './screens/screen-manager/ProfileScreen';
import ManagerSupportScreen from './screens/screen-manager/SupportScreen';
import ManagerNotificationsScreen from './screens/screen-manager/NotificationsScreen';
import GamesScreen from './screens/GamesScreen';
import NotificationsScreen from './screens/NotificationsScreen';
import ProfileScreen from './screens/ProfileScreen';
import NFCReaderScreen from './NFCReaderScreen';
import { MaterialCommunityIcons as Icon } from '@expo/vector-icons';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const InicioStack = createNativeStackNavigator();
const NFCStack = createNativeStackNavigator();

function InicioStackScreen() {
  return (
    <InicioStack.Navigator id={undefined}>
      <InicioStack.Screen name="Home" component={CliHomeScreen} options={{ title: 'Inicio' }} />
      <InicioStack.Screen name="NFCManual" component={require('./screens/NFCManualScreen').default} options={{ title: 'Buscar carta NFC' }} />
      <InicioStack.Screen name="NFCReader" component={NFCReaderScreen} options={{ title: 'Detalle Carta NFC' }} />
    </InicioStack.Navigator>
  );
}

function NFCStackScreen() {
  return (
    <NFCStack.Navigator id={undefined}>
      <NFCStack.Screen name="NFCManual" component={require('./screens/NFCManualScreen').default} options={{ title: 'Buscar carta NFC' }} />
      <NFCStack.Screen name="NFCReader" component={NFCReaderScreen} options={{ title: 'Detalle Carta NFC' }} />
    </NFCStack.Navigator>
  );
}

function MainTabs() {
  const { token, user } = useAuth();
  const isDesigner = user?.rol?.id === 5;
  return (
    <Tab.Navigator
      id={undefined}
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ color, size }) => {
          let iconName;
          switch (route.name) {
            case 'Inicio': iconName = 'home'; break;
            case 'Catálogo': iconName = 'view-grid'; break;
            case 'Carrito': iconName = 'cart'; break;
            case 'Perfil': iconName = 'account'; break;
            case 'Pedidos': iconName = 'clipboard-list'; break;
            case 'Juegos': iconName = 'gamepad-variant'; break;
            case 'Soporte': iconName = 'chat'; break;
            case 'Notificaciones': iconName = 'bell'; break;
            default: iconName = 'circle';
          }
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#27ae60',
        tabBarInactiveTintColor: '#888',
      })}
    >
      {isDesigner ? (
        <>
          <Tab.Screen name="Inicio" component={InicioStackScreen} />
          <Tab.Screen name="NFC" component={ManagerNFCStackScreen} options={{ tabBarIcon: ({ color, size }) => <Icon name="nfc-variant" size={size} color={color} /> }} />
          <Tab.Screen name="Pedidos" component={ManagerOrdersScreen} />
          <Tab.Screen name="Juegos" component={ManagerGamesScreen} />
          <Tab.Screen name="Perfil" children={props => <ManagerProfileScreen {...props} token={token} />} />
          <Tab.Screen name="Reportes" getComponent={() => require('./screens/ReportesScreen').default} />
          <Tab.Screen name="Soporte" component={ManagerSupportScreen} />
          <Tab.Screen name="Notificaciones" component={ManagerNotificationsScreen} />
        </>
      ) : (
        <>
          <Tab.Screen name="Inicio" component={InicioStackScreen} />
          <Tab.Screen name="Escanear" component={NFCStackScreen} options={{ tabBarIcon: ({ color, size }) => <Icon name="nfc-variant" size={size} color={color} /> }} />
          <Tab.Screen name="Pedidos" children={props => <CliOrdersScreen {...props} token={token} />} />
          <Tab.Screen name="Juegos" component={GamesScreen} />
          <Tab.Screen name="Perfil" children={props => <ProfileScreen {...props} token={token} />} />
          <Tab.Screen name="Soporte" component={CliSupportScreen} />
          <Tab.Screen name="Notificaciones" component={NotificationsScreen} />
        </>
      )}
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <CatalogProvider>
        <CartProvider>
          <NavigationContainer linking={linking}>
            <Stack.Navigator initialRouteName="Login" id={undefined}>
              <Stack.Screen name="Login" options={{ headerShown: false }}>
                {props => <LoginScreen {...props} />}
              </Stack.Screen>
              <Stack.Screen name="Main" options={{ headerShown: false }}>
                {props => <MainTabs {...props} />}
              </Stack.Screen>
            </Stack.Navigator>
          </NavigationContainer>
        </CartProvider>
      </CatalogProvider>
    </AuthProvider>
  );
}
