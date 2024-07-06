import React, { useState } from 'react';
import { View, FlatList } from 'react-native';
import { Text, TextInput, IconButton, Card, Avatar, useTheme } from 'react-native-paper';
import styles from './Style';

const TinNhan = () => {
  const [newMessage, setNewMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const quanLyChungCu = 'Người quản lý chung cư'; // Tên người quản lý chung cư
  const { colors } = useTheme();

  const sendMessage = () => {
    if (newMessage.trim() !== '') {
      const message = {
        content: newMessage,
        sender: 'Bạn',
      };
      setMessages([...messages, message]);
      setNewMessage('');
    }
  };

  const renderMessageItem = ({ item }) => (
    <Card style={[styles.messageContainer, item.sender === 'Bạn' ? styles.userMessage : styles.managerMessage]}>
      <Card.Title
        title={item.sender}
        titleStyle={styles.messageSender}
        left={(props) => <Avatar.Icon {...props} icon={item.sender === 'Bạn' ? "account" : "account-outline"} />}
      />
      <Card.Content>
        <Text style={styles.messageText}>{item.content}</Text>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={messages}
        renderItem={renderMessageItem}
        keyExtractor={(item, index) => index.toString()}
        contentContainerStyle={styles.messageList}
      />
      <View style={styles.inputContainer}>
        <TextInput
          mode="outlined"
          style={styles.input}
          value={newMessage}
          onChangeText={setNewMessage}
          placeholder={`Nhập tin nhắn cho ${quanLyChungCu}...`}
          placeholderTextColor="#777"
        />
        <IconButton
          icon="send"
          color={colors.primary}
          size={30}
          onPress={sendMessage}
          style={styles.sendButton}
        />
      </View>
    </View>
  );
};

export default TinNhan;
