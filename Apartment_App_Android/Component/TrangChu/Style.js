import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  headerContainer: {
    padding: 20,
    backgroundColor: '#6200ee',
    borderBottomLeftRadius: 15,
    borderBottomRightRadius: 15,
  },
  headerText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  headerDate: {
    fontSize: 16,
    color: 'white',
    marginVertical: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'white',
  },
  buttonsContainer: {
    padding: 10,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 5,
  },
  button: {
    flex: 1,
    marginHorizontal: 5,
    borderRadius: 10,
    overflow: 'hidden',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
  },
  buttonText: {
    color: 'white',
    marginLeft: 8,
  },
  dashboard: {
    padding: 10,
  },
  dashboardItem: {
    marginVertical: 10,
  },
  dashboardItemTitle: {
    fontSize: 18,
  },
  dashboardItemIcon: {
    marginRight: 10,
  },
  dashboardItemValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#6200ee',
  },
  newsContainer: {
    margin: 10,
  },
  newsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  newsImage: {
    height: 150,
    marginVertical: 10,
  },
  newsContent: {
    fontSize: 16,
  },
});

export default styles;
