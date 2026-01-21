# MoltenMeta
A flexible software platform integrating a liquid metal property database with predictive modeling capabilities, designed for scalability.

## Before You Begin

### Platform Requirements

* **Windows**: Windows 10 or later
* **macOS**: Supported (tested during development on a MacBook; not exhaustively tested on older macOS versionsd)
* **Linux**: Supported with limitations (see below)

### Linux Display Server Notes

On Linux, this application relies on advanced docking and window interaction features.
Due to long-standing upstream limitations in **Qt-Advanced-Docking-System** (QtADS), **Wayland** sessions currently exhibit unstable behavior.

Known issues under Wayland include:

* Broken or unresponsive dock dragging
* Window freezes when a dock is dragged outside its original container

These issues are **not application-specific bugs**, but stem from incompatibilities between Qt-based advanced docking mechanisms and Wayland’s window management model. The problem has persisted across multiple Qt releases and remains unresolved upstream.

As a result:

* **Running under X11 is strongly recommended on Linux**
* Wayland sessions are considered **unsupported** at this time

The upstream issue is tracked here:
👉 [Qt 6.9.0 + master result in broken windows on Ubuntu 22.04](https://github.com/githubuser0xFFFF/Qt-Advanced-Docking-System/issues/738)

### Recommendation for Linux Users

If you are using a Wayland-based desktop environment, please switch to an X11 session (for example, *“GNOME on Xorg”* at the login screen) before running this application.
Running under Wayland is possible, but stability and correct behavior **cannot be guaranteed**.
