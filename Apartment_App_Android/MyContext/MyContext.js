import React, { createContext, useReducer } from 'react';
import MyUserReducer from './MyUserReducer';

const MyConText = createContext();

const initialState = {
  user: null,
  token: null,
};

const MyConTextProvider = ({ children }) => {
  const [state, dispatch] = useReducer(MyUserReducer, initialState);

  return (
    <MyConText.Provider value={[state, dispatch]}>
      {children}
    </MyConText.Provider>
  );
};

export { MyConText, MyConTextProvider };
