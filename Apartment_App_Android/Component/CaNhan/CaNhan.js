import React, { useEffect, useState } from 'react';
import { View, TextInput, Alert } from 'react-native';
import { Avatar, Button, Card, Title, Paragraph, ActivityIndicator } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import styles from './Style'; // Your own style file
import { auThApi, endpoints } from '../../Config/Api'; // Your API configuration

const CaNhan = ({ navigation }) => {
  const [userInfo, setUserInfo] = useState(null);
  const [editing, setEditing] = useState(false); // State to track if in edit mode
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      loadUserInfo();
    });

    return unsubscribe;
  }, [navigation]);

  const loadUserInfo = async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (!token) {
        navigation.navigate('Login');
        return;
      }

      const res = await auThApi(token).get(endpoints['current-user']);
      const { first_name, last_name, email, phone, avatar, id } = res.data;
      setUserInfo({ first_name, last_name, email, phone, avatar, id });
      setFirstName(first_name);
      setLastName(last_name);
      setEmail(email);
      setPhone(phone);
    } catch (ex) {
      console.error('Error loading user info:', ex);
      Alert.alert('Error', 'Failed to load user information.');
    }
  };

  const handleSupportPress = () => {
    // Handle support button press
  };

  const handleLogoutPress = async () => {
    try {
      await AsyncStorage.removeItem('token');
      setUserInfo(null); // Reset userInfo on logout
      navigation.navigate('Login');
    } catch (ex) {
      console.error('Error logging out:', ex);
      Alert.alert('Error', 'Failed to log out.');
    }
  };

  const handleSavePress = async () => {
    try {
      const currentToken = await AsyncStorage.getItem('token');
      const storedToken = await AsyncStorage.getItem('token');
  
      if (!currentToken || currentToken !== storedToken) {
        navigation.navigate('Login');
        return;
      }
  
      const updatedFields = {};
  
      if (firstName !== userInfo?.first_name) {
        updatedFields.first_name = firstName;
      }
      if (lastName !== userInfo?.last_name) {
        updatedFields.last_name = lastName;
      }
      if (email !== userInfo?.email) {
        updatedFields.email = email;
      }
      if (phone !== userInfo?.phone) {
        updatedFields.phone = phone;
      }
  
      if (Object.keys(updatedFields).length === 0) {
        setEditing(false);
        return;
      }
  
      const endpoint = endpoints['update-profile'](userInfo.id); // Construct endpoint with userId
  
      const formData = new FormData();
      Object.entries(updatedFields).forEach(([key, value]) => {
        formData.append(key, value);
      });
  
      const axiosInstance = axios.create({
        baseURL: 'https://tnminhliem03.pythonanywhere.com/', // Replace with your API base URL
        timeout: 10000, // Timeout set to 10 seconds
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${currentToken}`,
        },
      });
  
      const res = await axiosInstance.patch(endpoint, formData);
  
      if (res.status === 200) {
        const updatedUserInfo = { ...userInfo, ...updatedFields };
        setUserInfo(updatedUserInfo);
        setEditing(false);
      } else {
        Alert.alert('Error', 'Failed to update profile.');
      }
    } catch (ex) {
      if (axios.isAxiosError(ex)) {
        console.error('Axios Error:', ex.message);
        if (ex.response) {
          console.error('Axios Response Data:', ex.response.data);
          console.error('Axios Status:', ex.response.status);
          Alert.alert('Error', `Failed to update profile. Status: ${ex.response.status}`);
        } else {
          console.error('No response received:', ex);
          Alert.alert('Error', 'Network error. Please check your connection.');
        }
      } else {
        console.error('Unexpected Error:', ex);
        Alert.alert('Error', 'An unexpected error occurred.');
      }
    }
  };
  

  return (
    <View style={styles.container}>
      <Title style={styles.title}>Thông Tin Cá Nhân</Title>

      {userInfo === null ? (
        <ActivityIndicator />
      ) : (
        <>
          <Card style={styles.card}>
            <Card.Content style={styles.userInfoContainer}>
              <Avatar.Image size={100} source={{ uri: userInfo.avatar }} />
              <View style={{ marginLeft: 20 }}>
                {editing ? (
                  <>
                    <TextInput
                      style={styles.input}
                      value={firstName}
                      onChangeText={setFirstName}
                      placeholder="First Name"
                    />
                    <TextInput
                      style={styles.input}
                      value={lastName}
                      onChangeText={setLastName}
                      placeholder="Last Name"
                    />
                    <TextInput
                      style={styles.input}
                      value={email}
                      onChangeText={setEmail}
                      placeholder="Email"
                    />
                    <TextInput
                      style={styles.input}
                      value={phone}
                      onChangeText={setPhone}
                      placeholder="Phone"
                    />
                  </>
                ) : (
                  <>
                    <Title style={styles.label}>{userInfo?.first_name} {userInfo?.last_name}</Title>
                    <Paragraph style={styles.info}>{userInfo?.email}</Paragraph>
                    <Paragraph style={styles.info}>{userInfo?.phone}</Paragraph>
                  </>
                )}
              </View>
            </Card.Content>
          </Card>
          <View style={styles.buttonContainer}>
            {!editing ? (
              <>
                <Button mode="contained" onPress={() => setEditing(true)} style={styles.button}>
                  Chỉnh Sửa
                </Button>
                <Button mode="contained" onPress={handleSupportPress} style={styles.button}>
                  Hỗ Trợ
                </Button>
                <Button mode="outlined" onPress={handleLogoutPress} style={styles.button}>
                  Đăng Xuất
                </Button>
              </>
            ) : (
              <>
                <Button mode="contained" onPress={handleSavePress} style={styles.button}>
                  Lưu
                </Button>
                <Button mode="outlined" onPress={() => setEditing(false)} style={styles.button}>
                  Hủy
                </Button>
              </>
            )}
          </View>
        </>
      )}
    </View>
  );
};

export default CaNhan;
