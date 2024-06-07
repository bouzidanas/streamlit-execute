import os
import streamlit.components.v1 as components
import streamlit as st

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

def connect():
    # Since this component is not visual or interactive, we'll hide it from the
    # Streamlit app using some CSS. This has been tested in Firefox, Chrome, and Edge.
    html_css = """
    <style>
    .element-container:has(.elim), .element-container:has(.elim.next) + .element-container, .element-container:has(iframe[title="__init__.streamlit_execute_init"]), .element-container:has(iframe[title="__init__.streamlit_execute_run"]){
        display: none;
    }
    </style>
    <div class='elim next'></div>
    """
    st.markdown(html_css, unsafe_allow_html=True)

    components.html("""
    <script>                
        function sendMessageToRecipient(event) {
            if (event.data.isStreamlitMessage && event.data.type === "streamlit_execute:run"){
                window.parent.document.querySelectorAll('iframe[title="__init__.streamlit_execute_init"]').forEach((iframe) => {
                    iframe.contentWindow.postMessage(event.data, "*");
                });
            }
            else if (event.data.isStreamlitMessage && event.data.type === "streamlit_execute:output"){
                window.parent.document.querySelectorAll('iframe[title="__init__.streamlit_execute_run"]').forEach((iframe) => {
                    iframe.contentWindow.postMessage(event.data, "*");
                });
            }
        }
        window.parent.addEventListener("message", sendMessageToRecipient);
    </script>
    """, height=0)


# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func_init = components.declare_component(
        # We give the component a simple, descriptive name ("streamlit_execute"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "streamlit_execute_init",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:5173",
    )
    _component_func_run = components.declare_component("streamlit_execute_run", url="http://localhost:5174")
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir_init = os.path.join(parent_dir, "frontend/dist")
    build_dir_run = os.path.join(parent_dir, "frontend_m/dist")
    _component_func_init = components.declare_component("streamlit_execute_init", path=build_dir_init)
    _component_func_run = components.declare_component("streamlit_execute_run", path=build_dir_run)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def init(code, key="st_exec:init"):
    """Create a new instance of "init".

    Parameters
    ----------
    code: str
        The code to execute.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    dict
        The code execution result.

    """

    # We add the following to allow css to target the component and hide it from view
    st.markdown("<div class='elim'></div>", unsafe_allow_html=True)
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    component_value = _component_func_init(code=code, key=key, default={"key": "", "status": ""})

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value

def run(code, target_key="st_exec:init", key=None):
    """Create a new instance of "init".

    Parameters
    ----------
    code: str
        The code to execute.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    dict
        The code execution result.

    """

    # We add the following to allow css to target the component and hide it from view
    st.markdown("<div class='elim'></div>", unsafe_allow_html=True)
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    component_value = _component_func_run(code=code, target_key=target_key, key=key, default={"id": "", "code":"", "type":"", "value":"", "stdout":""})

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value

if not _RELEASE:

    test_code = """
a=1+1
a
"""

    st.subheader("Component Test")
    response = init(test_code)
    st.write(response)

    run_response = run("print(a)")
    st.write(run_response)

    new_response = run("b=a*3\nb")
    st.write(new_response)

    third_response = run("b*b + 4")
    st.write(third_response)