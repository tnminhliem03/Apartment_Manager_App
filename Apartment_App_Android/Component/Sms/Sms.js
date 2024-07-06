import React, { useState, useEffect } from 'react';
import { Text, View } from 'react-native';
import messaging from '@react-native-firebase/messaging';
import {PermissionsAndroid} from 'react-native';
import { Linking, ActivityIndicator } from 'react-native';
import { NavigationContainer, useNavigation } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';



const Sms = () => {
    useEffect(()=>{
     const requestUserPermission = async () => {
       PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS);
      const authStatus = await messaging().requestPermission();
      const enabled =
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL;
 
      if (enabled) {
        console.log('Authorization status:', authStatus);
        const token = await messaging().getToken();
        console.log('FCM token:', token);
      }
    };
 
    requestUserPermission();
    },[])
    const getToken = async() =>{
        const token = await messaging().getToken()
        console.log("token= ",token)
    }
    useEffect(() => {
        requestUserPermission()
        getToken()

    }, [])
 
   return (
     <NavigationContainer linking={linking} fallback={<ActivityIndicator animating />}>
     <Stack.Navigator initialRouteName='Home'>
     </Stack.Navigator>
   </NavigationContainer>
   );
 }
 
 
 export default Sms;