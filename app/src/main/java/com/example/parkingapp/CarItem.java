package com.example.parkingapp;

public class CarItem {
    private String carNumber;
    private String carModel;
    private String carColor;
    private String carYear;
    private boolean isPrimary; // 주 차량 여부

    // 생성자 (Constructor)
    public CarItem(String carNumber, String carModel, String carColor, String carYear, boolean isPrimary) {
        this.carNumber = carNumber;
        this.carModel = carModel;
        this.carColor = carColor;
        this.carYear = carYear;
        this.isPrimary = isPrimary;
    }

    // Getter 메서드들
    public String getCarNumber() { return carNumber; }
    public String getCarModel() { return carModel; }
    public String getCarColor() { return carColor; }
    public String getCarYear() { return carYear; }
    public boolean isPrimary() { return isPrimary; }
}