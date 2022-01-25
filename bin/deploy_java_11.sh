#!/bin/bash

rm -r build/java_11 2> /dev/null
rm build/java-11.zip 2> /dev/null

mkdir -p build/java_11
mkdir -p build/java_11/com/neutrino/handlers
mkdir -p build/java_11/lib

cd build/java_11 || exit

cp ../../src/Java11Handler.java com/neutrino/handlers/Handler.java
cp ../../libs/gson/gson-2.8.9.jar ./lib/gson-2.8.9.jar
cp ../../libs/aws-lambda-runtime/aws-lambda-java-core-1.0.0.jar ./lib/aws-lambda-java-core-1.0.0.jar
cp ../../libs/java-runtime-compiler/compiler-2.21ea81.jar ./lib/compiler-2.21ea81.jar

javac -cp lib/gson-2.8.9.jar:lib/aws-lambda-java-core-1.0.0.jar:lib/compiler-2.21ea81.jar \
  com/neutrino/handlers/Handler.java || exit

cat > Manifest.mf << EOF
Manifest-Version: 1.0
Main-Class: Handler
Class-Path: lib/gson-2.8.9.jar lib/aws-lambda-java-core-1.0.0.jar lib/compiler-2.21ea81.jar
EOF

# jar cfm ../neutrino-java-11.jar Manifest.mf com/neutrino/handlers/*.class
zip -r ../java-11.zip ./*

cd ../.. || exit
aws s3 cp ./build/java-11.zip s3://np.neutrino.backend/java-11.zip

aws lambda update-function-code \
  --function-name neutrino-java-11 \
  --s3-bucket np.neutrino.backend \
  --s3-key java-11.zip