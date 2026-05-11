package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class CardDeleteRequest {
    @SerializedName("user_id")
    private String userId;
    @SerializedName("card_number")
    private String cardNumber;

    public CardDeleteRequest(String userId, String cardNumber) {
        this.userId = userId;
        this.cardNumber = cardNumber;
    }
}
