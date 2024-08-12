import axios from "axios";

const HOST ="https://tnminhliem03.pythonanywhere.com";

export const endpoints = {
    'rooms' : '/rooms/',
    'residents' : '/residents/',
    'complaints' : '/complaints/',
    'login': '/lk/token/',
    'current-user': '/residents/current/',
    's_questions': '/survey_questions/',
    's_answers': '/survey_answers/',
    'surveys': '/surveys/',
    'receipts' :'/receipts/',
    'packages' :'/packages/',
    'notifications':'/notifications/',
    'security_cards':'/security_cards/',
    'add-sc': '/security_cards/add-sc/',
    'payments': '/payments/',
    'vnpay_links': '/vnpay_links/',
    'links': '/vnpay_links/links/',
    'momo_links': '/momo_links/',
    'momo': '/momo_links/momo/',
    'vnpay_paids': '/vnpay_paids/',
    'momo_paids': '/momo_paids/',
    'create-complaint':'/complaints/create-complaint/',
    'update-profile' :(id) => `/residents/${id}/profile/`,
    'push-notif': '/notifications/push/'
}

export const auThApi = (accessToken)=> axios.create({
        baseURL:HOST,
        headers:{
            Authorization: `Bearer ${accessToken}` 
            
            
        }
        
    })

export default axios.create({
    baseURL : HOST
})