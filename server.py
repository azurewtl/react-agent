import socket
from typing import cast
from flask import Flask, render_template, request
from waitress import serve
from llama_index.agent import ReActAgent


def _ansi_style(value: str, *styles: str) -> str:
    codes = {
        "bold": 1,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "magenta": 35,
        "cyan": 36,
    }

    for style in styles:
        value = f"\x1b[{codes[style]}m{value}"

    return f"{value}\x1b[0m"


def get_interface_ip(family: socket.AddressFamily) -> str:
    """Get the IP address of an external interface. Used when binding to
    0.0.0.0 or ::1 to show a more useful URL.

    :meta private:
    """
    # arbitrary private address
    host = "fd31:f903:5ab5:1::1" if family == socket.AF_INET6 else "10.253.155.219"

    with socket.socket(family, socket.SOCK_DGRAM) as s:
        try:
            s.connect((host, 58162))
        except OSError:
            return "::1" if family == socket.AF_INET6 else "127.0.0.1"

        return s.getsockname()[0]  # type: ignore


def select_address_family(host: str, port: int) -> socket.AddressFamily:
    """Return ``AF_INET4``, ``AF_INET6``, or ``AF_UNIX`` depending on
    the host and port."""
    if host.startswith("unix://"):
        return socket.AF_UNIX
    elif ":" in host and hasattr(socket, "AF_INET6"):
        return socket.AF_INET6
    return socket.AF_INET


def log_startup(host: str, port: int) -> None:
    """Show information about the address when starting the server."""
    messages: "list[str]" = []

    try:
        af_unix = socket.AF_UNIX
    except AttributeError:
        af_unix = None

    address_family = select_address_family(host, port)

    if address_family == af_unix:
        messages.append(f" * Running on {host}")
    else:
        scheme = "http"
        display_hostname = host

        if display_hostname in {"0.0.0.0", "::"}:
            messages.append(f" * Running on all addresses ({display_hostname})")
            if display_hostname == "0.0.0.0":
                localhost = "127.0.0.1"
                display_hostname = get_interface_ip(socket.AF_INET)
            else:
                localhost = "[::1]"
                display_hostname = get_interface_ip(socket.AF_INET6)

            messages.append(f" * Running on {scheme}://{localhost}:{port}")

        if ":" in display_hostname:
            display_hostname = f"[{display_hostname}]"

        messages.append(f" * Running on {scheme}://{display_hostname}:{port}")

    print("\n".join(messages))


def run(agent: ReActAgent, host: str, port: int):
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            question = request.form.get("question")
            if question is None:
                return render_template("index.html")
            result = agent.query(question)
            response: str = cast(str, result.response)  # type: ignore
            return render_template(
                "index.html",
                result={
                    "response": response.replace("Answer: ", "").replace("Observation: ", "").strip(),
                },
            )
        return render_template("index.html")

    log_startup(host, port)
    print(_ansi_style("Press CTRL+C to quit", "yellow"))
    serve(app, host=host, port=port)
