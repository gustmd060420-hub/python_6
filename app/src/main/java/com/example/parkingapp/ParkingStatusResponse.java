package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class ParkingStatusResponse {

    @SerializedName("is_parked")
    private boolean is_parked;

    @SerializedName("location")
    private String location;

    @SerializedName("parked_time")
    private String parked_time;

    @SerializedName("fee")
    private String fee;

    public boolean isParked() { return is_parked; }
    public String getLocation() { return location; }
    public String getParkedTime() { return parked_time; }
    public String getFee() { return fee; }
}