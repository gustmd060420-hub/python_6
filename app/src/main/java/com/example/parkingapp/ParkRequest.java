package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class ParkRequest {
    @SerializedName("user_id")
    private String userId;
    @SerializedName("location")
    private String location;

    public ParkRequest(String userId, String location) {
        this.userId = userId;
        this.location = location;
    }
}
