package com.example.parkingapp;

public class CouponItem {
    private String title;       // 예: 강남역 30분 무료
    private String description; // 예: 강남역 공영주차장
    private String expiryDate;  // 예: 2026.05.31까지
    private boolean isAvailable;// 사용 가능 여부 (true: 사용가능, false: 사용완료)

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