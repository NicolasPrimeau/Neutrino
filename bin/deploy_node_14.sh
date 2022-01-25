rm -r build/node_14 2> /dev/null
rm build/node_14.zip 2> /dev/null

mkdir build/node_14
cp ./src/node_14.js build/node_14/main.js

zip -j build/node_14.zip build/node_14/*

aws s3 cp build/node_14.zip s3://np.neutrino.backend/node-14.zip

aws lambda update-function-code \
  --function-name neutrino-node-14 \
  --s3-bucket np.neutrino.backend \
  --s3-key node-14.zip