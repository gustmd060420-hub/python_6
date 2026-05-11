package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class CardAddRequest {
    @SerializedName("user_id")
    private String userId;
    @SerializedName("card_number")
    private String cardNumber;
    @SerializedName("bank")
    private String bank;
    @SerializedName("color")
    private String color;

    public CardAddRequest(String userId, String cardNumber, String bank, String color) {
        this.userId = userId;
        this.cardNumber = cardNumber;
        this.bank = bank;
        this.color = color;
    }
}
