package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class CarAddRequest {
    @SerializedName("user_id")
    private String userId;
    @SerializedName("plate")
    private String plate;
    @SerializedName("model")
    private String model;
    @SerializedName("color")
    private String color;
    @SerializedName("year")
    private String year;

    public CarAddRequest(String userId, String plate, String model, String color, String year) {
        this.userId = userId;
        this.plate = plate;
        this.model = model;
        this.color = color;
        this.year = year;
    }
}
