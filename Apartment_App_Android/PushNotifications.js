import { Platform, PermissionsAndroid, request } from "react-native";

export const checkAppPermission = async () => {
    if (Platform.OS === 'android') {
        try {
            const granted = await PermissionsAndroid.check(
                PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
            );
            
            if (!granted) {
                const permissionRequest = await PermissionsAndroid.request(
                                    PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
                );

                if (permissionRequest === PermissionsAndroid.RESULTS.granted) {
                    console.log('Xin quyền thành công!');
                } else {
                    console.log('Tiếp tục xin quyền');
                    await PermissionsAndroid.request(
                        PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
                    );
                }
            } else {
                console.log('Quyền đã được cấp trước đó!');
            }

        } catch(error) {
            await PermissionsAndroid.request(
                PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
            );
        }
    }
};

export const sendNotif = async (title, body) => {
    const content = {
        appId: 22002,
        appToken: 'lB3kiVHaDJJRC4NROiKcd5',
        title: title,
        body: body
    };

    const response = await fetch('https://app.nativenotify.com/api/notification/', {
        method: 'post',
        body: JSON.stringify(content),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    console.log('Thông báo đã được gửi đi!');
};