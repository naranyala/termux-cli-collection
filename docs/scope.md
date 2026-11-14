# Scope and Design

## Purpose

TCC is a collection of practical, safe, shell-friendly utilities for Termux on Android. It combines Python actions for fast development with C actions for native POSIX/system functionality.

The project is intended for everyday terminal workflows, experimentation, and learning. It is not a replacement for Termux, package management, or standard Unix utilities.

## In scope

- System, environment, storage, battery, file, text, and workflow utilities.
- Unprivileged operation whenever possible.
- Direct commands that work in scripts.
- An interactive launcher for phone-sized screens.
- Optional Termux integrations with clear package requirements.
- Small modules with predictable output and exit codes.

## Out of scope

- Root-only requirements or graphical interfaces.
- Destructive behavior without explicit confirmation.
- Malware, credential theft, or offensive-security automation.
- Unnecessary third-party dependencies.
- A large framework that hides individual utility behavior.

## Action requirements

Every action should have one clear purpose, be safe by default, support the launcher and direct invocation when practical, document dependencies, and remain readable on narrow terminals.
