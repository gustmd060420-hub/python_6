package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class UserInfoResponse {
    @SerializedName("user_id")
    private String userId;
    @SerializedName("name")
    private String name;
    public String getUserId() { return userId; }
    public String getName() { return name; }
}
