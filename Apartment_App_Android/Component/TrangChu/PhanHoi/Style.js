import { StyleSheet } from 'react-native';

export default StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginVertical: 20,
  },
  inputContainer: {
    marginBottom: 20,
  },
  input: {
    marginBottom: 16,
    fontSize: 18,
  },
  submitButton: {
    alignSelf: 'center',
    backgroundColor: '#6200ee',
    padding: 10,
  },
  noComplaintsText: {
    textAlign: 'center',
    marginTop: 20,
    fontSize: 18,
    color: '#757575',
  },
  complainItem: {
    marginBottom: 20,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    elevation: 2,
    padding: 10,
  },
  complainTime: {
    fontSize: 16,
    color: 'gray',
  },
  complainTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginVertical: 6,
  },
  complainContent: {
    fontSize: 18,
    color: '#333333',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#6200ee',
  },
});
