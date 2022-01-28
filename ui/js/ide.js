const url = "http://np.neutrino.s3-website.us-east-2.amazonaws.com/";
const apiUrl = "https://o5brsfw8jd.execute-api.us-east-2.amazonaws.com/prod";
const restApiUrl = "https://ckc08f6h01.execute-api.us-east-2.amazonaws.com/api/"
const wsUrl = "wss://dds81j87ij.execute-api.us-east-2.amazonaws.com/api/";
var wait = localStorageGetItem("wait") || false;
var check_timeout = 300;
var lastSource = "";
var syncReady = false;

var participantCount = 0;

var fontSize = 14;

var MonacoVim;
var MonacoEmacs;

var layout;

var sourceEditor;
// var stdinEditor;
var stdoutEditor;
var stderrEditor;

var isEditorDirty = false;
var currentLanguageId;
const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
});
const sessionId = params["sessionId"];

var $selectLanguage;
var $insertTemplateBtn;
var $runBtn;
var $sessionBtn;
var $copySessionBtn;
var $participantCountIcon;

var timeStart;
var timeEnd;

var layoutConfig = {
    settings: {
        showPopoutIcon: false,
        reorderEnabled: true
    },
    dimensions: {
        borderWidth: 3,
        headerHeight: 22
    },
    content: [{
        type: "row",
        content: [{
            type: "component",
            componentName: "source",
            title: "SOURCE",
            isClosable: false,
            componentState: {
                readOnly: false
            },
            width: 60
        },
        {
            type: "column",
            content: [
            /*
            {
                type: "stack",
                height: 0,
                content: [{
                    type: "component",
                    componentName: "stdin",
                    title: "STDIN",
                    isClosable: false,
                    componentState: {
                        readOnly: false
                    }
                }]
            },
            */
            {
                type: "stack",
                content: [{
                        type: "component",
                        componentName: "stdout",
                        title: "STDOUT",
                        isClosable: false,
                        componentState: {
                            readOnly: true
                        }
                    }, {
                        type: "component",
                        componentName: "stderr",
                        title: "STDERR",
                        isClosable: false,
                        componentState: {
                            readOnly: true
                        }
                    }]
            }]
        }]
    }]
};

function encode(str) {
    return btoa(unescape(encodeURIComponent(str || "")));
}

function decode(bytes) {
    var escaped = escape(atob(bytes || ""));
    try {
        return decodeURIComponent(escaped);
    } catch {
        return unescape(escaped);
    }
}

function localStorageSetItem(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (ignorable) {
  }
}

function localStorageGetItem(key) {
  try {
    return localStorage.getItem(key);
  } catch (ignorable) {
    return null;
  }
}

function showError(title, content) {
    $("#site-modal #title").html(title);
    $("#site-modal .content").html(content);
    $("#site-modal").modal("show");
}

function handleError(jqXHR, textStatus, errorThrown) {
    showError(`${jqXHR.statusText} (${jqXHR.status})`, `<pre>${JSON.stringify(jqXHR, null, 4)}</pre>`);
}

function handleRunError(jqXHR, textStatus, errorThrown) {
    handleError(jqXHR, textStatus, errorThrown);
    $runBtn.removeClass("loading");
}

function updateRunOutput(stdout, stderr) {
    stdoutEditor.setValue(stdout);
    stderrEditor.setValue(stderr);

    if (stdout !== "") {
        var dot = document.getElementById("stdout-dot");
        if (!dot.parentElement.classList.contains("lm_active")) {
            dot.hidden = false;
        }
    }
    if (stderr !== "") {
        var dot = document.getElementById("stderr-dot");
        if (!dot.parentElement.classList.contains("lm_active")) {
            dot.hidden = false;
        }
    }
}

function handleResult(data) {
    timeEnd = performance.now();
    console.log("It took " + (timeEnd - timeStart) + " ms to get submission result.");

    updateRunOutput(data.stdout, data.stderr);
    sendRunOutput();
    $runBtn.removeClass("loading");
}

function getIdFromURI() {
  var uri = location.search.substr(1).trim();
  return uri.split("&")[0];
}

function getLanguageId() {
    return parseInt($selectLanguage.val());
}

function run() {
    if (sourceEditor.getValue().trim() === "") {
        showError("Error", "Source code can't be empty!");
        return;
    } else {
        $runBtn.addClass("loading");
    }

    document.getElementById("stdout-dot").hidden = true;
    document.getElementById("stderr-dot").hidden = true;

    stdoutEditor.setValue("");
    stderrEditor.setValue("");

    var sourceValue = sourceEditor.getValue();
    //var stdinValue = stdinEditor.getValue();
    var languageId = getLanguageId();

    var data = {
        source_code: sourceValue,
        language_id: languageId,
        //stdin: stdinValue,
    };

    var sendRequest = function(data) {
        timeStart = performance.now();
        $.ajax({
            url: apiUrl + `/` + languagePaths[languageId],
            type: "POST",
            contentType: "application/json",
            dataType: 'json',
            data: JSON.stringify(data),
            success: function (data) {
                handleResult(data);
            },
            error: handleRunError
        });
    }
    sendRequest(data);
}

function updateURLParameter(url, param, paramVal){
    var newAdditionalURL = "";
    var tempArray = url.split("?");
    var baseURL = tempArray[0];
    var additionalURL = tempArray[1];
    var temp = "";
    if (additionalURL) {
        tempArray = additionalURL.split("&");
        for (var i=0; i<tempArray.length; i++){
            if(tempArray[i].split('=')[0] != param){
                newAdditionalURL += temp + tempArray[i];
                temp = "&";
            }
        }
    }

    var rows_txt = temp + "" + param + "=" + paramVal;
    return baseURL + "?" + newAdditionalURL + rows_txt;
}

function getUuidV4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

function getFunnyName() {
    var sendRequest = function() {
        $.ajax({
            url: restApiUrl + `/session/new`,
            type: "POST",
            contentType: "application/json",
            dataType: 'json',
            success: function (data) {
                setSession(data.name);
            },
            error: handleRunError
        });
    }
    sendRequest();
}

function setSession(sessionName) {
    window.location.href = updateURLParameter(window.location.href, "sessionId", sessionName);
}

function newSession() {
    // setSession(getUuidV4());
    getFunnyName();
}

function changeEditorLanguage() {
    monaco.editor.setModelLanguage(sourceEditor.getModel(), $selectLanguage.find(":selected").attr("mode"));
    currentLanguageId = parseInt($selectLanguage.val());
    $(".lm_title")[0].innerText = "";
}

function insertTemplate() {
    currentLanguageId = parseInt($selectLanguage.val());
    sourceEditor.setValue(sources[currentLanguageId]);
    changeEditorLanguage();
}

function loadRandomLanguage() {
    var values = [];
    for (var i = 0; i < $selectLanguage[0].options.length; ++i) {
        values.push($selectLanguage[0].options[i].value);
    }
    // $selectLanguage.dropdown("set selected", values[Math.floor(Math.random() * $selectLanguage[0].length)]);
    setLanguage(values[0]);
}

function setLanguage(languageId) {
    $selectLanguage.dropdown("set selected", languageId);
    insertTemplate();
}

function resizeEditor(layoutInfo) {


}

function clearSource() {
    sourceEditor.setValue("");
    sendSourceBroadcastMessage(true);
}

function saveSource() {
    sendSaveMessage();
}

function downloadSource() {
    var value = parseInt($selectLanguage.val());
    download(sourceEditor.getValue(), fileNames[value], "text/plain");
}

function editorsUpdateFontSize(fontSize) {
    sourceEditor.updateOptions({fontSize: fontSize});
    // stdinEditor.updateOptions({fontSize: fontSize});
    stdoutEditor.updateOptions({fontSize: fontSize});
    stderrEditor.updateOptions({fontSize: fontSize});
}

function updateScreenElements() {
    var display = window.innerWidth <= 1200 ? "none" : "";
    $(".wide.screen.only").each(function(index) {
        $(this).css("display", display);
    });
}

var ws = null;
if (sessionId) {
    ws = new WebSocket(wsUrl);
    ws.onopen = function() {
        sendRegisterMessage();
        updateParticipantCount(1);
        updateNotification("Connected");
    };
    ws.onmessage = function(message) {
        const event = JSON.parse(message.data);
        if (event.type == "source_update") {
            setLanguage(event.data.language_id);
            if (event.data.full_update) {
                applyUpdate(event.data.source_code);
            } else {
                // Partial update does not work well
                // applyPartialUpdate(event.data.source_code);
                applyUpdate(event.data.source_code);
            }
            syncReady = true;
        } else if (event.type == "source_update_request") {
            sendSourceBroadcastMessage(full_update=true);
        } else if (event.type == "sync_ready") {
            syncReady = true;
        } else if (event.type == "run_output_update") {
            updateRunOutput(event.data.stdout, event.data.stderr);
        } else if (event.type == "new_participant") {
            updateParticipantCount(1);
        } else if (event.type == "participant_drop") {
            updateParticipantCount(-1);
        }
    };
    ws.onclose = function() {
        sendDeRegisterMessage();
        updateParticipantCount(-1);
        updateNotification("Disconnected");
    };
}

function sendTestMessage(message) {
    sendWsMessage({
      "type": "test",
      "data": {
        "message": message
      }
    });
}


function sendRegisterMessage() {
    sendWsMessage({
        "type": "register",
        "data": {}
    })
}


function sendDeRegisterMessage() {
    sendWsMessage({
        "type": "deregister",
        "data": {}
    })
}


function sendSaveMessage() {
    sendWsMessage({
        "type": "save",
        "data": {
            "source_code": sourceEditor.getValue(),
            "language_id": getLanguageId()
        }
    })
}


function sendSourceBroadcastMessage(full_update = false) {
    sendWsMessage({
        "type": "source_broadcast",
        "data": {
            "source_code": sourceEditor.getValue(),
            "full_update": full_update
        }
    });
}

function updateParticipantCount(change) {
    participantCount += change;
    $participantCountIcon.html("<i class=\"user icon\"></i>" + participantCount);
}

function updateNotification(text) {
    $("#notification").fadeIn(1000).text(text).delay(1000).fadeOut(1000);
}

function sendRunOutput() {
    sendWsMessage({
        "type": "run_output",
        "data": {
            "stdout": stdoutEditor.getValue(),
            "stderr": stderrEditor.getValue()
        }
    });
}

function sendWsMessage(event) {
    event["sessionId"] = sessionId;
    if (ws && ws.readyState == 1) {
        ws.send(JSON.stringify(event));
    }
}

function getTimestampS() {
    return Math.floor(Date.now() / 1000);
}


function applyUpdate(sourceCode) {
    const lineNumber = sourceEditor.getPosition().lineNumber - 1;
    const col = sourceEditor.getPosition().column;
    sourceEditor.setValue(sourceCode);
    lastSource = sourceCode;
    sourceEditor.setPosition({lineNumber: lineNumber + 1, column: col});
}

function applyPartialUpdate(sourceCode) {
    const currentTextLines = sourceEditor.getValue().split(/\r?\n/);
    const updateLines = sourceCode.split(/\r?\n/);

    const lineNumber = sourceEditor.getPosition().lineNumber - 1;
    const col = sourceEditor.getPosition().column;

    if (lineNumber > 1 ) {
        updateLines[lineNumber] = currentTextLines[lineNumber];
    }

    const update = updateLines.join("\r\n");
    sourceEditor.setValue(update);
    lastSource = update;

    sourceEditor.setPosition({lineNumber: lineNumber + 1, column: col});
}


if (ws) {
    const SYNC_TIME_MS = 1000;
    const interval = setInterval(function() {
        if (!sourceEditor || !syncReady) {
            return;
        }
        var currentSource = sourceEditor.getValue();
        if (lastSource != currentSource) {
          sendSourceBroadcastMessage();
          lastSource = currentSource;
        }
     }, SYNC_TIME_MS);
}


$(window).resize(function() {
    layout.updateSize();
    updateScreenElements();
});

$(document).ready(function () {
    updateScreenElements();

    $selectLanguage = $("#select-language");
    $selectLanguage.change(function (e) {
        if (!isEditorDirty) {
            insertTemplate();
        } else {
            changeEditorLanguage();
        }
    });

    $insertTemplateBtn = $("#insert-template-btn");
    $insertTemplateBtn.click(function (e) {
        if (isEditorDirty && confirm("Are you sure? Your current changes will be lost.")) {
            insertTemplate();
        }
    });

    $runBtn = $("#run-btn");
    $runBtn.click(function (e) {
        run();
    });

    $sessionBtn = $("#session-btn");
    $sessionBtn.click(function (e) {
        newSession();
    });

    $('#more').dropdown();
    $(".ui.dropdown.site-links").dropdown({action: "hide", on: "hover"});

    if (sessionId != null) {
        $("#participants-count-holder").html(`
            <div id="participant-count" class="ui label">
                <i class="user icon"></i>0
            </div>
        `);
        $participantCountIcon = $("#participant-count");

        if (window.isSecureContext) {
            $("#left-menu").append(`
                <div class="item no-left-padding borderless">
                    <div id="copy-session-btn" class="ui primary labeled icon button">
                        <i class="copy icon"></i>Copy Link
                    </div>
                </div>
            `);
            $copySessionBtn = $("#copy-session-btn");
            $copySessionBtn.click(function (e) {
                // navigator.clipboard.writeText(window.location.href);
                $copySessionBtn.html(`
                    <i class=\"check icon\"></i>
                    Copied
                `);
                setTimeout(function() {
                    $copySessionBtn.html("<i class=\"copy icon\"></i>Copy Link");
                }, 1000);
            });
        }
    }

    $("body").keydown(function (e) {
        var keyCode = e.keyCode || e.which;

        if (keyCode == 120) { // F9 -> run
            e.preventDefault();
            run();
        } else if (keyCode == 113) { //F2 -> New file
            e.preventDefault();
            window.open(url, '_blank').focus();
        } else if (keyCode == 115) { //F4 -> Clear file
            e.preventDefault();
            clearSource();
        } else if (keyCode == 121) { //F10 -> Download file
            e.preventDefault();
            downloadSource();
        } else if (event.ctrlKey && keyCode == 83) { // Ctrl+s
            e.preventDefault();
            sendSaveMessage();
        } else if (event.ctrlKey && keyCode == 107) { // Ctrl++
            e.preventDefault();
            fontSize += 1;
            editorsUpdateFontSize(fontSize);
        } else if (event.ctrlKey && keyCode == 109) { // Ctrl+-
            e.preventDefault();
            fontSize -= 1;
            editorsUpdateFontSize(fontSize);
        }
    });

    require(["vs/editor/editor.main", "monaco-vim", "monaco-emacs"], function (ignorable, MVim, MEmacs) {
        layout = new GoldenLayout(layoutConfig, $("#site-content"));

        MonacoVim = MVim;
        MonacoEmacs = MEmacs;

        layout.registerComponent("source", function (container, state) {
            sourceEditor = monaco.editor.create(container.getElement()[0], {
                automaticLayout: true,
                theme: "vs-dark",
                scrollBeyondLastLine: true,
                readOnly: state.readOnly,
                language: "python",
                minimap: {
                    enabled: false
                }
            });

            sourceEditor.getModel().onDidChangeContent(function (e) {
                currentLanguageId = parseInt($selectLanguage.val());
                isEditorDirty = sourceEditor.getValue() != sources[currentLanguageId];
            });

            sourceEditor.onDidLayoutChange(resizeEditor);

        });
        /*
        layout.registerComponent("stdin", function (container, state) {
            stdinEditor = monaco.editor.create(container.getElement()[0], {
                automaticLayout: true,
                theme: "vs-dark",
                scrollBeyondLastLine: false,
                readOnly: state.readOnly,
                language: "plaintext",
                minimap: {
                    enabled: false
                },

            });
        });
        */

        layout.registerComponent("stdout", function (container, state) {
            stdoutEditor = monaco.editor.create(container.getElement()[0], {
                automaticLayout: true,
                theme: "vs-dark",
                scrollBeyondLastLine: false,
                readOnly: state.readOnly,
                language: "plaintext",
                minimap: {
                    enabled: false
                }
            });

            container.on("tab", function(tab) {
                tab.element.append("<span id=\"stdout-dot\" class=\"dot\" hidden></span>");
                tab.element.on("mousedown", function(e) {
                    e.target.closest(".lm_tab").children[3].hidden = true;
                });
            });
        });

        layout.registerComponent("stderr", function (container, state) {
            stderrEditor = monaco.editor.create(container.getElement()[0], {
                automaticLayout: true,
                theme: "vs-dark",
                scrollBeyondLastLine: false,
                readOnly: state.readOnly,
                language: "plaintext",
                minimap: {
                    enabled: false
                }
            });

            container.on("tab", function(tab) {
                tab.element.append("<span id=\"stderr-dot\" class=\"dot\" hidden></span>");
                tab.element.on("mousedown", function(e) {
                    e.target.closest(".lm_tab").children[3].hidden = true;
                });
            });
        });

        layout.on("initialised", function () {
            // $(".monaco-editor")[0].appendChild($("#editor-status-line")[0]);
            loadRandomLanguage();
            $("#site-navigation").css("border-bottom", "1px solid black");
            sourceEditor.focus();
            editorsUpdateFontSize(fontSize);
        });

        layout.init();
    });
});

const pythonSource = `
print("Hello world")
`;


const javaSource = `
public class Main {
  public static void main() {
    System.out.println("Hello world");
  }
}
`;

const nodeSource = `
console.log("Hello world");
`;

const ruby27Source = `
p "Hello world"
`;

const fileNames = {
    1: "python.py",
    2: "main.java",
    3: "main.js",
    4: "main.rb"
};

const sources = {
    1: pythonSource,
    2: javaSource,
    3: nodeSource,
    4: ruby27Source
};

const languagePaths = {
    1: "neutrino-python-3_8",
    2: "neutrino-java-11",
    3: "neutrino-node-14",
    4: "neutrino-ruby-2_7"
}


