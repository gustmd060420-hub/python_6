package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class CouponItem {
    @SerializedName("title")
    private String title;
    @SerializedName("description")
    private String description;
    @SerializedName("expires_at")
    private String expiryDate;
    @SerializedName("is_active")
    private boolean isAvailable;

    public CouponItem() {}

    public CouponItem(String title, String description, String expiryDate, boolean isAvailable) {
        this.title = title;
        this.description = description;
        this.expiryDate = expiryDate;
        this.isAvailable = isAvailable;
    }

    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public String getExpiryDate() { return expiryDate; }
    public boolean isAvailable() { return isAvailable; }
}
