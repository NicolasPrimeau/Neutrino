const fs = require('fs');
const child_process = require('child_process');

exports.handler =  async function(event, context) {
    const data = JSON.parse(event.body);

    var tempFileName = "/tmp/" + Date.now() + '.js';
    fs.writeFileSync(tempFileName, data.source_code);

    var stdout = "";
    var stderr = "";

    try {
        const process = child_process.execFileSync('node', [tempFileName])
        stdout = process.toString();
    } catch(error) {
        stderr = error.toString();
    }

    return {
        statusCode: 200,
        headers: {
            "Access-Control-Allow-Origin": "*"
        },
        body: JSON.stringify({
            "stdout": stdout,
            "stderr": stderr
        })
    }
}