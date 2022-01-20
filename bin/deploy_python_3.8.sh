rm -r build/python3_8 2> /dev/null
mkdir build/python3_8
cp ./src/python3_8.py build/python3_8

rm build/python3_8.zip 2> /dev/null
zip -j build/python3_8.zip build/python3_8/*

aws s3 cp build/python3_8.zip s3://np.neutrino.backend/python3_8.zip

aws lambda update-function-code \
  --function-name neutrino-python-3_8 \
  --s3-bucket np.neutrino.backend \
  --s3-key python3_8.zip