import React, { useEffect, useState, useCallback } from "react";
import { FlatList, TouchableOpacity, View, ActivityIndicator, Alert } from "react-native";
import { Card, Title, Paragraph, Button } from "react-native-paper";
import { FontAwesome } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import Api, { auThApi, endpoints } from "../../Config/Api";
import styles from "./Style";

const TuDo = ({ navigation }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);

  const loadUserInfo = async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (!token) {
        navigation.navigate('Login');
        return;
      }

      let res = await auThApi(token).get(endpoints['current-user']);
      setUserInfo(res.data);
    } catch (ex) {
      console.error(ex);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadUserInfo();
    }, [])
  );

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await Api.get(endpoints.packages);
        setItems(response.data.results);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching items:", error);
        setLoading(false);
      }
    };

    if (userInfo) {
      fetchItems();
    }
  }, [userInfo]);

  const filteredItems = items.filter(item => item.resident === userInfo?.id);

  const handleActivateItem = async (itemId) => {
    try {
      const response = await Api.patch(`${endpoints.packages}/${itemId}/activate`);
      const updatedItem = response.data;
      
      const updatedItems = items.map(item => 
        item.id === itemId ? updatedItem : item
      );
      
      setItems(updatedItems);
      Alert.alert('Success', 'Item activated successfully');
    } catch (error) {
      console.error("Error activating item:", error);
      Alert.alert('Error', 'Failed to activate item');
    }
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity onPress={() => {/* Handle item press */}}>
      <Card style={styles.itemContainer}>
        <Card.Cover source={{ uri: item.image }} />
        <Card.Content>
          <Title style={styles.itemTitle}>{item.name}</Title>
          <Paragraph style={styles.itemNote}>{item.note}</Paragraph>
          <Paragraph style={[styles.itemStatus, { color: item.active ? 'red' : 'green' }]}>
            {item.active ? 'Chưa Lấy' : 'Đã Lấy'}
          </Paragraph>
        </Card.Content>
        <Card.Actions>
          {item.active ? (
            <Button 
              mode="contained" 
              onPress={() => handleActivateItem(item.id)} 
              style={styles.activateButton}
              icon="check-circle-outline"
              color="#6200ee"
            >
              Activate
            </Button>
          ) : (
            <Button 
              mode="contained" 
              disabled={true}
              icon="check-circle"
              color="white"
              style={styles.activatedButton}
            >
              Activated
            </Button>
          )}
          <FontAwesome name="chevron-right" size={24} color="#757575" />
        </Card.Actions>
      </Card>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator animating={true} />
      ) : (
        <FlatList
          data={filteredItems}
          renderItem={renderItem}
          keyExtractor={item => item.id.toString()}
          contentContainerStyle={styles.flatlistContent}
        />
      )}
    </View>
  );
};

export default TuDo;
