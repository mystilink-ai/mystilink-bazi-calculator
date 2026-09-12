package com.mystilink.bazi;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Invokes the mystilink-bazi CLI and returns JSON stdout.
 */
public final class BaziCalculator {
    private BaziCalculator() {}

    public static String resolveCli() {
        String env = System.getenv("MYSTILINK_BAZI_CLI");
        if (env != null && !env.isBlank()) {
            return env;
        }
        return "mystilink-bazi";
    }

    public static String run(String... args) throws Exception {
        List<String> cmd = new ArrayList<>();
        cmd.add(resolveCli());
        for (String a : args) {
            cmd.add(a);
        }
        ProcessBuilder pb = new ProcessBuilder(cmd);
        pb.redirectErrorStream(false);
        Process proc = pb.start();
        StringBuilder stdout = new StringBuilder();
        StringBuilder stderr = new StringBuilder();
        try (BufferedReader out = new BufferedReader(
                new InputStreamReader(proc.getInputStream(), StandardCharsets.UTF_8));
             BufferedReader err = new BufferedReader(
                new InputStreamReader(proc.getErrorStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = out.readLine()) != null) {
                stdout.append(line).append('\n');
            }
            while ((line = err.readLine()) != null) {
                stderr.append(line).append('\n');
            }
        }
        int code = proc.waitFor();
        if (code != 0) {
            String msg = stderr.length() > 0 ? stderr.toString() : stdout.toString();
            if (msg.isBlank()) {
                msg = "mystilink-bazi exited with code " + code;
            }
            throw new IllegalStateException(msg.trim());
        }
        return stdout.toString();
    }

    public static String calculate(String date, Integer hour, int minute) throws Exception {
        List<String> args = new ArrayList<>();
        args.add("calculate");
        args.add("--date");
        args.add(date);
        if (hour != null) {
            args.add("--hour");
            args.add(String.valueOf(hour));
        }
        args.add("--minute");
        args.add(String.valueOf(minute));
        return run(args.toArray(new String[0]));
    }

    public static String calculate(
            String date,
            Integer hour,
            int minute,
            String timezone,
            Double longitude
    ) throws Exception {
        List<String> args = new ArrayList<>();
        args.add("calculate");
        args.add("--date");
        args.add(date);
        if (hour != null) {
            args.add("--hour");
            args.add(String.valueOf(hour));
        }
        args.add("--minute");
        args.add(String.valueOf(minute));
        if (timezone != null && longitude != null) {
            args.add("--timezone");
            args.add(timezone);
            args.add("--longitude");
            args.add(String.format(Locale.US, "%f", longitude));
        }
        return run(args.toArray(new String[0]));
    }

    public static String dayun(String date, String gender, int count) throws Exception {
        return run("dayun", "--date", date, "--gender", gender, "--count", String.valueOf(count));
    }

    public static String liunian(int year, String dayStem, String pillarsJson) throws Exception {
        List<String> args = new ArrayList<>();
        args.add("liunian");
        args.add("--year");
        args.add(String.valueOf(year));
        if (dayStem != null && !dayStem.isEmpty()) {
            args.add("--day-stem");
            args.add(dayStem);
        }
        if (pillarsJson != null && !pillarsJson.isEmpty()) {
            args.add("--pillars-json");
            args.add(pillarsJson);
        }
        return run(args.toArray(new String[0]));
    }

    public static String version() throws Exception {
        return run("version");
    }
}
