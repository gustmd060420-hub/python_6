package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class CouponAddRequest {
    @SerializedName("user_id")
    private String userId;
    @SerializedName("title")
    private String title;
    @SerializedName("description")
    private String description;
    @SerializedName("expires_at")
    private String expiresAt;
    @SerializedName("is_active")
    private boolean isActive;

    public CouponAddRequest(String userId, String title, String description, String expiresAt) {
        this.userId = userId;
        this.title = title;
        this.description = description;
        this.expiresAt = expiresAt;
        this.isActive = true;
    }
}
