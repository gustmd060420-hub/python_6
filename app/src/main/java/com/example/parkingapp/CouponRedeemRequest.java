package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class CouponRedeemRequest {
    @SerializedName("user_id") private String userId;
    @SerializedName("coupon_code") private String couponCode;

    public CouponRedeemRequest(String userId, String couponCode) {
        this.userId = userId;
        this.couponCode = couponCode;
    }
}
