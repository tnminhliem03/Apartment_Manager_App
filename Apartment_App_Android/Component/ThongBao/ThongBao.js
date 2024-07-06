import React, { useEffect, useState } from "react";
import { View, FlatList } from "react-native";
import { Text, Card, List, IconButton, ActivityIndicator, useTheme } from "react-native-paper";
import Api, { endpoints } from "../../Config/Api";
import styles from "./Style";

const ThongBao = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMoreNotifications, setLoadingMoreNotifications] = useState(false);
  const [nextNotificationPage, setNextNotificationPage] = useState(null);
  const [expanded, setExpanded] = useState(null);
  const { colors } = useTheme();

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const notificationRes = await Api.get(endpoints.notifications);
        setNotifications(notificationRes.data.results);
        setNextNotificationPage(notificationRes.data.next);
        setLoading(false);
      } catch (ex) {
        console.error("Error fetching notifications:", ex);
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  const loadMoreData = async () => {
    if (nextNotificationPage && !loadingMoreNotifications) {
      try {
        setLoadingMoreNotifications(true);
        const res = await Api.get(nextNotificationPage);
        setNotifications([...notifications, ...res.data.results]);
        setNextNotificationPage(res.data.next);
      } catch (ex) {
        console.error("Error loading more notifications:", ex);
      } finally {
        setLoadingMoreNotifications(false);
      }
    }
  };

  const toggleExpand = (id) => {
    setExpanded(expanded === id ? null : id);
  };

  const iconList = [
    'flash-outline',
    'tools',
    'calendar-check-outline',
    'shield-check-outline',
    'broom',
    'heart-outline',
    'storefront-outline',
    'fire-extinguisher',
    'sprout-outline',
    'account-edit-outline',
    'bell-outline'
  ];

  const renderIcon = (index) => {
    const iconIndex = index % iconList.length; // Cycle through the icon list
    return iconList[iconIndex];
  };

  const renderItem = ({ item, index }) => (
    <Card style={styles.itemContainer}>
      <List.Item
        title={item.name}
        left={props => <List.Icon {...props} icon={renderIcon(index)} />}
        right={props => (
          <IconButton
            {...props}
            icon={expanded === item.id ? "chevron-up" : "chevron-down"}
            onPress={() => toggleExpand(item.id)}
          />
        )}
      />
      {expanded === item.id && (
        <Card.Content>
          <Text>{item.content}</Text>
        </Card.Content>
      )}
    </Card>
  );

  return (
    <View style={styles.container}>
      <Text style={[styles.title, { color: colors.primary }]}>Thông Báo Từ Quản Lý Chung Cư</Text>
      {loading ? (
        <ActivityIndicator animating={true} />
      ) : (
        <FlatList
          data={notifications}
          renderItem={renderItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
          onEndReached={loadMoreData}
          onEndReachedThreshold={0.1}
          ListFooterComponent={loadingMoreNotifications && <ActivityIndicator animating={true} />}
        />
      )}
    </View>
  );
};

export default ThongBao;
