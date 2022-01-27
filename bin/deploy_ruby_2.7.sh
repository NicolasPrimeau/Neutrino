rm -r build/ruby2_7 2> /dev/null
mkdir build/ruby2_7
cp ./src/ruby-2_7.rb build/ruby2_7/lambda_function.rb

rm build/ruby2_7.zip 2> /dev/null
zip -j build/ruby2_7.zip build/ruby2_7/*

aws s3 cp build/ruby2_7.zip s3://np.neutrino.backend/ruby2_7.zip

aws lambda update-function-code \
  --function-name neutrino-ruby-2_7 \
  --s3-bucket np.neutrino.backend \
  --s3-key ruby2_7.zip