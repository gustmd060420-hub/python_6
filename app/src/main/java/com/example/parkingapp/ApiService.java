package com.example.parkingapp;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Query;

public interface ApiService {
    @POST("/signup")
    Call<AuthResponse> signup(@Body UserRequest request);

    @POST("/login")
    Call<AuthResponse> login(@Body UserRequest request);

    @GET("/parking/status")
    Call<ParkingStatusResponse> getParkingStatus(@Query("user_id") String userId);

    // [추가된 코드] 결제 및 출차 요청
    @POST("/parking/exit")
    Call<AuthResponse> exitParking(@Body UserIdRequest request);
}