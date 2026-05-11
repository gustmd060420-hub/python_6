package com.example.parkingapp;

import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class RetrofitClient {

    // =============================================
    // 접속 방식에 따라 아래 BASE_URL 하나만 주석 해제
    // =============================================

    // [에뮬레이터 전용] 10.0.2.2 = 에뮬레이터에서 PC localhost를 가리키는 주소
    // private static final String BASE_URL = "http://10.0.2.2:8000/";

    // [실기기 - 같은 와이파이] cmd → ipconfig → IPv4 주소 확인 후 입력
    private static final String BASE_URL = "http://192.168.219.100:8000/";

    // [실기기 - ngrok] cmd → "ngrok http 8000" 실행 후 표시된 https://xxxx.ngrok-free.app 입력
    // private static final String BASE_URL = "https://xxxx.ngrok-free.app/";

    // =============================================

    private static Retrofit retrofit = null;

    public static ApiService getApiService() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit.create(ApiService.class);
    }

    // BASE_URL 변경 후 호출하면 Retrofit 인스턴스를 초기화합니다
    public static void reset() {
        retrofit = null;
    }
}
