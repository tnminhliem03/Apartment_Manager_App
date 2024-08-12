import React, { useState, useContext } from 'react';
import { View, Alert, ActivityIndicator } from 'react-native';
import { TextInput, Button, Text, Title } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import styles from './Style';
import Api, { auThApi, endpoints } from '../../Config/Api';
import MyConText from '../../Config/MyConText';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../Config/Firebase';

const Login = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [, dispatch] = useContext(MyConText);

  const login = async () => {
    setLoading(true);
    try {
      const res = await Api.post(endpoints['login'], {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': "ixf3r8dG1ckyj2LGi9UQrLhu9cSU8cNyPIDsURrS",
        'client_secret': "5EECr7BSNWYN5oaQv6h9fyAfMOFiXcaMd5TvX0DvD0nXCujsiE4SajgkjLHMpERz2VIEYUniJJQtBx6K0COIYctCSYNeMMTHquCyuXYKZEhorV1lhbMOxgYRH82VLamU"
      });

      await AsyncStorage.setItem('token', res.data.access_token);
      // Lưu thông tin người dùng đã đăng nhập vào AsyncStorage
      
      // test chat app thì mở lên, bth thì cmt lại
      await signInWithEmailAndPassword(auth, username, password);

      navigation.navigate('Main');

      dispatch({ type: "login", payload: res.data.user });
      

    } catch (ex) {
      console.error('Login error: User name hoặc mật khẩu không đúng');
      if (ex.response && ex.response.data && ex.response.data.error === 'unsupported_grant_type') {
        Alert.alert('Thông báo', 'Grant type không được hỗ trợ');
      } 
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Title style={styles.title}>Đăng Nhập</Title>
      <TextInput
        label="Tên đăng nhập"
        value={username}
        onChangeText={text => setUsername(text)}
        mode="outlined"
        style={styles.input}
        left={<TextInput.Icon name={() => <Icon name="account" />} />}
      />
      <TextInput
        label="Mật khẩu"
        value={password}
        onChangeText={text => setPassword(text)}
        mode="outlined"
        secureTextEntry
        style={styles.input}
        left={<TextInput.Icon name={() => <Icon name="lock" />} />}
      />
      {loading ? (
        <ActivityIndicator size="large" />
      ) : (
        <Button
          mode="contained"
          onPress={login}
          style={styles.button}
          icon="login"
        >
          Đăng Nhập
        </Button>
      )}
    </View>
  );
};

export default Login;
