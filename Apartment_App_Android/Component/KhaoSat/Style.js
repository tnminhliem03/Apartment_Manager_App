// KhaoSatStyles.js

import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#fff",
  },
  header: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  flatlistContent: {
    flexGrow: 1,
  },
  surveyContainer: {
    backgroundColor: "#f0f0f0",
    padding: 15,
    marginBottom: 20,
    borderRadius: 10,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  itemContainer: {
    backgroundColor: "#e0e0e0",
    padding: 15,
    marginBottom: 20,
    borderRadius: 10,
  },
  answerContainer: {
    backgroundColor: "#d0d0d0",
    padding: 10,
    marginTop: 10,
    borderRadius: 5,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 5,
  },
  content: {
    fontSize: 16,
  },
  description: {
    fontSize: 16,
    marginBottom: 5,
  },
});

export default styles;
