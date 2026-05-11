package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class CreditCardItem {
    @SerializedName("card_number")
    private String cardNumber;
    @SerializedName("bank")
    private String cardCompany;
    @SerializedName("color")
    private String bgColorHex;
    @SerializedName("is_default")
    private boolean isPrimary;

    public CreditCardItem() {}

    public CreditCardItem(String cardNumber, String cardCompany, String bgColorHex, boolean isPrimary) {
        this.cardNumber = cardNumber;
        this.cardCompany = cardCompany;
        this.bgColorHex = bgColorHex;
        this.isPrimary = isPrimary;
    }

    public String getCardNumber() { return cardNumber; }
    public String getCardCompany() { return cardCompany; }
    public String getBgColorHex() { return bgColorHex; }
    public boolean isPrimary() { return isPrimary; }
}
