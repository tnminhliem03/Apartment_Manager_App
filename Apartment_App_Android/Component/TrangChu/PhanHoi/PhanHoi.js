import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, Alert, KeyboardAvoidingView, Platform, TouchableWithoutFeedback, Keyboard, FlatList } from 'react-native';
import { TextInput, Button, Card, IconButton, FAB } from 'react-native-paper';
import Api, { endpoints } from '../../../Config/Api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import moment from 'moment';
import 'moment/locale/vi';
import styles from './Style';  // Import your styles here

const PhanHoi = ({ navigation }) => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [content, setContent] = useState('');
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const token = await AsyncStorage.getItem('token');
        if (!token) return;

        const response = await Api.get(endpoints['current-user'], {
          headers: { Authorization: `Bearer ${token}` },
        });
        setCurrentUser(response.data);
      } catch (error) {
        console.error('Error fetching current user:', error);
      }
    };

    fetchCurrentUser();
  }, []);

  useEffect(() => {
    const loadComplaints = async () => {
      try {
        let res = await Api.get(endpoints['complaints']);
        setComplaints(res.data.results);
      } catch (ex) {
        console.error('Error loading complaints:', ex);
      } finally {
        setLoading(false);
      }
    };
    loadComplaints();
  }, []);

  const handleCreateComplaint = async () => {
    if (!name || !content) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    const newComplaint = {
      name: name,
      content: content,
      resident: currentUser.id,
    };

    try {
      const token = await AsyncStorage.getItem('token');
      const response = await Api.post(endpoints['create-complaint'], newComplaint, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data', // Đặt đúng Content-Type
        },
      });
      setComplaints([response.data, ...complaints]);
      setName('');
      setContent('');
      Alert.alert('Success', 'Complaint created successfully');
    } catch (error) {
      console.error('Error creating complaint:', error);
      if (error.response) {
        console.error('Server response data:', error.response.data);
        console.error('Server response status:', error.response.status);
        console.error('Server response headers:', error.response.headers);
        console.error('Server response body:', error.response.data);
      } else if (error.request) {
        console.error('No response received:', error.request);
      } else {
        console.error('Error setting up the request:', error.message);
      }
      Alert.alert('Error', 'Failed to create complaint');
    }
  };

  const renderComplaint = ({ item }) => (
    <Card style={styles.complainItem}>
      <Card.Content>
        <Text style={styles.complainTime}>
          {moment(item.created_date).locale('vi').format('DD/MM/YYYY HH:mm')}
        </Text>
        <Text style={styles.complainTitle}>{item.name}</Text>
        <Text style={styles.complainContent}>{item.content}</Text>
      </Card.Content>
      <Card.Actions>
        <IconButton icon="comment-processing" size={20} onPress={() => console.log('Responding')} />
        <IconButton icon="delete" size={20} onPress={() => console.log('Deleting')} />
      </Card.Actions>
    </Card>
  );

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1 }}
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <View style={styles.container}>
          <Text style={styles.title}>Danh Sách Phản Hồi</Text>

          {loading ? (
            <ActivityIndicator animating={true} size="large" />
          ) : (
            <FlatList
              data={complaints}
              renderItem={renderComplaint}
              keyExtractor={(item, index) => item.id.toString() || index.toString()}
              ListEmptyComponent={<Text style={styles.noComplaintsText}>Không có phản hồi nào</Text>}
            />
          )}

          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              label="Name"
              value={name}
              onChangeText={setName}
              mode="outlined"
            />
            <TextInput
              style={styles.input}
              label="Content"
              value={content}
              onChangeText={setContent}
              mode="outlined"
              multiline
            />
            <Button mode="contained" onPress={handleCreateComplaint} style={styles.submitButton}>
              Submit
            </Button>
          </View>

          <FAB
            style={styles.fab}
            icon="plus"
            onPress={() => {
              setName('');
              setContent('');
            }}
          />
        </View>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
};

export default PhanHoi;
