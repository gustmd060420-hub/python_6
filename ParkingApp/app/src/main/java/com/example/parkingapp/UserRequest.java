package com.example.parkingapp;

public class UserRequest {
    String user_id;
    String password;
    String name;

    public UserRequest(String user_id, String password, String name) {
        this.user_id = user_id;
        this.password = password;
        this.name = name;
    }
}