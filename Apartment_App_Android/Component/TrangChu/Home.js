import React, { useEffect } from 'react';
import { View, ScrollView, Linking, Platform, PermissionsAndroid } from 'react-native';
import { Appbar, Card, Button, Text, Avatar } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import styles from "./Style";
import Api, { endpoints } from '../../Config/Api';
import axios from 'axios';
import { checkAppPermission, sendNotif } from '../../PushNotifications';

const Home = ({ navigation }) => {

  const openNewsLink = () => {
    const newsLink = 'https://vnexpress.net/chung-khoan-xanh-tro-lai-sau-tuan-mat-100-diem-4737288.html';
    Linking.openURL(newsLink);
  };

  useEffect(() => {
    checkAppPermission();
  }, []);

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <Appbar.Header>
        <Appbar.Content title="Xin Chào" titleStyle={styles.headerText} />
      </Appbar.Header>

      {/* Buttons */}
      <View style={styles.buttonsContainer}>
        <View style={styles.buttonRow}>
          <Button 
            mode="contained" 
            icon={() => <MaterialCommunityIcons name="format-list-bulleted" size={20} color="white" />} 
            style={styles.button} 
            onPress={() => navigation.navigate('DanhSachPhong')}
          >
            Danh Sách Phòng
          </Button>
          <Button 
            mode="contained" 
            icon={() => <MaterialCommunityIcons name="message" size={20} color="white" />} 
            style={styles.button} 
            onPress={() => navigation.navigate('QuanLyPhanHoi')}
          >
            Phản hồi
          </Button>
          <Button 
            mode="contained" 
            icon={() => <MaterialCommunityIcons name="clipboard-text" size={20} color="white" />} 
            style={styles.button} 
            onPress={() => navigation.navigate('KhaoSat')}
          >
            Khảo Sát
          </Button>
        </View>
        <View style={styles.buttonRow}>
          <Button 
            mode="contained" 
            icon={() => <MaterialCommunityIcons name="car" size={20} color="white" />} 
            style={styles.button} 
            onPress={() => navigation.navigate('TheXe')}
          >
            Thẻ Xe
          </Button>
          <Button 
            mode="contained" 
            icon={() => <MaterialCommunityIcons name="tools" size={20} color="white" />} 
            style={styles.button} 
            onPress={() => navigation.navigate('TuDo')}
          >
            Tủ Đồ
          </Button>
          <Button 
            mode="contained" 
            icon={() => <MaterialCommunityIcons name="receipt" size={20} color="white" />} 
            style={styles.button} 
            onPress={() => navigation.navigate('HoaDon')}
          >
            Hoá Đơn
          </Button>
        </View>
      </View>

      {/* Dashboard */}
      <View style={styles.dashboard}>
        {/* Available Units */}
        <Card style={styles.dashboardItem}>
          <Card.Title
            title="Liên hệ quảng cáo"
            titleStyle={styles.dashboardItemTitle}
            left={(props) => <MaterialCommunityIcons name="home-outline" size={40} style={styles.dashboardItemIcon} />}
            right={(props) => <Avatar.Text size={40} label="8" style={styles.dashboardItemValue} />}
          />
        </Card>
        
        {/* Maintenance Requests */}
        <Card style={styles.dashboardItem}>
          <Card.Title
            title="Liên hệ quảng cáo"
            titleStyle={styles.dashboardItemTitle}
            left={(props) => <MaterialCommunityIcons name="wrench-outline" size={40} style={styles.dashboardItemIcon} />}
            right={(props) => <Avatar.Text size={40} label="3" style={styles.dashboardItemValue} />}
          />
        </Card>

        {/* Upcoming Events */}
        <Card style={styles.dashboardItem}>
          <Card.Title
            title="Liên hệ quảng cáo"
            titleStyle={styles.dashboardItemTitle}
            left={(props) => <MaterialCommunityIcons name="calendar-outline" size={40} style={styles.dashboardItemIcon} />}
            right={(props) => <Avatar.Text size={40} label="2" style={styles.dashboardItemValue} />}
          />
        </Card>
      </View>

      {/* News Section */}
      <Card style={styles.newsContainer}>
        <Card.Title title="Tin Tức" titleStyle={styles.newsTitle} />
        <Card.Content>
          <Card.Cover source={require('../Assets/TinTuc1.jpg')} style={styles.newsImage} />
          <Text style={styles.newsContent}>
            VN-Index tăng hơn 15 điểm trong phiên đầu tuần khi sắc xanh chiếm ưu thế, cổ phiếu chứng khoán, ngân hàng là đầu kéo chính của thị trường
          </Text>
        </Card.Content>
        <Card.Actions>
          <Button onPress={() => sendNotif('Tân', 'Xin chào Tân')}>Xem chi tiết</Button>
        </Card.Actions>
      </Card>
    </ScrollView>
  );
};

export default Home;
