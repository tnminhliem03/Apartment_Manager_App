import React, { useEffect, useState } from "react";
import { FlatList, View, Alert, Modal, Linking } from "react-native";
import { ActivityIndicator, Text, Button, Card } from "react-native-paper";
import QRCode from 'react-native-qrcode-svg';
import Api, { endpoints } from "../../Config/Api"; // Adjust import path as per your project structure
import styles from "./Style"; // Adjust import path as per your project structure
import AsyncStorage from '@react-native-async-storage/async-storage';
import { checkAppPermission, sendNotif } from '../../PushNotifications';

const Payments = () => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMorePayments, setLoadingMorePayments] = useState(false);
  const [nextPaymentPage, setNextPaymentPage] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [momoQRCode, setMomoQRCode] = useState(null);
  const [vnpayQRCode, setVnpayQRCode] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalContent, setModalContent] = useState(null);
  const [paymentDetails, setPaymentDetails] = useState(null);

  useEffect(() => {
    checkAppPermission();
  }, []);

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
    const fetchData = async () => {
      try {
        const paymentRes = await Api.get(endpoints.payments);
        if (paymentRes.data && Array.isArray(paymentRes.data.results)) {
          setPayments(paymentRes.data.results);
          setNextPaymentPage(paymentRes.data.next);
        } else {
          console.error('Unexpected API response format for payments');
        }
        setLoading(false);
      } catch (ex) {
        console.error('Error fetching payments:', ex);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (currentUser) {
      const fetchUserPayments = async () => {
        setLoading(true);
        try {
          const paymentRes = await Api.get(endpoints.payments);
          if (paymentRes.data && Array.isArray(paymentRes.data.results)) {
            const userPayments = paymentRes.data.results.filter(
              payment => payment.resident === currentUser.id
            );
            setPayments(userPayments);
            setNextPaymentPage(paymentRes.data.next);
          } else {
            console.error('Unexpected API response format for payments');
          }
        } catch (error) {
          console.error('Error fetching user payments:', error);
        } finally {
          setLoading(false);
        }
      };

      fetchUserPayments();
    }
  }, [currentUser]);

  const loadMoreData = async () => {
    if (nextPaymentPage && !loadingMorePayments) {
      try {
        setLoadingMorePayments(true);
        const res = await Api.get(nextPaymentPage);
        if (res.data && Array.isArray(res.data.results)) {
          const filteredPayments = res.data.results.filter(payment => payment.resident === currentUser.id);
          setPayments([...payments, ...filteredPayments]);
          setNextPaymentPage(res.data.next);
        } else {
          console.error('Unexpected API response format for loading more payments');
        }
        setLoadingMorePayments(false);
      } catch (ex) {
        console.error("Error loading more payments:", ex);
        setLoadingMorePayments(false);
      }
    }
  };

  const handleMomoPayment = async (payment) => {
    // Check if the payment belongs to the current user
    if (payment.resident !== currentUser.id) {
      Alert.alert('Error', 'You are not authorized to view this payment.');
      return;
    }

    const token = await AsyncStorage.getItem('token');
      if (!token) {
        return;
      }

    const data = {
      payment: payment.id
    };

    try {
      const momoLinks = await Api.post(endpoints['momo'], data, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const payUrl = momoLinks.data.payUrl;
      console.log('Pay URL:', payUrl);
      Linking.openURL(payUrl);
    } catch(error) {
      console.error('Error when making VNP payment:', error);
    }
  };

  const handleVnpayPayment = async (payment) => {
    // Check if the payment belongs to the current user
    if (payment.resident !== currentUser.id) {
      Alert.alert('Error', 'You are not authorized to view this payment.');
      return;
    }

    const token = await AsyncStorage.getItem('token');
      if (!token) {
        return;
      }

    const data = {
      payment: payment.id
    };

    try {
      const vnpApi = await Api.post(endpoints['links'], data, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const paymentUrl = vnpApi.data.payment_url;
      console.log('Pay URL:', paymentUrl);
      Linking.openURL(paymentUrl);
    } catch(error) {
      console.error('Error when making VNP payment:', error);
    }
  };


  const closeModal = () => {
    setModalVisible(false);
    setModalContent(null);
    setMomoQRCode(null);
    setVnpayQRCode(null);
  };

  const simulateSuccessfulPayment = () => {
    // Update the payment status to active (paid)
    const updatedPayments = payments.map(payment => 
      payment.id === paymentDetails.id ? { ...payment, active: false } : payment
    );
    setPayments(updatedPayments);

    // Show a success alert
    Alert.alert('Payment Successful', `You have successfully paid ${paymentDetails.amount} VND for ${paymentDetails.name}`);

    // Close the modal
    closeModal();
  };

  const renderPaymentItem = ({ item }) => (
    <Card style={styles.receiptContainer}>
      <Card.Title title={item.name || 'No name provided'} />
      <Card.Content>
        <View style={styles.itemContainer}>
          <Text style={styles.subtitle}>Ngày tạo:</Text>
          <Text style={styles.content}>{new Date(item.created_date).toLocaleDateString() || 'No date provided'}</Text>
        </View>
        <View style={styles.itemContainer}>
          <Text style={styles.subtitle}>Số tiền:</Text>
          <Text style={styles.content}>{item.amount || 'No amount provided'} VND</Text>
        </View>
        <Text style={[styles.status, { color: item.active ? '#f44336' : '#4caf50' }]}>
          {item.active ? 'Chưa thanh toán' : 'Đã thanh toán'}
        </Text>
      </Card.Content>
      <Card.Actions>
        <Button 
          mode="contained" 
          onPress={() => handleMomoPayment(item)} 
          style={styles.momoButton} 
          buttonColor="#8e44ad" 
          disabled={!item.active}
        >
          Momo
        </Button>
        <Button 
          mode="contained" 
          onPress={() => handleVnpayPayment(item)} 
          style={styles.vnpayButton} 
          buttonColor="#e74c3c" 
          disabled={!item.active}
        >
          VNpay
        </Button>
      </Card.Actions>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Danh sách thanh toán</Text>
      {loading ? (
        <ActivityIndicator animating={true} />
      ) : (
        <FlatList
          data={payments}
          renderItem={renderPaymentItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.flatlistContent}
          onEndReached={loadMoreData}
          onEndReachedThreshold={0.1}
          ListFooterComponent={loadingMorePayments && <ActivityIndicator animating={true} />}
        />
      )}

      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={closeModal}
      >
        <View style={styles.modalContainer}>
          <View style={styles.qrModal}>
            {modalContent === 'momo' && momoQRCode ? (
              <QRCode value={momoQRCode} size={250} />
            ) : modalContent === 'vnpay' && vnpayQRCode ? (
              <QRCode value={vnpayQRCode} size={250} />
            ) : (
              <ActivityIndicator size="large" />
            )}
            <Button onPress={simulateSuccessfulPayment}>Simulate Scan</Button>
            <Button onPress={closeModal}>Close</Button>
          </View>
        </View>
      </Modal>
    </View>
  );
};

export default Payments;
