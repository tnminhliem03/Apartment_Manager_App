import React, { useEffect, useState } from "react";
import { ActivityIndicator, FlatList, StyleSheet, Text, View, Switch } from "react-native";

import Api, { endpoints } from "../../../Config/Api";

const Phong = ({ navigation }) => {
  const [phong, setPhong] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false); // State để theo dõi việc nạp thêm dữ liệu
  const [nextPage, setNextPage] = useState(null); // State để lưu trữ URL của trang tiếp theo

  useEffect(() => {
    const fetchPhong = async () => {
      try {
        let allPhong = [];
        let nextPageUrl = endpoints.rooms;
        
        // Fetch initial data
        const initialRes = await Api.get(nextPageUrl);
        allPhong = [...allPhong, ...initialRes.data.results];
        setNextPage(initialRes.data.next);
        
        setPhong(allPhong);
        setLoading(false);
      } catch (ex) {
        console.error(ex);
        setLoading(false);
      }
    };
    
    fetchPhong();
  }, []);

  const loadMoreData = async () => {
    if (nextPage && !loadingMore) {
      try {
        setLoadingMore(true);
        const res = await Api.get(nextPage);
        const newPhong = res.data.results;
        setPhong([...phong, ...newPhong]);
        setNextPage(res.data.next);
      } catch (ex) {
        console.error("Error loading more data:", ex);
      } finally {
        setLoadingMore(false);
      }
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.roomContainer}>
      <Text style={styles.roomNumber}>Tên phòng: {item.name}</Text>
      <Text style={styles.roomNumber}>Số phòng: {item.number}</Text>
      <Text style={styles.roomSquare}>Diện tích: {item.square} m²</Text>
      <Switch
        value={item.is_empty}
        style={styles.switch}
        disabled={true} // Prevent user interaction
        trackColor={{ false: "#767577", true: "#81b0ff" }} // Customize the track color
        thumbColor={item.is_empty ? "#34C759" : "#f4f3f4"} // Customize the thumb color when is_empty is true
      />
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Danh sách phòng</Text>
      {loading ? (
        <ActivityIndicator />
      ) : (
        <FlatList
          data={phong}
          renderItem={renderItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.flatlistContent}
          onEndReached={loadMoreData} // Xác định khi người dùng kéo đến cuối danh sách
          onEndReachedThreshold={0.1} // Khoảng cách từ cuối danh sách mà sự kiện onEndReached được gọi (tính bằng phần trăm)
          ListFooterComponent={loadingMore && <ActivityIndicator />} // Hiển thị indicator khi đang nạp thêm dữ liệu
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#f0f0f0",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  flatlistContent: {
    flexGrow: 1,
  },
  roomContainer: {
    backgroundColor: "#fff",
    padding: 15,
    marginBottom: 10,
    borderRadius: 8,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  roomNumber: {
    fontSize: 18,
    fontWeight: "bold",
  },
  roomSquare: {
    fontSize: 16,
    fontWeight: "normal",
  },
  switch: {
    alignSelf: "flex-end",
  },
});

export default Phong;
