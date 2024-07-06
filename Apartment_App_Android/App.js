import * as React from 'react';
import { NavigationContainer, useFocusEffect } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Text } from 'react-native';
import Login from './Component/Login/Login';
import Home from './Component/TrangChu/Home';
import TinNhan from './Component/TinNhan/TinNhan';
import ThongBao from './Component/ThongBao/ThongBao';
import CaNhan from './Component/CaNhan/CaNhan';
import Phong from './Component/TrangChu/Phong/Phong';
import PhanHoi from './Component/TrangChu/PhanHoi/PhanHoi';
import MyConText from './Config/MyConText';
import KhaoSat from './Component/KhaoSat/KhaoSat';
import MyUserReducer from './reducer/reducers';
import HoaDon from './Component/HoaDon/HoaDon';
import TuDo from './Component/TuDo/TuDo';
import TheXe from './Component/TheXe/TheXe';
import registerNNPushToken from 'native-notify';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const TabNavigator = ({navigation}) => {
  const [user, dispatch] = React.useContext(MyConText);

  registerNNPushToken(22002, "lB3kiVHaDJJRC4NROiKcd5");


  useFocusEffect(
    React.useCallback(() => {
      if (user === null) {
        // Redirect to login screen
        navigation.navigate('Login');
      } else {
        navigation.navigate('Main');
      }
    }, [user, navigation])
  );

  return (
    <MyConText.Provider value={[user, dispatch]}>
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: 'blue',
          tabBarInactiveTintColor: 'gray',
          tabBarStyle: { backgroundColor: '#fff', display: 'flex' }
        }}
      >
        <Tab.Screen 
          name="Trang Chủ" 
          component={Home} 
          options={{
            tabBarLabel: 'Trang chủ',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color: color, fontSize: size }}>🏠</Text>
            ),
          }} 
        />
        <Tab.Screen 
          name="Tin Nhắn" 
          component={TinNhan} 
          options={{
            tabBarLabel: 'Tin nhắn',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color: color, fontSize: size }}>✉️</Text>
            ),
          }} 
        />
        <Tab.Screen 
          name="ThongBao" 
          component={ThongBao} 
          options={{
            tabBarLabel: 'Thông báo',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color: color, fontSize: size }}>🔔</Text>
            ),
          }} 
        />
        {user !== null ? (
          <Tab.Screen 
            name="Cá Nhân" 
            component={CaNhan} 
            options={{
              tabBarLabel: 'Cá Nhân',
              tabBarIcon: ({ color, size }) => (
                <Text style={{ color: color, fontSize: size }}>👤</Text>
              ),
            }} 
          />
        ) : (
          <Tab.Screen 
            name="Đăng Nhập" 
            component={Login} 
            options={{
              tabBarLabel: 'Đăng Nhập',
              tabBarIcon: ({ color, size }) => (
                <Text style={{ color: color, fontSize: size }}>🔑</Text>
              ),
            }} 
          />
        )}
      </Tab.Navigator>
    </MyConText.Provider>
  );
};

const App = () => {
  const [user, dispatch] = React.useReducer(MyUserReducer, null);
  
  return (
    <MyConText.Provider value={[user, dispatch]}>
      <SafeAreaProvider>
        <NavigationContainer>
          <Stack.Navigator>
            <Stack.Screen name="Main" component={TabNavigator} options={{ headerShown: false }} />
            <Stack.Screen name="DanhSachPhong" component={Phong} />
            <Stack.Screen name="QuanLyPhanHoi" component={PhanHoi} />
            <Stack.Screen name="CaNhan" component={CaNhan} />
            <Stack.Screen name="Login" component={Login} />
            <Stack.Screen name="KhaoSat" component={KhaoSat} />
            <Stack.Screen name="HoaDon" component={HoaDon} />
            <Stack.Screen name="TuDo" component={TuDo} />
            <Stack.Screen name="Home" component={Home} />
            <Stack.Screen name="TheXe" component={TheXe} />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </MyConText.Provider>
  );
};

export default App;
