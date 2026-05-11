package com.example.parkingapp;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Query;

public interface ApiService {

    // 회원
    @POST("/signup")
    Call<AuthResponse> signup(@Body UserRequest request);

    @POST("/login")
    Call<AuthResponse> login(@Body UserRequest request);

    @GET("/user/info")
    Call<UserInfoResponse> getUserInfo(@Query("user_id") String userId);

    @POST("/user/delete")
    Call<AuthResponse> deleteUser(@Body UserIdRequest request);

    // 주차
    @GET("/parking/status")
    Call<ParkingStatusResponse> getParkingStatus(@Query("user_id") String userId);

    @POST("/parking/enter")
    Call<AuthResponse> enterParking(@Body UserIdRequest request);

    @POST("/parking/exit")
    Call<AuthResponse> exitParking(@Body UserIdRequest request);

    // 차량
    @GET("/cars")
    Call<CarListResponse> getCars(@Query("user_id") String userId);

    @POST("/cars/add")
    Call<AuthResponse> addCar(@Body CarAddRequest request);

    @POST("/cars/delete")
    Call<AuthResponse> deleteCar(@Body PlateDeleteRequest request);

    // 카드
    @GET("/cards")
    Call<CardListResponse> getCards(@Query("user_id") String userId);

    @POST("/cards/add")
    Call<AuthResponse> addCard(@Body CardAddRequest request);

    @POST("/cards/delete")
    Call<AuthResponse> deleteCard(@Body CardDeleteRequest request);

    // 쿠폰
    @GET("/coupons")
    Call<CouponListResponse> getCoupons(@Query("user_id") String userId);

    @POST("/coupons/add")
    Call<AuthResponse> addCoupon(@Body CouponAddRequest request);

    @POST("/coupons/redeem")
    Call<AuthResponse> redeemCoupon(@Body CouponRedeemRequest request);
}
