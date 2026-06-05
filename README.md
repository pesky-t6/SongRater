# Raycaster & Level Designer 🎮

A low-level 3D raycasting engine and interactive 2D level designer built in C++ using SDL3 and OpenGL — inspired by the rendering techniques behind classic games like Wolfenstein 3D and DOOM.

> **Status:** In active development. The raycasting renderer is functional. The level designer tool with custom sprite importing is in progress.

---

## What It Is

This project has two connected parts:

**Raycasting Engine** — a real-time 3D renderer built from scratch using the raycasting technique: casting rays from a 2D map to project walls into a pseudo-3D perspective. No game engine abstractions — just C++, SDL3 for windowing and input, and OpenGL for rendering.

**Level Designer** — an interactive 2D editor where you can import your own sprites and "paint" a level using them, then preview it in the raycasting 3D view. Intended as a practical tool for planning and visualizing game levels.

---

## Why This Project Exists

Most game development happens inside engines like Unity or Unreal. This project is about understanding what happens underneath — how a framebuffer works, how rays are cast and walls are projected, how a rendering loop is structured at the hardware level. Building a renderer from scratch is one of the most direct ways to develop the low-level graphics intuition that modern game engines abstract away.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| C++ | Core language |
| [SDL3](https://wiki.libsdl.org/SDL3/FrontPage) | Window management, input handling, audio |
| OpenGL | Hardware-accelerated rendering |
| CMake | Build system |

---

## Getting Started

### Prerequisites

- A C++17-compatible compiler (MSVC, GCC, or Clang)
- CMake 3.15+
- SDL3 installed (see [SDL3 build instructions](https://wiki.libsdl.org/SDL3/Installation))
- OpenGL drivers (standard on most systems)

### Build

```bash
git clone https://github.com/pesky-t6/Raycaster.git
cd Raycaster
mkdir build && cd build
cmake ..
cmake --build .
```

---

## Roadmap

- [x] Raycasting renderer with SDL3 + OpenGL
- [x] Basic wall projection and player movement
- [ ] Level designer with 2D tile painting
- [ ] Custom sprite importing
- [ ] Live 3D preview of designed level
- [ ] Texture mapping on walls

---

## References

This project was initially built following a raycasting tutorial series, with progressive extensions toward the level designer tool. The rendering architecture and level editor design are my own additions beyond the tutorial scope.

---

## Author

**Angad Sidhu** — [GitHub](https://github.com/pesky-t6) · [Portfolio](https://pesky-t6.github.io/AngadPortfolio.github.io/)
