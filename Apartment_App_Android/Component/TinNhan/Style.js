import { StyleSheet } from 'react-native';
import { Colors } from 'react-native-paper';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  },
  messageList: {
    paddingBottom: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#ccc',
    paddingTop: 12,
  },
  input: {
    flex: 1,
    marginRight: 8,
  },
  sendButton: {
    marginBottom: 12,
  },
  messageContainer: {
    marginVertical: 8,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#e0f7fa', // Light blue color
  },
  managerMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#f5f5f5', // Light grey color
  },
  messageSender: {
    fontSize: 14,
    color: '#777',
  },
  messageText: {
    fontSize: 16,
    color: '#000',
  },
});

export default styles;
