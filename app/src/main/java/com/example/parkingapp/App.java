package com.example.parkingapp;

import android.app.Application;
import android.content.SharedPreferences;
import com.naver.maps.map.NaverMapSdk;

public class App extends Application {

    @Override
    public void onCreate() {
        super.onCreate();

        // 앱 완전 종료 또는 업데이트 후 재시작 시 자동 로그아웃
        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        prefs.edit()
                .putBoolean("isLoggedIn", false)
                .remove("userId")
                .apply();

        NaverMapSdk.getInstance(this).setClient(
                new NaverMapSdk.NaverCloudPlatformClient("1kbqd5fxey")
        );
    }
}
