package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class PlateDeleteRequest {
    @SerializedName("user_id")
    private String userId;
    @SerializedName("plate")
    private String plate;

    public PlateDeleteRequest(String userId, String plate) {
        this.userId = userId;
        this.plate = plate;
    }
}
