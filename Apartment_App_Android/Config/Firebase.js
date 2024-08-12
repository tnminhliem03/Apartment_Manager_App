// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBqNwOrFMSK0mhLqwiGym6hALd34h6dNzk",
  authDomain: "chatapp-371a3.firebaseapp.com",
  databaseURL: "https://chatapp-371a3-default-rtdb.firebaseio.com",
  projectId: "chatapp-371a3",
  storageBucket: "chatapp-371a3.appspot.com",
  messagingSenderId: "312812727108",
  appId: "1:312812727108:web:66ee95a9a46dfb4f850511",
  measurementId: "G-F4E9CLBPZ1"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export const auth = getAuth(app);
export const database = getFirestore(app);