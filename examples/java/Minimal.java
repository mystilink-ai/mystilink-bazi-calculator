package com.mystilink.bazi.examples;

import com.mystilink.bazi.BaziCalculator;

public class Minimal {
    public static void main(String[] args) throws Exception {
        String json = BaziCalculator.calculate("1990-05-15", 12, 0);
        System.out.println(json);
    }
}
