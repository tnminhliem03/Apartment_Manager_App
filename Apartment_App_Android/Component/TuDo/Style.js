import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
  },
  itemContainer: {
    marginBottom: 10,
  },
  itemTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  itemNote: {
    fontSize: 14,
    color: '#757575',
  },
  itemStatus: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  activateButton: {
    marginRight: 10,
  },
  activatedButton: {
    marginRight: 10,
    backgroundColor: '#90ee90',  // Light green color
  },
  flatlistContent: {
    paddingBottom: 20,
  },
});

export default styles;
