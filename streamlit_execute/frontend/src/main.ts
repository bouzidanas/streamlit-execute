import { Streamlit, RenderData } from "streamlit-component-lib"
import { loadPyodide } from "pyodide";

// setup code
const setupCode =`
import sys
import io
sys.stdout = io.StringIO()
`

console.log(window.top)

let component_key = "st_exec:init"

// init Pyodide
async function init() {
  let pyodideReady = await loadPyodide();
  return pyodideReady;
}

let pyodideReadyPromise = init();

// evaluate Python code
async function evaluatePython(id: string, code: string) {
  let pyodide = await pyodideReadyPromise;
  try {
    let output = pyodide.runPython(code)??"";
    let stdout = pyodide.runPython("sys.stdout.getvalue()");
    pyodide.runPython('sys.stdout = io.StringIO()');
    if (id === "__setup__") return;
    if (id === "__init__") {
      Streamlit.setComponentValue({id: id, code: code, status: "success", value: output, stdout: stdout});
    }
    else {
      sendMessageToStreamlitComponent(id, {id: id, code: code, status: "success", value: output, stdout: stdout});
    }
  } catch (err) {
    if (id === "__setup__") return;
    if (id === "__init__") {
      Streamlit.setComponentValue({id: id, code: code, status: "error", value: err, stdout: ""});
    }
    else {
      sendMessageToStreamlitComponent(id, {id: id, code: code, status: "error", value: err, stdout: ""});
    }
  }
}

evaluatePython("__setup__", setupCode);

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event: Event): void {
  // Get the RenderData from the event
  const data = (event as CustomEvent<RenderData>).detail
  component_key = data.args["target_key"];

  // Execute the Python code in data.args["code"]
  evaluatePython("__init__", data.args["code"]);

  // We tell Streamlit to update our frameHeight after each render event, in
  // case it has changed. (This isn't strictly necessary for the example
  // because our height stays fixed, but this is a low-cost function, so
  // there's no harm in doing it redundantly.)
  Streamlit.setFrameHeight()
}

// Send a message to the Streamlit init component
function sendMessageToStreamlitComponent(id: string, data: any) {
  var outData = Object.assign({
    isStreamlitMessage: true,
    type: "streamlit_execute:output",
    id: id,
  }, data);
  window.top?.postMessage(outData, "*");
}

// data is any JSON-serializable value you sent from Python,
// and it's already deserialized for you.
function onDataFromExecRun(event: MessageEvent) {
  if (!event.data.isStreamlitMessage && event.data.type !== "streamlit_execute:run" && event.data["target_key"] !== component_key) return;
  console.log("event.data", event.data)
  evaluatePython(event.data.id, event.data.code);
}

// Hook things up!
window.addEventListener("message", onDataFromExecRun);

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight()
