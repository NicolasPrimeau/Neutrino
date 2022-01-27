require 'json'
require "stringio"


def lambda_handler(event:, context:)
    source_code = event["body"]["source_code"]
    out, err = run_code(source_code)

    {
        statusCode: 200,
        headers: {"Access-Control-Allow-Origin": "*"},
        body: {"stdout": out, "stderr": err}.to_json
    }
end



def run_code(source_code)
    original_stdout = $stdout
    original_stderr = $stderr
    $stdout = StringIO.new
    $stderr = StringIO.new

    eval(source_code)

    return $stdout.string, $stderr.string
ensure
    $stdout = original_stdout
    $stderr = original_stderr
end
