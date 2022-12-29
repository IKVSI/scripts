#!/bin/bash
ln -s ./7zar.py ~/.local/bin/7zar
ln -s ./7zex.py ~/.local/bin/7zex
cp ./*.desktop ~/.local/share/applications/
cp ./icons/*.png ~/.local/share/icons/
cp ./autostart/* ~/.config/autostart/