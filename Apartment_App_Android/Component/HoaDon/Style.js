import { StyleSheet } from 'react-native';

export default StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f8f8',
    padding: 10,
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginVertical: 20,
  },
  receiptContainer: {
    marginVertical: 8,
    marginHorizontal: 16,
    borderRadius: 8,
    elevation: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  itemContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  content: {
    fontSize: 14,
    color: '#333',
  },
  status: {
    fontSize: 16,
    fontWeight: 'bold',
    marginVertical: 10,
  },
  momoButton: {
    flex: 1,
    marginRight: 5,
    backgroundColor: '#8e44ad', // MoMo's purple color
    color: '#fff',
  },
  vnpayButton: {
    flex: 1,
    marginLeft: 5,
    backgroundColor: '#e74c3c', // VNPay's red color
    color: '#fff',
  },
  flatlistContent: {
    paddingBottom: 20,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  qrModal: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
});
