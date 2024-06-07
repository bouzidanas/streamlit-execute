import { Streamlit, RenderData } from "streamlit-component-lib"
import {v4 as uuidv4} from 'uuid';

var data: RenderData | null = null;
var uniqueId = uuidv4().slice(0, 8)

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event: Event): void {
  // Get the RenderData from the event
  data = (event as CustomEvent<RenderData>).detail
  
  // First 8 characters of UUIDv4
  uniqueId = uuidv4().slice(0, 8)
  sendMessageToStreamlitComponent(data.args.key + "-" + uniqueId, data.args)

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
    type: "streamlit_execute:run",
    id: id,
  }, data);
  window.top?.postMessage(outData, "*");
}

// data is any JSON-serializable value you sent from Python,
// and it's already deserialized for you.
function onDataFromExecOutput(event: MessageEvent) {
  if (event.data.isStreamlitMessage && event.data.type === "streamlit_execute:output" && event.data.id === data?.args.key + "-" + uniqueId) {
    console.log("event.data final", event.data)
    Streamlit.setComponentValue({code: event.data.code, status: event.data.status, value: event.data.value, stdout: event.data.stdout});
  }
}

// Hook things up!
window.addEventListener("message", onDataFromExecOutput);

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight()
