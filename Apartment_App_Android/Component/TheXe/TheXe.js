import React, { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator, Alert, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Provider as PaperProvider, Card, List } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Api, { auThApi, endpoints } from '../../Config/Api';

const TheXe = () => {
  const [loading, setLoading] = useState(true);
  const [registeredCards, setRegisteredCards] = useState([]);
  const [name, setName] = useState('');
  const [nameRegister, setNameRegister] = useState('');
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [typeVehicle, setTypeVehicle] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const [loadingMoreCards, setLoadingMoreCards] = useState(false);
  const [nextPage, setNextPage] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      setLoading(true);
      try {
        const token = await AsyncStorage.getItem('token');
        if (!token) {
          return;
        }

        const response = await auThApi(token).get(endpoints['current-user']);
        setCurrentUser(response.data);
      } catch (error) {
        console.error('Error fetching user data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  useEffect(() => {
    if (currentUser) {
      const fetchRegisteredCards = async () => {
        setLoading(true);
        try {
          const token = await AsyncStorage.getItem('token');
          if (!token) {
            return;
          }

          const cardResponse = await Api.get(endpoints.security_cards);
          if (Array.isArray(cardResponse.data.results)) {
            const userCards = cardResponse.data.results.filter(card => card.resident === currentUser.id);
            setRegisteredCards(userCards);
            setNextPage(cardResponse.data.next); // Assuming 'next' is the pagination link
          } else {
            console.error('Unexpected API response format for security cards');
          }
        } catch (error) {
          console.error('Error fetching registered cards:', error);
        } finally {
          setLoading(false);
        }
      };

      fetchRegisteredCards();
    }
  }, [currentUser]);

  const loadMoreCards = async () => {
    if (nextPage && !loadingMoreCards) {
      setLoadingMoreCards(true);
      try {
        const token = await AsyncStorage.getItem('token');
        if (!token) {
          return;
        }

        // Fetch data from the nextPage URL
        const response = await Api.get(nextPage, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (Array.isArray(response.data.results)) {
          // Filter and append only cards that belong to the current user
          const moreCards = response.data.results.filter(card => card.resident === currentUser.id);

          // Update registeredCards state with the new set of cards
          setRegisteredCards(prevCards => [...prevCards, ...moreCards]);
          
          // Update nextPage URL for subsequent pagination
          setNextPage(response.data.next);
        } else {
          console.error('Unexpected API response format for security cards');
        }

      } catch (error) {
        console.error('Error fetching more cards:', error);
      } finally {
        setLoadingMoreCards(false);
      }
    }
  };

  const handleRegister = async () => {
    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('token');
      if (!token) {
        return;
      }

      const newCard = {
        name: name,
        name_register: nameRegister,
        vehicle_number: vehicleNumber,
        type_vehicle: typeVehicle,
        resident: currentUser.id
      };

      const response = await Api.post(endpoints['add-sc'], newCard, {
        headers: { Authorization: `Bearer ${token}` },
        'Content-Type': 'multipart/form-data',
      });

      // Update registeredCards state with new card appended
      setRegisteredCards(prevCards => [...prevCards, response.data]);
      Alert.alert('Success', 'Security card registration successful.');
      
      // Clear input fields after successful registration
      setName('');
      setNameRegister('');
      setVehicleNumber('');
      setTypeVehicle('');

    } catch (success) {
      Alert.alert('Success', 'Bạn đã đăng ký thành công');
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

  const renderItem = ({ item }) => (
    <Card style={{ marginBottom: 10 }}>
      <Card.Content>
        <Text>Name: {item.name}</Text>
        <Text>Name Registered: {item.name_register}</Text>
        <Text>Vehicle Number: {item.vehicle_number}</Text>
        <Text>Type of Vehicle: {item.type_vehicle}</Text>
      </Card.Content>
    </Card>
  );

  return (
    <PaperProvider>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : -500} // Adjust this value as needed
      >
        <View style={{ flex: 1, padding: 20 }}>
          {loading ? (
            <ActivityIndicator />
          ) : (
            <FlatList
              data={registeredCards}
              renderItem={renderItem}
              keyExtractor={(item) => item.id.toString()}
              onEndReached={loadMoreCards}
              onEndReachedThreshold={0.1}
              ListFooterComponent={loadingMoreCards ? <ActivityIndicator animating={true} /> : null}
            />
          )}

          <Text>Đăng ký thẻ xe cho người thân:</Text>
          <TextInput
            label="Họ và tên"
            value={name}
            onChangeText={setName}
            style={{ marginBottom: 10 }}
          />
          <TextInput
            label="Tên đăng ký"
            value={nameRegister}
            onChangeText={setNameRegister}
            style={{ marginBottom: 10 }}
          />
          <TextInput
            label="Biển số xe"
            value={vehicleNumber}
            onChangeText={setVehicleNumber}
            style={{ marginBottom: 10 }}
          />
          <TextInput
            label="Loại xe"
            value={typeVehicle}
            onChangeText={setTypeVehicle}
            style={{ marginBottom: 10 }}
          />
          <Button
            mode="contained"
            onPress={handleRegister}
            disabled={loading}
            style={{ marginTop: 10 }}
          >
            Đăng ký
          </Button>
        </View>
      </KeyboardAvoidingView>
    </PaperProvider>
  );
};

export default TheXe;
