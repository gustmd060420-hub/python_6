package com.example.parkingapp; // 본인 패키지명 확인

public class CreditCardItem {
    private String cardNumber;
    private String cardCompany;
    private String bgColorHex; // 카드의 배경색 (예: "#4A6CFF")
    private boolean isPrimary; // 주 카드 여부

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