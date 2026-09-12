# Compile and run (requires mystilink-bazi on PATH):
#   javac -d out ../../bindings/java/src/main/java/com/mystilink/bazi/BaziCalculator.java Minimal.java
#   java -cp out com.mystilink.bazi.examples.Minimal
#
# Note: place Minimal.java under package path or adjust package declaration for your layout.
# From this directory with flat package override:
#   javac -cp ../../bindings/java/src/main/java -d out Minimal.java \
#     ../../bindings/java/src/main/java/com/mystilink/bazi/BaziCalculator.java
#   java -cp out com.mystilink.bazi.examples.Minimal
